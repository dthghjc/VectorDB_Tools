import gradio as gr
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import os # 导入os用于文件操作
import glob # 用于列出文件
import openai # 用于捕获特定异常
from config.settings import Settings # 直接导入Settings类

# 导入后端函数(假设它们在内部或通过依赖注入处理数据库会话)
from app.schema_manager import create_schema, get_all_schemas, get_schema_by_name, delete_schema_by_name, create_upload_log, get_upload_logs
from app.data_processor import process_uploaded_file, DATA_DIR as PROCESSOR_DATA_DIR
from app.vectorizer import vectorize_jsonl_file, DATA_DIR as VECTORIZER_DATA_DIR
from app.milvus_uploader import upload_jsonl_to_milvus, connect_to_milvus # 导入Milvus函数
from app.database import SessionLocal # 创建操作会话

# 通过实例化Settings在模块级别加载配置
try:
    config = Settings()
except Exception as e:
    print(f"严重错误: 在ui/app_ui.py中加载设置失败: {e}")
    # 如果配置在此失败,UI可能无法正常工作
    # 根据需要的行为提供虚拟值或重新抛出异常
    class DummyConfig:
        milvus_host = "error_loading_config"
        milvus_port = "0"
    config = DummyConfig()

# 确保数据目录相同或处理差异(如果需要)
DATA_DIR = PROCESSOR_DATA_DIR 
if VECTORIZER_DATA_DIR != DATA_DIR:
    print("警告: 处理器和向量化器的数据目录不同!")
    # 决定如何处理,例如使用其中一个,要求一致性等

# --- UI的辅助函数 --- #

def _get_db():
    """UI函数中数据库会话的上下文管理器"""
    return SessionLocal()

def format_fields_for_display(fields_json: Optional[List[Dict[str, Any]]]) -> str:
    """将JSON字段列表格式化为可读的显示字符串"""
    if not fields_json:
        return "未定义字段"
    lines = []
    for field in fields_json:
        details = f"{field.get('name', 'N/A')} ({field.get('type', 'N/A')})"
        if field.get('is_primary'):
            details += " [PK]"
        if field.get('is_vector'):
            details += f" [Vector, Dim={field.get('dim', 'N/A')}]"
        lines.append(details)
    return "\n".join(lines)

def get_schema_names() -> List[str]:
    """获取所有schema的名称用于下拉列表"""
    with _get_db() as db:
        schemas = get_all_schemas(db)
        return sorted([s.name for s in schemas]) # 对名称排序

def refresh_schema_list() -> pd.DataFrame:
    """获取所有schema并将其格式化为Gradio表格的Pandas DataFrame"""
    with _get_db() as db:
        schemas = get_all_schemas(db)
        data = {
            "Name": [s.name for s in schemas],
            "Description": [s.description or "-" for s in schemas],
            "Fields": [format_fields_for_display(s.fields) for s in schemas],
            "Created At": [s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "-" for s in schemas]
        }
        df = pd.DataFrame(data, columns=["Name", "Description", "Fields", "Created At"])
        return df.sort_values(by="Name").reset_index(drop=True)

def list_jsonl_files() -> List[str]:
    """列出DATA_DIR中的.jsonl文件"""
    try:
        jsonl_files = glob.glob(os.path.join(DATA_DIR, "*.jsonl"))
        # 仅返回文件名而不是完整路径用于显示
        return sorted([os.path.basename(f) for f in jsonl_files])
    except Exception as e:
        print(f"列出{DATA_DIR}中的JSONL文件时出错: {e}")
        return []

def get_schema_fields_for_dropdowns(schema_name: Optional[str]) -> tuple[gr.update, gr.update]:
    """获取给定schema名称的文本和向量字段以更新下拉列表"""
    if not schema_name:
        return gr.update(choices=[], value=None), gr.update(choices=[], value=None)
    
    text_fields = []
    vector_fields = []
    try:
        with _get_db() as db:
            schema = get_schema_by_name(db, schema_name)
            if schema and schema.fields:
                for field in schema.fields:
                    field_name = field.get('name')
                    if not field_name: continue
                    
                    if field.get('is_vector'):
                        vector_fields.append(field_name)
                    # 假设可以保存文本的基本类型
                    elif field.get('type') in ['str', 'text', 'varchar']: # 如果需要可以更具体
                         text_fields.append(field_name)
                         
        return gr.update(choices=sorted(text_fields), value=None), gr.update(choices=sorted(vector_fields), value=None)
    except Exception as e:
        print(f"获取schema '{schema_name}'的字段时出错: {e}")
        return gr.update(choices=[], value=None), gr.update(choices=[], value=None)

def refresh_upload_history() -> pd.DataFrame:
     """获取上传日志并格式化以供显示"""
     try:
          with _get_db() as db:
               logs = get_upload_logs(db, limit=200) # 获取最近200条日志
          if not logs:
               return pd.DataFrame(columns=["Time", "Schema", "File", "Records", "Status", "Message"])
          
          data = {
               "Time": [log.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if log.uploaded_at else "-" for log in logs],
               "Schema": [log.schema_name for log in logs],
               "File": [log.uploaded_filename for log in logs],
               "Records": [log.record_count for log in logs],
               "Status": [log.status for log in logs],
               "Message": [log.message or "-" for log in logs]
          }
          return pd.DataFrame(data)
     except Exception as e:
          print(f"刷新上传历史时出错: {e}")
          return pd.DataFrame({"Error": [f"加载历史记录失败: {e}"]})

# --- UI事件处理程序 --- #

def handle_create_schema(name: str, description: Optional[str], fields_json_str: str) -> Tuple[str, pd.DataFrame, gr.update, gr.update]:
    """处理创建新schema的按钮点击"""
    # 预期输出: [status_message_create, schema_table, schema_dropdown_proc, schema_dropdown_vect] (4个项目)
    schema_dropdown_update = gr.update(choices=get_schema_names())
    if not name:
        # 返回4个项目: 状态,schema表格(无更新),下拉列表_proc(更新),下拉列表_vect(更新)
        return "Schema名称不能为空.", gr.update(), schema_dropdown_update, schema_dropdown_update

    # 基本的字段解析(需要健壮的JSON解析和验证!)
    try:
        fields = pd.read_json(fields_json_str, orient='records')
        fields_list = fields.to_dict(orient='records')
    except Exception as e:
        # 返回4个项目: 状态,schema表格(无更新),下拉列表_proc(无更新),下拉列表_vect(无更新)
        return f"解析字段JSON时出错: {e}. 预期格式: '[{{'name': ...}}, ...]'.", gr.update(), gr.update(), gr.update()

    if not fields_list:
         # 返回4个项目: 状态,schema表格(无更新),下拉列表_proc(无更新),下拉列表_vect(无更新)
         return "Schema必须至少有一个字段.", gr.update(), gr.update(), gr.update()

    try:
        with _get_db() as db:
            create_schema(db=db, name=name, description=description, fields=fields_list)
        # 返回4个项目: 状态,schema表格(更新),下拉列表_proc(更新),下拉列表_vect(更新)
        return f"Schema '{name}' 创建成功!", refresh_schema_list(), schema_dropdown_update, schema_dropdown_update
    except ValueError as e:
        # 返回4个项目: 状态,schema表格(更新),下拉列表_proc(无更新),下拉列表_vect(无更新)
        return f"错误: {e}", refresh_schema_list(), gr.update(), gr.update()
    except Exception as e:
        print(f"创建schema时发生意外错误: {e}")
        # 返回4个项目: 状态,schema表格(更新),下拉列表_proc(无更新),下拉列表_vect(无更新)
        return "发生意外错误.", refresh_schema_list(), gr.update(), gr.update()

def handle_delete_schema(schema_name: str) -> Tuple[str, pd.DataFrame, gr.update, gr.update]:
    """处理从列表中删除选定schema"""
    # 预期输出: [status_message_delete, schema_table, schema_dropdown_proc, schema_dropdown_vect] (4个项目)
    schema_dropdown_update = gr.update(choices=get_schema_names())
    refreshed_list = refresh_schema_list() # 提前刷新列表以重用

    if not schema_name:
        # 返回4个项目: 状态,schema表格(无更新),下拉列表_proc(更新),下拉列表_vect(更新)
        return "请输入要删除的schema名称.", gr.update(), schema_dropdown_update, schema_dropdown_update

    # 在实际UI中添加确认步骤
    try:
        with _get_db() as db:
            deleted = delete_schema_by_name(db, schema_name)
            # 已在上面刷新列表
            if deleted:
                # 返回4个项目: 状态,schema表格(更新),下拉列表_proc(更新),下拉列表_vect(更新)
                return f"Schema '{schema_name}' 删除成功.", refreshed_list, schema_dropdown_update, schema_dropdown_update
            else:
                # 返回4个项目: 状态,schema表格(更新),下拉列表_proc(更新),下拉列表_vect(更新)
                return f"未找到Schema '{schema_name}'.", refreshed_list, schema_dropdown_update, schema_dropdown_update
    except ValueError as e:
         # 返回4个项目: 状态,schema表格(更新),下拉列表_proc(无更新),下拉列表_vect(无更新)
         return f"删除schema '{schema_name}'时出错: {e}", refreshed_list, gr.update(), gr.update()
    except Exception as e:
        print(f"删除schema时发生意外错误: {e}")
        # 返回4个项目: 状态,schema表格(更新),下拉列表_proc(无更新),下拉列表_vect(无更新)
        return f"删除'{schema_name}'时发生意外错误.", refreshed_list, gr.update(), gr.update()

# 数据处理处理程序
def handle_process_data(uploaded_file: Optional[Any], selected_schema_name: Optional[str]) -> tuple[str, Optional[str], gr.update]:
    jsonl_dropdown_update = gr.update(choices=list_jsonl_files())
    if uploaded_file is None or not selected_schema_name:
        return "错误: 请上传文件(CSV/JSON)并选择schema.", None, jsonl_dropdown_update

    uploaded_file_path = uploaded_file.name # Gradio文件对象的.name属性为路径
    print(f"收到文件: {uploaded_file_path}, 选择的Schema: {selected_schema_name}")

    try:
        with _get_db() as db:
            schema = get_schema_by_name(db, selected_schema_name)
            if not schema:
                return f"错误: 在数据库中未找到Schema '{selected_schema_name}'.", None, jsonl_dropdown_update
        
        # 调用后端处理函数
        jsonl_output_path = process_uploaded_file(uploaded_file_path, schema)
        
        # 使路径相对于DATA_DIR以保持显示/下载一致性
        # relative_jsonl_path = os.path.relpath(jsonl_output_path, start=DATA_DIR)
        # Gradio文件组件通常在路径可访问时正确处理路径

        return f"文件处理成功. 输出保存到: {jsonl_output_path}", jsonl_output_path, gr.update(choices=list_jsonl_files(), value=os.path.basename(jsonl_output_path))

    except ValueError as e:
        return f"处理错误: {e}", None, jsonl_dropdown_update
    except Exception as e:
        print(f"数据处理过程中发生意外错误: {e}") # 记录完整错误
        # 向用户提供更清晰的错误消息
        return f"处理过程中发生意外错误. 请查看日志了解详情.", None, jsonl_dropdown_update

# 向量化处理程序
def handle_vectorize_data(
    jsonl_filename: Optional[str],
    schema_name: Optional[str],
    text_field: Optional[str],
    vector_field: Optional[str],
    model_type: Optional[str]
) -> tuple[str, Optional[str], gr.update]:
    jsonl_dropdown_update = gr.update(choices=list_jsonl_files())
    if not all([jsonl_filename, schema_name, text_field, vector_field, model_type]):
        return "错误: 请选择JSONL文件、schema、文本字段、向量字段和模型.", None, jsonl_dropdown_update

    jsonl_file_path = os.path.join(DATA_DIR, jsonl_filename) # 构建完整路径
    print(f"开始向量化: {jsonl_filename}, Schema: {schema_name}, 文本: {text_field}, 向量: {vector_field}, 模型: {model_type}")

    try:
        with _get_db() as db:
            schema = get_schema_by_name(db, schema_name)
            if not schema:
                return f"错误: 未找到Schema '{schema_name}'.", None, jsonl_dropdown_update

        # 调用后端向量化函数
        output_vector_path = vectorize_jsonl_file(
            jsonl_file_path=jsonl_file_path,
            schema=schema,
            model_type=model_type,
            text_field_name=text_field,
            vector_field_name=vector_field
        )
        
        # 向量化成功后刷新JSONL文件列表
        output_filename = os.path.basename(output_vector_path)
        return f"向量化成功. 输出保存到: {output_vector_path}", output_vector_path, gr.update(choices=list_jsonl_files(), value=output_filename)

    except FileNotFoundError as e:
         return f"错误: {e}", None, jsonl_dropdown_update
    except ValueError as e:
         return f"向量化错误: {e}", None, jsonl_dropdown_update
    except openai.error.AuthenticationError: # OpenAI密钥问题的特定错误
         return "向量化错误: OpenAI API密钥无效或缺失. 请检查.env配置.", None, jsonl_dropdown_update
    except Exception as e:
        print(f"向量化过程中发生意外错误: {e}") # 记录完整错误
        # 考虑记录回溯: import traceback; traceback.print_exc()
        return f"向量化过程中发生意外错误. 请查看日志.", None, jsonl_dropdown_update

# --- Gradio UI构建 --- #

def create_schema_ui():
    """创建schema管理的Gradio界面块"""
    with gr.Blocks(analytics_enabled=False) as schema_tab_block:
        gr.Markdown("## Schema管理")
        
        with gr.Tabs():
            with gr.TabItem("创建Schema"):
                with gr.Row():
                    with gr.Column(scale=1):
                        schema_name = gr.Textbox(label="Schema名称", placeholder="例如: documents_openai")
                        schema_desc = gr.Textbox(label="描述(可选)", placeholder="带有OpenAI嵌入的文本文档的Schema")
                        # 暂时使用简单的JSON输入 - 需要动态UI构建器!
                        gr.Markdown("将字段定义为JSON列表(例如: `[{\"name\": \"id\", \"type\": \"int\", \"is_primary\": true}, {\"name\": \"text\", \"type\": \"str\"}, {\"name\": \"embedding\", \"type\": \"vector<float>\", \"is_vector\": true, \"dim\": 1536}]`)")
                        schema_fields_json = gr.Textbox(
                            label="字段(JSON列表)",
                            lines=5,
                            placeholder='[{"name": "doc_id", "type": "int", "is_primary": true}, ...]',
                            elem_id="schema-fields-json"
                        )
                        create_button = gr.Button("创建Schema", variant="primary")
                    with gr.Column(scale=2):
                        status_message_create = gr.Textbox(label="状态", interactive=False)

            with gr.TabItem("查看和删除Schema"):
                gr.Markdown("数据库中存储的现有schema.")
                refresh_button = gr.Button("刷新列表")
                schema_table = gr.DataFrame(
                    headers=["名称", "描述", "字段", "创建时间"],
                    datatype=["str", "str", "str", "str"],
                    label="Schema列表",
                    interactive=False # 仅显示
                )
                with gr.Row():
                     delete_name_input = gr.Textbox(label="要删除的Schema名称", placeholder="输入精确名称")
                     delete_button = gr.Button("删除Schema", variant="stop")
                status_message_delete = gr.Textbox(label="状态", interactive=False)

        # --- 移除create_schema_ui中的冗余事件监听器 --- #
        # 实际的监听器稍后在create_ui中定义,那里可以访问组件
        # create_button.click(...)
        # delete_button.click(...)
        # refresh_button.click(...)
        # schema_tab_block.load(...)

    # 仅返回在此函数作用域内定义的组件
    # 从返回元组中移除schema_dropdown_proc, schema_dropdown_vect
    return (schema_tab_block, schema_name, schema_desc, schema_fields_json, 
            create_button, status_message_create, refresh_button, schema_table, 
            delete_name_input, delete_button, status_message_delete)

def create_data_processing_ui():
    # 此函数定义数据处理标签页的UI元素
    with gr.Blocks(analytics_enabled=False) as processing_tab_block:
        gr.Markdown("## 数据处理: CSV/JSON到JSONL")
        with gr.Row():
            with gr.Column(scale=1):
                file_uploader = gr.File(label="上传数据文件(CSV或JSON)", file_types=['.csv', '.json'])
                schema_dropdown = gr.Dropdown(
                    label="选择目标Schema",
                    # choices=get_schema_names(), # 在主UI中设置初始选项
                    interactive=True
                )
                process_button = gr.Button("处理数据", variant="primary")
            with gr.Column(scale=2):
                status_message_process = gr.Textbox(label="状态", interactive=False)
                output_file_display = gr.File(label="生成的JSONL文件", interactive=False)
        
    # 返回事件处理所需的组件
    return (processing_tab_block, file_uploader, schema_dropdown, 
            process_button, status_message_process, output_file_display)

def create_vectorization_ui():
    # 此函数定义向量化标签页的UI元素
    with gr.Blocks(analytics_enabled=False) as vectorization_tab_block:
        gr.Markdown("## 向量化: JSONL到向量")
        with gr.Row():
            with gr.Column(scale=1):
                jsonl_filename = gr.Dropdown(
                    label="选择JSONL文件",
                    choices=list_jsonl_files(),
                    interactive=True
                )
                schema_dropdown = gr.Dropdown(
                    label="选择目标Schema",
                    choices=get_schema_names(),
                    interactive=True
                )
                text_field = gr.Dropdown(
                    label="选择文本字段",
                    choices=[],
                    interactive=True
                )
                vector_field = gr.Dropdown(
                    label="选择向量字段",
                    choices=[],
                    interactive=True
                )
                model_type = gr.Dropdown(
                    label="选择模型类型",
                    choices=["OpenAI", "BGE"],
                    interactive=True
                )
                vectorize_button = gr.Button("向量化数据", variant="primary")
            with gr.Column(scale=2):
                status_message_vectorize = gr.Textbox(label="状态", interactive=False)
                output_file_display = gr.File(label="生成的向量文件", interactive=False)
        
    # 返回事件处理所需的组件
    return (vectorization_tab_block, jsonl_filename, schema_dropdown, text_field, vector_field, model_type, vectorize_button, status_message_vectorize, output_file_display)

def create_milvus_upload_ui():
     with gr.Blocks(analytics_enabled=False) as milvus_tab_block:
          gr.Markdown("## Milvus上传: 插入JSONL数据")
          with gr.Row():
               with gr.Column(scale=1):
                    jsonl_filename = gr.Dropdown(label="选择JSONL文件(带向量)", interactive=True)
                    schema_dropdown = gr.Dropdown(label="选择目标Schema/集合", interactive=True)
                    gr.Markdown("Milvus连接详情")
                    # 使用加载的配置作为默认值
                    milvus_host = gr.Textbox(label="主机", value=config.milvus_host)
                    milvus_port = gr.Textbox(label="端口", value=str(config.milvus_port)) # 确保为Textbox提供字符串
                    upload_button = gr.Button("上传到Milvus", variant="primary")
               with gr.Column(scale=2):
                    status_message_upload = gr.Textbox(label="状态", interactive=False)
     # 需要来自其他标签页的历史表以更新它
     history_table_placeholder = gr.DataFrame(visible=False)
     return (milvus_tab_block, jsonl_filename, schema_dropdown, milvus_host, milvus_port, 
             upload_button, status_message_upload, history_table_placeholder)

def create_ui(): # 如果以后需要,添加config作为参数
    """创建带有所有标签页的主Gradio应用程序UI"""
    with gr.Blocks(title="Milvus向量工具", theme=gr.themes.Default(), analytics_enabled=False) as demo:
        gr.Markdown("# Milvus向量工具")
        
        # --- 实例化UI组件 --- 
        (schema_tab_block, schema_name, schema_desc, schema_fields_json, 
         create_button, status_message_create, refresh_button, schema_table, 
         delete_name_input, delete_button, status_message_delete) = create_schema_ui()
        
        (processing_tab_block, file_uploader, schema_dropdown_proc, 
         process_button, status_message_process, output_file_display) = create_data_processing_ui()

        (vectorization_tab_block, jsonl_filename, schema_dropdown_vect, text_field, vector_field, model_type, vectorize_button, status_message_vectorize, output_file_display) = create_vectorization_ui()

        (milvus_tab_block, jsonl_filename_upload, schema_dropdown_upload, milvus_host, milvus_port, 
         upload_button, status_message_upload, history_table_placeholder) = create_milvus_upload_ui()

        # --- 排列标签页 --- 
        with gr.Tabs():
            with gr.TabItem("Schema管理"):
                # 嵌入预创建的块 - 这可能无法按预期工作
                # 相反,我们在上面定义组件并在这里仅引用它们用于布局
                # 移除render调用,让Gradio处理布局
                # schema_tab_block.render() # 在这里渲染块
                # 尝试直接放置组件(这需要重构)
                # 现在,我们依赖于schema_tab_block被定义,但这个结构有缺陷
                pass # 占位符 - 正确的结构应该在这里定义组件

            with gr.TabItem("数据处理"):
                # 移除render调用
                # processing_tab_block.render() # 在这里渲染块
                pass # 占位符

            with gr.TabItem("向量化"):
                # 移除render调用
                # vectorization_tab_block.render() # 在这里渲染块
                pass # 占位符

            with gr.TabItem("Milvus上传"):
                # 移除render调用
                # milvus_tab_block.render() # 在这里渲染块
                # 我们需要正确定义这个标签页的组件
                gr.Markdown("## Milvus上传")
                with gr.Row():
                    with gr.Column(scale=1):
                        # 重新定义组件或如果全局定义则正确引用它们
                        jsonl_filename_upload_comp = gr.Dropdown(label="选择JSONL文件(带向量)", choices=list_jsonl_files(), interactive=True)
                        schema_dropdown_upload_comp = gr.Dropdown(label="选择目标Schema/集合", choices=get_schema_names(), interactive=True)
                        gr.Markdown("Milvus连接详情")
                        milvus_host_comp = gr.Textbox(label="主机", value=config.milvus_host)
                        milvus_port_comp = gr.Textbox(label="端口", value=str(config.milvus_port))
                        upload_button_comp = gr.Button("上传到Milvus", variant="primary")
                    with gr.Column(scale=2):
                        status_message_upload_comp = gr.Textbox(label="状态", interactive=False)

            with gr.TabItem("上传历史"):
                 gr.Markdown("## 上传历史")
                 refresh_history_button = gr.Button("刷新历史")
                 history_table = gr.DataFrame(label="上传日志", interactive=False)

                 # 绑定刷新按钮
                 refresh_history_button.click(
                     fn=refresh_upload_history,
                     inputs=[],
                     outputs=[history_table]
                 )
                 # 加载初始历史
                 demo.load(fn=refresh_upload_history, inputs=[], outputs=[history_table])


        # --- 定义事件处理程序(在标签页结构外) --- #

        # Schema事件(这些可能需要访问现在可能在标签页内定义的组件)
        # Schema创建按钮
        create_button.click(
            fn=handle_create_schema,
            inputs=[schema_name, schema_desc, schema_fields_json],
            outputs=[status_message_create, schema_table, schema_dropdown_proc, schema_dropdown_vect] 
        )
        
        # Schema删除按钮
        delete_button.click(
            fn=handle_delete_schema,
            inputs=[delete_name_input],
            outputs=[status_message_delete, schema_table, schema_dropdown_proc, schema_dropdown_vect] 
        )

        # Schema刷新按钮(更新表格和下拉列表)
        def refresh_all_schema_components():
            # 返回表格数据和两个下拉列表的更新
            # Returns table data, and updates for the two dropdowns
            return refresh_schema_list(), gr.update(choices=get_schema_names()), gr.update(choices=get_schema_names())

        refresh_button.click(
            fn=refresh_all_schema_components, # Correct function
            inputs=[],
            outputs=[schema_table, schema_dropdown_proc, schema_dropdown_vect] # Update both table and dropdown
        )

        # Data Process Button
        process_button.click(
            fn=handle_process_data,
            inputs=[file_uploader, schema_dropdown_proc],
            outputs=[status_message_process, output_file_display]
        )

        # Vectorize Button
        vectorize_button.click(
            fn=handle_vectorize_data,
            inputs=[jsonl_filename, schema_dropdown_vect, text_field, vector_field, model_type],
            outputs=[status_message_vectorize, output_file_display]
        )

        # Milvus Upload Button (Needs handler and correct component references)
        # Assuming components defined inside the tab:
        # upload_button_comp.click(
        #     fn=handle_upload_to_milvus, # Needs to be created
        #     inputs=[jsonl_filename_upload_comp, schema_dropdown_upload_comp, milvus_host_comp, milvus_port_comp],
        #     outputs=[status_message_upload_comp, history_table] # Update history table too
        # )

        # Initial data loading for schema table and dropdown when app starts
        def load_initial_data():
            initial_list = refresh_schema_list()
            initial_choices = get_schema_names()
            # Update table, proc dropdown, vect dropdown
            return initial_list, gr.update(choices=initial_choices), gr.update(choices=initial_choices)

        demo.load(
            fn=load_initial_data,
            inputs=[],
            outputs=[schema_table, schema_dropdown_proc, schema_dropdown_vect]
        )

    return demo

# Example of running this UI standalone (for testing)
if __name__ == "__main__":
    # Initialize DB if running standalone for testing UI
    from app.database import init_db
    try:
        init_db()
    except Exception as e:
        print(f"Standalone UI DB Init Error: {e}")
        # Decide if UI should launch anyway

    ui = create_ui()
    ui.launch(server_name="0.0.0.0", auth=("test", "test1234")) # Use dummy auth for direct testing 