from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool # Often better for web apps/serverless

from config.settings import load_config

# Load configuration to get database URL
settings = load_config()
DATABASE_URL = settings.database_url

# Create SQLAlchemy engine
# Using NullPool to prevent issues with connection pooling in some environments
# echo=True for debugging SQL queries, remove in production
engine = create_engine(DATABASE_URL, poolclass=NullPool, echo=False)

# Create a sessionmaker
# autocommit=False and autoflush=False are standard practices
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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