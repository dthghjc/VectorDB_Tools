import gradio as gr
from config.settings import load_config
from app.database import init_db
from ui.app_ui import create_ui
from config.logging_config import setup_logging, get_logger

# Setup logging BEFORE anything else if possible
setup_logging()
logger = get_logger(__name__) # Get logger for this module

def main():
    # Load configuration
    try:
        logger.info("Loading configuration...")
        config = load_config()
        logger.info("Configuration loaded successfully.")
    except ValueError as e:
        logger.error(f"Failed to load configuration: {e}", exc_info=True)
        gr.Error(f"Configuration Error: {e}")
        return

    # Initialize database
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        gr.Error(f"Database Initialization Error: {e}")
        return

    logger.info("Starting Milvus Vector Tools Gradio UI...")

    # Create Gradio UI
    try:
        demo = create_ui() # Pass config if needed by UI components
        logger.info("Gradio UI created.")
    except Exception as e:
        logger.error(f"Failed to create Gradio UI: {e}", exc_info=True)
        gr.Error(f"UI Creation Error: {e}")
        return

    # Launch Gradio app with authentication
    try:
        auth_tuple = (config.gradio_username, config.gradio_password.get_secret_value())
        logger.info(f"Launching Gradio app with user: {config.gradio_username}")
        # Consider adding server_name="0.0.0.0" if needed for network access
        demo.launch(auth=auth_tuple)
    except Exception as e:
         logger.error(f"Failed to launch Gradio app: {e}", exc_info=True)
         # Error here might be critical, maybe print to stderr
         print(f"FATAL: Failed to launch Gradio: {e}")

if __name__ == "__main__":
    main() 