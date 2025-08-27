import os
import time  # 1. 导入 time 模块
# from dotenv import load_dotenv
from sqlalchemy import create_engine, text # 2. 导入 text 用于执行原生SQL
from app.core.config import settings
# load_dotenv()
# --- 数据库配置 ---
# USER = os.getenv("DB_USER")
# PASSWORD = os.getenv("DB_PASSWORD")
# HOST = os.getenv("DB_HOST")
# PORT = os.getenv("DB_PORT")
# DBNAME = os.getenv("DB_NAME")

# DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"
DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

# --- 测试连接 ---
print("Attempting to connect to the database...")

try:
    # --- 方法一：仅测试连接时间 ---
    start_time_connect = time.perf_counter()
    
    connection_only = engine.connect() # 建立连接
    
    end_time_connect = time.perf_counter()
    connection_only.close() # 记得关闭连接
    
    duration_connect = (end_time_connect - start_time_connect) * 1000 # 转换为毫秒
    print(f"✅ Pure connection successful!")
    print(f"   -> Connection time: {duration_connect:.2f} ms\n")


    # --- 方法二：测试连接 + 简单查询（推荐）---
    start_time_roundtrip = time.perf_counter()
    
    with engine.connect() as connection:
        # 执行一个最简单的 "ping" 查询
        connection.execute(text("SELECT 1"))
        
    end_time_roundtrip = time.perf_counter()
    
    duration_roundtrip = (end_time_roundtrip - start_time_roundtrip) * 1000 # 转换为毫秒
    print(f"✅ Connection and simple query successful!")
    print(f"   -> Round-trip time (connect + query): {duration_roundtrip:.2f} ms")

except Exception as e:
    print(f"❌ Failed to connect: {e}")