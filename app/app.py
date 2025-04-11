import gradio as gr
import json
import os
from services.schema_persist import save_schema_to_json, get_schema_names

# 默认 schema 存储目录
SCHEMA_DIR = "schemas"

# 处理创建 Schema 的函数
def handle_create_schema(name, desc, fields_json_str):
    if not name.strip():
        return "❌ 请填写 Schema 名称"
    try:
        fields = json.loads(fields_json_str)  # 解析字段 JSON 字符串
    except Exception as e:
        return f"❌ 字段 JSON 解析失败: {e}"

    schema_dict = {
        "description": desc,
        "fields": fields
    }
    save_schema_to_json(schema_dict, os.path.join(SCHEMA_DIR, f"{name}.json"))  # 保存 Schema 到 JSON 文件
    return f"✅ Schema {name} 保存成功"

# 创建 Gradio 界面
with gr.Blocks(title="Milvus_Tools", theme=gr.themes.Default()) as demo:
    gr.Markdown("# 🧠 Milvus-Tools")

    with gr.Tabs():
        # 1. Schema管理
        with gr.TabItem("Schema管理"):
            with gr.Tabs():
                with gr.TabItem("创建Schema"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            schema_name = gr.Textbox(label="Schema名称")  # Schema 名称输入框
                            schema_desc = gr.Textbox(label="描述(可选)")  # Schema 描述输入框

                            gr.Markdown("### 添加字段")

                            new_field_name = gr.Textbox(label="字段名")  # 字段名输入框
                            new_field_type = gr.Dropdown(
                                label="字段类型",
                                choices=[
                                    "BOOL", "INT8", "INT16", "INT32", "INT64", "FLOAT", "DOUBLE",
                                    "FLOAT_VECTOR", "FLOAT16_VECTOR", "SPARSE_FLOAT_VECTOR", "BINARY_VECTOR",
                                    "VARCHAR", "JSON", "ARRAY"
                                ],
                                value="INT64"  # 默认字段类型
                            )
                            with gr.Row():
                                new_field_is_primary = gr.Checkbox(label="是否主键", value=False)  # 是否主键复选框
                                new_field_auto_id = gr.Checkbox(label="主键是否自动生成（AutoID）", value=False, visible=False)  # AutoID键复选框
                            
                            # 动态参数输入区域（根据字段类型切换）
                            new_field_dim = gr.Number(label="向量维度 (FLOAT_VECTOR / FLOAT16_VECTOR / BINARY_VECTOR)", visible=False)  # 向量维度输入框
                            new_field_max_length = gr.Number(label="最大长度 (VARCHAR / ARRAY of VARCHAR)", visible=False)  # 最大长度输入框
                            new_field_max_capacity = gr.Number(label="ARRAY 最大容量", visible=False)  # 数组最大容量输入框
                            new_field_element_type = gr.Dropdown(label="ARRAY 元素类型", choices=["INT64", "VARCHAR"], visible=False)  # 数组元素类型选择框

                            add_field_button = gr.Button("添加字段")  # 添加字段按钮

                            gr.Markdown("字段 JSON:")
                            schema_fields_json = gr.Textbox(lines=6, interactive=False)  # 字段 JSON 显示框
                            create_button = gr.Button("创建Schema", variant="primary")  # 创建 Schema 按钮

                        with gr.Column(scale=2):
                            field_table = gr.DataFrame(
                                headers=["字段名", "类型", "主键", "dim", "max_length"],
                                datatype=["str", "str", "bool", "number", "number"],
                                interactive=False  # 数据表不可交互
                            )
                            status_create = gr.Textbox(label="状态", interactive=False)  # 状态显示框
                            selected_field_dropdown = gr.Dropdown(label="选择字段操作", choices=[], interactive=True)  # 字段操作选择框
                            with gr.Row():
                                move_up_button = gr.Button("↑ 上移")  # 上移按钮
                                move_down_button = gr.Button("↓ 下移")  # 下移按钮
                                delete_button = gr.Button("🗑 删除")  # 删除按钮

                            field_state = gr.State(value=[])  # 字段状态存储

                            # 更新字段可见性的函数
                            def update_field_visibility(field_type):
                                return {
                                    new_field_dim: gr.update(visible=field_type in ["FLOAT_VECTOR", "FLOAT16_VECTOR", "BINARY_VECTOR"]),
                                    new_field_max_length: gr.update(visible=field_type in ["VARCHAR", "ARRAY"]),
                                    new_field_max_capacity: gr.update(visible=(field_type == "ARRAY")),
                                    new_field_element_type: gr.update(visible=(field_type == "ARRAY")),
                                }

                            # 更新自动生成主键复选框的可见性和交互性
                            def update_auto_id_checkbox(field_type, is_primary):
                                if is_primary and field_type == "INT64":
                                    return gr.update(visible=True, interactive=True)  # 满足条件时可见且可交互
                                return gr.update(visible=False, interactive=False)  # 不满足条件时隐藏且不可交互

                            # 添加字段的函数
                            def add_field(name, dtype, is_primary, dim, max_length, max_capacity, element_type, auto_id, current_fields):
                                if any(f["name"] == name for f in current_fields):
                                    return gr.update(), gr.update(value=current_fields), json.dumps(current_fields, indent=2), f"❌ 字段 '{name}' 已存在", gr.update()

                                new_field = {
                                    "name": name,
                                    "type": dtype,
                                    "is_primary": is_primary
                                }
                                row = [name, dtype, is_primary, None, None]
                                if dtype in ["FLOAT_VECTOR", "FLOAT16_VECTOR", "BINARY_VECTOR"] and dim:
                                    new_field["dim"] = int(dim)
                                    row[3] = int(dim)
                                if dtype in ["VARCHAR", "ARRAY"] and max_length:
                                    new_field["max_length"] = int(max_length)
                                    row[4] = int(max_length)
                                if dtype == "ARRAY" and max_capacity:
                                    new_field["max_capacity"] = int(max_capacity)
                                    new_field["element_type"] = element_type

                                if is_primary and auto_id:  # 处理自动生成主键的逻辑
                                    new_field["auto_id"] = True

                                current_fields.append(new_field)  # 将新字段添加到当前字段列表
                                table = [[f["name"], f["type"], f.get("is_primary", False), f.get("dim"), f.get("max_length")] for f in current_fields]
                                return current_fields, table, json.dumps(current_fields, indent=2), "", gr.update(choices=[f["name"] for f in current_fields])

                            # 删除字段的函数
                            def delete_field(name, current_fields):
                                current_fields = [f for f in current_fields if f["name"] != name]
                                table = [[f["name"], f["type"], f.get("is_primary", False), f.get("dim"), f.get("max_length")] for f in current_fields]
                                return current_fields, table, json.dumps(current_fields, indent=2), gr.update(choices=[f["name"] for f in current_fields])

                            # 移动字段的函数
                            def move_field(name, current_fields, direction):
                                index = next((i for i, f in enumerate(current_fields) if f["name"] == name), None)
                                if index is None:
                                    return current_fields, gr.update(), schema_fields_json.value, gr.update()
                                if direction == "up" and index > 0:
                                    current_fields[index], current_fields[index - 1] = current_fields[index - 1], current_fields[index]
                                if direction == "down" and index < len(current_fields) - 1:
                                    current_fields[index], current_fields[index + 1] = current_fields[index + 1], current_fields[index]
                                table = [[f["name"], f["type"], f.get("is_primary", False), f.get("dim"), f.get("max_length")] for f in current_fields]
                                return current_fields, table, json.dumps(current_fields, indent=2), gr.update(choices=[f["name"] for f in current_fields])

                            # 监听字段类型变化，更新相关输入框的可见性
                            new_field_type.change(
                                                update_field_visibility,
                                                inputs=[new_field_type],
                                                outputs=[new_field_dim, new_field_max_length, new_field_max_capacity, new_field_element_type]
                                            )
                            
                            # 绑定按钮点击事件
                            add_field_button.click(add_field, [new_field_name, new_field_type, new_field_is_primary, new_field_dim, new_field_max_length, new_field_max_capacity, new_field_element_type, new_field_auto_id, field_state],
                                                   [field_state, field_table, schema_fields_json, status_create, selected_field_dropdown])
                            delete_button.click(delete_field, [selected_field_dropdown, field_state], [field_state, field_table, schema_fields_json, selected_field_dropdown])
                            move_up_button.click(lambda name, fields: move_field(name, fields, "up"), [selected_field_dropdown, field_state], [field_state, field_table, schema_fields_json, selected_field_dropdown])
                            move_down_button.click(lambda name, fields: move_field(name, fields, "down"), [selected_field_dropdown, field_state], [field_state, field_table, schema_fields_json, selected_field_dropdown])
                            create_button.click(handle_create_schema, [schema_name, schema_desc, schema_fields_json], outputs=[status_create])

                with gr.TabItem("查看和删除Schema"):
                    gr.Markdown("🚧 功能开发中...")

        # 2. 数据处理
        with gr.TabItem("数据处理"):
            gr.Markdown("🚧 功能开发中...")

        # 3. 向量化
        with gr.TabItem("向量化"):
            gr.Markdown("🚧 功能开发中...")

        # 4. Milvus上传
        with gr.TabItem("Milvus上传"):
            gr.Markdown("🚧 功能开发中...")

        # 5. 上传历史
        with gr.TabItem("上传历史"):
            gr.Markdown("🚧 功能开发中...")

# 启动 Gradio 应用
demo.launch(
    server_name="0.0.0.0", 
    server_port=7899,
    debug=True
)