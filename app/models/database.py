from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool  # 通常在 Web 应用或无服务器环境中更好

from config.settings import Settings  # 导入配置类

# 加载配置以获取数据库 URL
try:
    settings = Settings()
    DATABASE_URL = settings.database_url
except Exception as e:
    print(f"致命错误: 在 database.py 中加载配置失败: {e}")
    # 根据应用程序结构，您可能希望退出或引发异常
    # 目前，将 URL 设置为 None 或一个虚拟值以允许启动
    # 但数据库操作将失败。
    DATABASE_URL = None  # 或引发 SystemExit(f"配置错误: {e}")

# 创建 SQLAlchemy 引擎
# 使用 NullPool 以防止某些环境中的连接池问题
# echo=True 用于调试 SQL 查询，生产环境中应移除
# 处理 DATABASE_URL 可能因配置错误而为 None 的情况
if DATABASE_URL:
    engine = create_engine(DATABASE_URL, poolclass=NullPool, echo=False)
    # 创建 sessionmaker
    # autocommit=False 和 autoflush=False 是标准做法
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None
    print("警告: 由于缺少配置，数据库引擎无法初始化。")

# 声明模型的基类
Base = declarative_base()

def get_db():
    """依赖函数以获取数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """通过创建表来初始化数据库。"""
    if not engine:
        print("数据库引擎未初始化，跳过数据库初始化。")
        return
    try:
        print("正在初始化数据库...")
        # 在调用 create_all 之前导入所有模型
        # 这确保它们被注册到 Base 元数据中
        from . import models  # noqa: F401
        Base.metadata.create_all(bind=engine)
        print("数据库表已创建（如果它们不存在的话）。")
    except Exception as e:
        print(f"初始化数据库时出错: {e}")
        # 决定如何处理初始化错误（例如，退出、记录）
        raise

# 可选: 在导入或直接运行此模块时调用 init_db()
# 在生产环境中自动执行此操作时要谨慎
# init_db()  # 考虑在主应用启动时显式调用此函数