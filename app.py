import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import gradio as gr
from config.settings import Settings # Import Settings class
from app.database import init_db
from ui.app_ui import create_ui
from config.logging_config import setup_logging, get_logger

# 尽可能在其他操作之前设置日志记录
setup_logging()
logger = get_logger(__name__) # 获取当前模块的日志记录器

def main():
    # 加载配置
    try:
        logger.info("Loading configuration using BaseSettings...")
        config = Settings() # Instantiate Settings directly
        logger.info("Configuration loaded successfully.")
        # Optional: Log some non-sensitive config values
        logger.debug(f"Gradio port: {config.gradio_port}, Milvus host: {config.milvus_host}")
    except Exception as e: # Catch potential validation errors from Settings()
        logger.error(f"Failed to load configuration: {e}", exc_info=True)
        # Display error in Gradio if possible, or just exit
        print(f"FATAL: Configuration loading failed: {e}")
        # Optionally use gr.Error if Gradio interface is partially available or needed for error display
        # gr.Error(f"Configuration Error: {e}")
        return # Exit if config fails

    # 初始化数据库
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        gr.Error(f"Database Initialization Error: {e}")
        return

    logger.info("Starting Milvus Vector Tools Gradio UI...")

    # 创建 Gradio UI
    try:
        demo = create_ui() # 如果UI组件需要,可以传入config
        logger.info("Gradio UI created.")
    except Exception as e:
        logger.error(f"Failed to create Gradio UI: {e}", exc_info=True)
        gr.Error(f"UI Creation Error: {e}")
        return

    # 启动带认证的 Gradio 应用
    try:
        auth_tuple = (config.gradio_username, config.gradio_password.get_secret_value())
        logger.info(f"Launching Gradio app with user: {config.gradio_username}")
        # 启用网络访问,允许外部IP连接
        demo.launch(auth=auth_tuple, server_name="0.0.0.0", server_port=config.gradio_port)
    except Exception as e:
         logger.error(f"Failed to launch Gradio app: {e}", exc_info=True)
         # 这里的错误可能很严重,需要打印到stderr
         print(f"FATAL: Failed to launch Gradio: {e}")

if __name__ == "__main__":
    main()