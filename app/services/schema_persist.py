import os
import json
from pymilvus import CollectionSchema, FieldSchema, DataType

# 支持的字段类型映射表
DATA_TYPE_MAP = {
    "BOOL": DataType.BOOL,
    "INT8": DataType.INT8,
    "INT16": DataType.INT16,
    "INT32": DataType.INT32,
    "INT64": DataType.INT64,
    "FLOAT": DataType.FLOAT,
    "DOUBLE": DataType.DOUBLE,
    "FLOAT_VECTOR": DataType.FLOAT_VECTOR,
    "BINARY_VECTOR": DataType.BINARY_VECTOR,
    "VARCHAR": DataType.VARCHAR,
    "JSON": DataType.JSON,
    "ARRAY": DataType.ARRAY,
    "FLOAT16_VECTOR": DataType.FLOAT16_VECTOR,
    "SPARSE_FLOAT_VECTOR": DataType.SPARSE_FLOAT_VECTOR,
}

def get_schema_names(schema_dir="schemas"):
    """返回所有已保存的 schema 名称（不含 .json 后缀）"""
    if not os.path.exists(schema_dir):
        return []
    return [f.replace(".json", "") for f in os.listdir(schema_dir) if f.endswith(".json")]

def save_schema_to_json(schema_dict: dict, save_path: str):
    """将 schema 字典保存为 JSON 文件"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(schema_dict, f, indent=2, ensure_ascii=False)

def load_schema_dict_from_file(file_path: str) -> dict:
    """从文件中加载 schema 字典"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def dict_to_milvus_schema(schema_dict: dict) -> CollectionSchema:
    """将 JSON 格式 schema 恢复为 pymilvus 的 CollectionSchema 实例"""
    fields = []
    for f in schema_dict["fields"]:
        dtype = DATA_TYPE_MAP[f["type"]]
        kwargs = {
            "name": f["name"],
            "dtype": dtype,
            "is_primary": f.get("is_primary", False),
            "auto_id": f.get("auto_id", False),
            "description": f.get("description", ""),
        }

        # 类型相关参数处理
        if dtype == DataType.FLOAT_VECTOR and "dim" in f:
            kwargs["dim"] = f["dim"]
        if dtype == DataType.FLOAT16_VECTOR and "dim" in f:
            kwargs["dim"] = f["dim"]
        if dtype == DataType.SPARSE_FLOAT_VECTOR:
            pass  # 暂无额外参数
        if dtype == DataType.VARCHAR and "max_length" in f:
            kwargs["max_length"] = f["max_length"]
        if dtype == DataType.ARRAY:
            kwargs["element_type"] = DATA_TYPE_MAP[f["element_type"]]
            kwargs["max_capacity"] = f["max_capacity"]
            if "max_length" in f:
                kwargs["max_length"] = f["max_length"]

        fields.append(FieldSchema(**kwargs))

    return CollectionSchema(
        fields=fields,
        description=schema_dict.get("description", "")
    )

def schema_to_dict(schema: CollectionSchema) -> dict:
    """将 CollectionSchema 转为 JSON 可持久化结构"""
    fields_json = []
    for f in schema.fields:
        f_dict = f.to_dict()
        f_dict["type"] = f_dict["type"].name
        if "element_type" in f_dict:
            f_dict["element_type"] = f_dict["element_type"].name
        fields_json.append(f_dict)

    return {
        "description": schema.description,
        "fields": fields_json
    }
