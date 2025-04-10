from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool # Often better for web apps/serverless

from config.settings import Settings # Import Settings class

# Load configuration to get database URL by instantiating Settings
try:
    settings = Settings()
    DATABASE_URL = settings.database_url
except Exception as e:
    print(f"CRITICAL: Failed to load settings in database.py: {e}")
    # Depending on the application structure, you might want to exit or raise
    # For now, set URL to None or a dummy value to potentially allow startup
    # but database operations will fail.
    DATABASE_URL = None # Or raise SystemExit(f"Config error: {e}")

# Create SQLAlchemy engine
# Using NullPool to prevent issues with connection pooling in some environments
# echo=True for debugging SQL queries, remove in production
# Handle case where DATABASE_URL might be None due to config error
if DATABASE_URL:
    engine = create_engine(DATABASE_URL, poolclass=NullPool, echo=False)
    # Create a sessionmaker
    # autocommit=False and autoflush=False are standard practices
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None
    print("WARNING: Database engine could not be initialized due to missing configuration.")

# Base class for declarative models
Base = declarative_base()

def get_db():
    """Dependency function to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes the database by creating tables."""
    if not engine:
        print("Database engine not initialized. Skipping DB init.")
        return
    try:
        print("Initializing database...")
        # Import all models here before calling create_all
        # This ensures they are registered with Base metadata
        from . import models # noqa: F401
        Base.metadata.create_all(bind=engine)
        print("Database tables created (if they didn't exist).")
    except Exception as e:
        print(f"Error initializing database: {e}")
        # Decide how to handle initialization errors (e.g., exit, log)
        raise

# Optional: Call init_db() when this module is imported or run directly
# Be cautious doing this automatically in production environments
# init_db() # Consider calling this explicitly, e.g., in main app startup 