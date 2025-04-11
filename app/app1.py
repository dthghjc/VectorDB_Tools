import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import gradio as gr
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import json
import glob
import openai

# 导入配置和数据库模块
from config.settings import Settings
from app.database import init_db, SessionLocal

# 导入后端功能模块
from app.schema_manager import create_schema, get_all_schemas, get_schema_by_name, delete_schema_by_name, create_upload_log, get_upload_logs
from app.data_processor import process_uploaded_file, DATA_DIR as PROCESSOR_DATA_DIR
from app.vectorizer import vectorize_jsonl_file, DATA_DIR as VECTORIZER_DATA_DIR
from app.milvus_uploader import upload_jsonl_to_milvus, connect_to_milvus

# 确保数据目录相同
DATA_DIR = PROCESSOR_DATA_DIR
if VECTORIZER_DATA_DIR != DATA_DIR:
    print("警告: 处理器和向量化器的数据目录不同!")

# 加载配置
try:
    print("加载配置...")
    config = Settings()
    print("配置加载成功")
except Exception as e:
    print(f"致命错误: 配置加载失败: {e}")
    sys.exit(1)

# 初始化数据库
try:
    print("初始化数据库...")
    init_db()
    print("数据库初始化成功")
except Exception as e:
    print(f"致命错误: 数据库初始化失败: {e}")
    sys.exit(1)

# --- UI辅助函数 --- #

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
        return sorted([s.name for s in schemas])

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
                    elif field.get('type') in ['str', 'text', 'varchar']:
                         text_fields.append(field_name)
                         
        return gr.update(choices=sorted(text_fields), value=None), gr.update(choices=sorted(vector_fields), value=None)
    except Exception as e:
        print(f"获取schema '{schema_name}'的字段时出错: {e}")
        return gr.update(choices=[], value=None), gr.update(choices=[], value=None)

def refresh_upload_history() -> pd.DataFrame:
     """获取上传日志并格式化以供显示"""
     try:
          with _get_db() as db:
               logs = get_upload_logs(db, limit=200)
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
    schema_dropdown_update = gr.update(choices=get_schema_names())
    if not name:
        return "Schema名称不能为空.", gr.update(), schema_dropdown_update, schema_dropdown_update

    try:
        fields = pd.read_json(fields_json_str, orient='records')
        fields_list = fields.to_dict(orient='records')
    except Exception as e:
        return f"解析字段JSON时出错: {e}. 预期格式: '[{{'name': ...}}, ...]'.", gr.update(), gr.update(), gr.update()

    if not fields_list:
         return "Schema必须至少有一个字段.", gr.update(), gr.update(), gr.update()

    try:
        with _get_db() as db:
            create_schema(db=db, name=name, description=description, fields=fields_list)
        return f"Schema '{name}' 创建成功!", refresh_schema_list(), schema_dropdown_update, schema_dropdown_update
    except ValueError as e:
        return f"错误: {e}", refresh_schema_list(), gr.update(), gr.update()
    except Exception as e:
        print(f"创建schema时发生意外错误: {e}")
        return "发生意外错误.", refresh_schema_list(), gr.update(), gr.update()

def handle_delete_schema(schema_name: str) -> Tuple[str, pd.DataFrame, gr.update, gr.update]:
    """处理从列表中删除选定schema"""
    schema_dropdown_update = gr.update(choices=get_schema_names())
    refreshed_list = refresh_schema_list()

    if not schema_name:
        return "请输入要删除的schema名称.", gr.update(), schema_dropdown_update, schema_dropdown_update

    try:
        with _get_db() as db:
            deleted = delete_schema_by_name(db, schema_name)
            if deleted:
                return f"Schema '{schema_name}' 删除成功.", refreshed_list, schema_dropdown_update, schema_dropdown_update
            else:
                return f"未找到Schema '{schema_name}'.", refreshed_list, schema_dropdown_update, schema_dropdown_update
    except ValueError as e:
         return f"删除schema '{schema_name}'时出错: {e}", refreshed_list, gr.update(), gr.update()
    except Exception as e:
        print(f"删除schema时发生意外错误: {e}")
        return f"删除'{schema_name}'时发生意外错误.", refreshed_list, gr.update(), gr.update()

def handle_process_data(uploaded_file: Optional[Any], selected_schema_name: Optional[str]) -> tuple[str, Optional[str], gr.update]:
    jsonl_dropdown_update = gr.update(choices=list_jsonl_files())
    if uploaded_file is None or not selected_schema_name:
        return "错误: 请上传文件(CSV/JSON)并选择schema.", None, jsonl_dropdown_update

    uploaded_file_path = uploaded_file.name
    print(f"收到文件: {uploaded_file_path}, 选择的Schema: {selected_schema_name}")

    try:
        with _get_db() as db:
            schema = get_schema_by_name(db, selected_schema_name)
            if not schema:
                return f"错误: 在数据库中未找到Schema '{selected_schema_name}'.", None, jsonl_dropdown_update
        
        jsonl_output_path = process_uploaded_file(uploaded_file_path, schema)
        
        return f"文件处理成功. 输出保存到: {jsonl_output_path}", jsonl_output_path, gr.update(choices=list_jsonl_files(), value=os.path.basename(jsonl_output_path))

    except ValueError as e:
        return f"处理错误: {e}", None, jsonl_dropdown_update
    except Exception as e:
        print(f"数据处理过程中发生意外错误: {e}")
        return f"处理过程中发生意外错误. 请查看日志了解详情.", None, jsonl_dropdown_update

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

    jsonl_file_path = os.path.join(DATA_DIR, jsonl_filename)
    print(f"开始向量化: {jsonl_filename}, Schema: {schema_name}, 文本: {text_field}, 向量: {vector_field}, 模型: {model_type}")

    try:
        with _get_db() as db:
            schema = get_schema_by_name(db, schema_name)
            if not schema:
                return f"错误: 未找到Schema '{schema_name}'.", None, jsonl_dropdown_update

        output_vector_path = vectorize_jsonl_file(
            jsonl_file_path=jsonl_file_path,
            schema=schema,
            model_type=model_type,
            text_field_name=text_field,
            vector_field_name=vector_field
        )
        
        output_filename = os.path.basename(output_vector_path)
        return f"向量化成功. 输出保存到: {output_vector_path}", output_vector_path, gr.update(choices=list_jsonl_files(), value=output_filename)

    except FileNotFoundError as e:
         return f"错误: {e}", None, jsonl_dropdown_update
    except ValueError as e:
         return f"向量化错误: {e}", None, jsonl_dropdown_update
    except openai.error.AuthenticationError:
         return "向量化错误: OpenAI API密钥无效或缺失. 请检查.env配置.", None, jsonl_dropdown_update
    except Exception as e:
        print(f"向量化过程中发生意外错误: {e}")
        return f"向量化过程中发生意外错误. 请查看日志.", None, jsonl_dropdown_update

def handle_upload_to_milvus(
    jsonl_filename: Optional[str],
    schema_name: Optional[str],
    milvus_host: str,
    milvus_port: str
) -> tuple[str, pd.DataFrame]:
    """处理上传到Milvus的按钮点击"""
    if not jsonl_filename or not schema_name:
        return "错误: 请选择JSONL文件和目标Schema.", refresh_upload_history()
    
    jsonl_file_path = os.path.join(DATA_DIR, jsonl_filename)
    
    try:
        # 转换端口为整数
        milvus_port_int = int(milvus_port)
        
        # 执行上传
        print(f"开始上传到Milvus: 文件={jsonl_filename}, Schema={schema_name}, 主机={milvus_host}, 端口={milvus_port_int}")
        total_inserted, status, message = upload_jsonl_to_milvus(
            schema_name=schema_name,
            jsonl_file_path=jsonl_file_path,
            milvus_host=milvus_host,
            milvus_port=milvus_port_int
        )
        
        if status == 'Success':
            return f"成功上传到Milvus! 共插入 {total_inserted} 条记录。", refresh_upload_history()
        else:
            return f"上传到Milvus失败: {message}", refresh_upload_history()
            
    except ValueError as e:
        print(f"Milvus上传值错误: {e}")
        return f"上传错误: {e}", refresh_upload_history()
    except ConnectionError as e:
        print(f"Milvus连接错误: {e}")
        return f"连接到Milvus失败: {e}", refresh_upload_history()
    except Exception as e:
        print(f"Milvus上传意外错误: {e}", exc_info=True)
        return f"上传过程中发生错误: {e}", refresh_upload_history()

# --- Gradio UI构建 --- #

# 构建UI并创建demo对象(在模块级别定义以支持热重载)
print("构建Milvus向量工具Gradio UI...")
with gr.Blocks(title="Milvus向量工具", theme=gr.themes.Default()) as demo:
    gr.Markdown("# Milvus向量工具")
    
    with gr.Tabs():
        # --- Schema管理标签页 --- #
        with gr.TabItem("Schema管理"):
            with gr.Tabs():
                with gr.TabItem("创建Schema"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            schema_name = gr.Textbox(label="Schema名称", placeholder="例如: documents_openai")
                            schema_desc = gr.Textbox(label="描述(可选)", placeholder="带有OpenAI嵌入的文本文档的Schema")
                            gr.Markdown("将字段定义为JSON列表(例如: `[{\"name\": \"id\", \"type\": \"int\", \"is_primary\": true}, {\"name\": \"text\", \"type\": \"str\"}, {\"name\": \"embedding\", \"type\": \"vector<float>\", \"is_vector\": true, \"dim\": 1536}]`)")
                            schema_fields_json = gr.Textbox(
                                label="字段(JSON列表)",
                                lines=5,
                                placeholder='[{"name": "doc_id", "type": "int", "is_primary": true}, ...]'
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
                        interactive=False
                    )
                    with gr.Row():
                         delete_name_input = gr.Textbox(label="要删除的Schema名称", placeholder="输入精确名称")
                         delete_button = gr.Button("删除Schema", variant="stop")
                    status_message_delete = gr.Textbox(label="状态", interactive=False)

        # --- 数据处理标签页 --- #
        with gr.TabItem("数据处理"):
            gr.Markdown("## 数据处理: CSV/JSON到JSONL")
            with gr.Row():
                with gr.Column(scale=1):
                    file_uploader = gr.File(label="上传数据文件(CSV或JSON)", file_types=['.csv', '.json'])
                    schema_dropdown_proc = gr.Dropdown(
                        label="选择目标Schema",
                        choices=get_schema_names(),
                        interactive=True
                    )
                    process_button = gr.Button("处理数据", variant="primary")
                with gr.Column(scale=2):
                    status_message_process = gr.Textbox(label="状态", interactive=False)
                    output_file_process = gr.File(label="生成的JSONL文件", interactive=False)

        # --- 向量化标签页 --- #
        with gr.TabItem("向量化"):
            gr.Markdown("## 向量化: JSONL到向量")
            with gr.Row():
                with gr.Column(scale=1):
                    jsonl_filename_vect = gr.Dropdown(
                        label="选择JSONL文件",
                        choices=list_jsonl_files(),
                        interactive=True
                    )
                    schema_dropdown_vect = gr.Dropdown(
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
                    output_file_vectorize = gr.File(label="生成的向量文件", interactive=False)

        # --- Milvus上传标签页 --- #
        with gr.TabItem("Milvus上传"):
            gr.Markdown("## Milvus上传: 插入JSONL数据")
            with gr.Row():
                with gr.Column(scale=1):
                    jsonl_filename_upload = gr.Dropdown(
                        label="选择JSONL文件(带向量)",
                        choices=list_jsonl_files(),
                        interactive=True
                    )
                    schema_dropdown_upload = gr.Dropdown(
                        label="选择目标Schema/集合",
                        choices=get_schema_names(),
                        interactive=True
                    )
                    gr.Markdown("Milvus连接详情")
                    milvus_host = gr.Textbox(label="主机", value=config.milvus_host)
                    milvus_port = gr.Textbox(label="端口", value=str(config.milvus_port))
                    upload_button = gr.Button("上传到Milvus", variant="primary")
                with gr.Column(scale=2):
                    status_message_upload = gr.Textbox(label="状态", interactive=False)

        # --- 上传历史标签页 --- #
        with gr.TabItem("上传历史"):
             gr.Markdown("## 上传历史")
             refresh_history_button = gr.Button("刷新历史")
             history_table = gr.DataFrame(label="上传日志", interactive=False)

    # --- 事件处理绑定 --- #
    
    # Schema管理事件
    create_button.click(
        fn=handle_create_schema,
        inputs=[schema_name, schema_desc, schema_fields_json],
        outputs=[status_message_create, schema_table, schema_dropdown_proc, schema_dropdown_vect]
    )
    
    delete_button.click(
        fn=handle_delete_schema,
        inputs=[delete_name_input],
        outputs=[status_message_delete, schema_table, schema_dropdown_proc, schema_dropdown_vect]
    )
    
    refresh_button.click(
        fn=refresh_schema_list,
        inputs=[],
        outputs=[schema_table]
    )
    
    # 数据处理事件
    process_button.click(
        fn=handle_process_data,
        inputs=[file_uploader, schema_dropdown_proc],
        outputs=[status_message_process, output_file_process, jsonl_filename_vect]
    )
    
    # 向量化处理事件
    schema_dropdown_vect.change(
        fn=get_schema_fields_for_dropdowns,
        inputs=[schema_dropdown_vect],
        outputs=[text_field, vector_field]
    )
    
    vectorize_button.click(
        fn=handle_vectorize_data,
        inputs=[jsonl_filename_vect, schema_dropdown_vect, text_field, vector_field, model_type],
        outputs=[status_message_vectorize, output_file_vectorize, jsonl_filename_upload]
    )
    
    # Milvus上传事件
    upload_button.click(
        fn=handle_upload_to_milvus,
        inputs=[jsonl_filename_upload, schema_dropdown_upload, milvus_host, milvus_port],
        outputs=[status_message_upload, history_table]
    )
    
    # 上传历史事件
    refresh_history_button.click(
        fn=refresh_upload_history,
        inputs=[],
        outputs=[history_table]
    )
    
    # 初始数据加载
    demo.load(
        fn=refresh_schema_list,
        inputs=[],
        outputs=[schema_table]
    )
    
    demo.load(
        fn=refresh_upload_history,
        inputs=[],
        outputs=[history_table]
    )


print("启动Milvus向量数据库工具Gradio UI...")

demo.launch(
    server_name="0.0.0.0", 
    server_port=config.gradio_port,
    debug=True
)