from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import datetime

from . import models
from .database import get_db
from .models import UploadLog
from config.logging_config import get_logger # Import logger

logger = get_logger(__name__) # Get logger for this module

# --- Data Transfer Objects (DTOs) or Pydantic Models (Optional but recommended) ---
# For type safety and validation, you might define Pydantic models here
# Example:
# class FieldDefinition(BaseModel):
#     name: str
#     type: str # e.g., 'str', 'int', 'float', 'vector<float>'
#     is_primary: bool = False
#     is_vector: bool = False
#     dim: Optional[int] = None

# class SchemaCreate(BaseModel):
#     name: str
#     description: Optional[str] = None
#     fields: List[FieldDefinition]

# --- CRUD Operations ---

def create_schema(db: Session, name: str, description: Optional[str], fields: List[Dict[str, Any]]) -> models.SchemaModel:
    """Creates a new schema in the database after validating fields."""
    logger.info(f"Attempting to create schema: {name}")
    if not name:
        logger.error("Schema creation failed: Name is required.")
        raise ValueError("Schema name is required.")
    if not fields:
        logger.error("Schema creation failed: Fields definition is required.")
        raise ValueError("Schema must have at least one field defined.")
        
    # Validate the fields definition first
    try:
        validate_schema_definition(fields)
        logger.info(f"Schema fields definition for '{name}' validated successfully.")
    except ValueError as validation_error:
        logger.error(f"Schema definition validation failed for '{name}': {validation_error}")
        raise validation_error # Re-raise the specific validation error

    db_schema = models.SchemaModel(
        name=name,
        description=description,
        fields=fields
    )
    db.add(db_schema)
    try:
        db.commit()
        db.refresh(db_schema)
        logger.info(f"Schema '{name}' created successfully (ID: {db_schema.id}).")
        return db_schema
    except IntegrityError as e: # Catches unique constraint violation
         db.rollback()
         logger.error(f"Error creating schema '{name}': Schema name likely already exists. Details: {e}")
         raise ValueError(f"Schema name '{name}' already exists.") from e
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating schema '{name}': {e}", exc_info=True)
        raise ValueError(f"Failed to create schema '{name}'.") from e

def get_schema_by_name(db: Session, name: str) -> Optional[models.SchemaModel]:
    """Retrieves a schema by its unique name."""
    logger.debug(f"Querying for schema with name: {name}")
    schema = db.query(models.SchemaModel).filter(models.SchemaModel.name == name).first()
    if schema:
        logger.debug(f"Schema '{name}' found.")
    else:
        logger.debug(f"Schema '{name}' not found.")
    return schema

def get_all_schemas(db: Session, skip: int = 0, limit: int = 100) -> List[models.SchemaModel]:
    """Retrieves a list of all schemas with pagination."""
    logger.debug(f"Querying for all schemas (limit: {limit}, skip: {skip}).")
    schemas = db.query(models.SchemaModel).order_by(models.SchemaModel.name).offset(skip).limit(limit).all()
    logger.debug(f"Found {len(schemas)} schemas.")
    return schemas

def delete_schema_by_name(db: Session, name: str) -> bool:
    """Deletes a schema by its name. Returns True if deleted, False otherwise."""
    logger.info(f"Attempting to delete schema: {name}")
    db_schema = get_schema_by_name(db, name)
    if db_schema:
        try:
            db.delete(db_schema)
            db.commit()
            logger.info(f"Schema '{name}' deleted successfully.")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting schema '{name}': {e}", exc_info=True)
            # Add more specific error handling if needed (e.g., FK constraints)
            raise ValueError(f"Failed to delete schema '{name}'. Check if it is in use.") from e
    else:
        logger.warning(f"Schema '{name}' not found for deletion.")
        return False

# --- Upload Log Operations --- #

def create_upload_log(
    db: Session,
    schema_name: str,
    uploaded_filename: str,
    record_count: int,
    status: str = 'Success',
    message: Optional[str] = None,
    original_filename: Optional[str] = None,
    processed_filename: Optional[str] = None,
    vectorized_filename: Optional[str] = None
) -> Optional[UploadLog]: # Return Optional since logging failure is possible
    """Creates a new upload log entry in the database."""
    logger.info(f"Creating upload log for file: {uploaded_filename}, schema: {schema_name}, status: {status}")
    log_entry = UploadLog(
        schema_name=schema_name,
        original_filename=original_filename,
        processed_filename=processed_filename,
        vectorized_filename=vectorized_filename,
        uploaded_filename=uploaded_filename,
        record_count=record_count,
        status=status,
        message=message,
    )
    db.add(log_entry)
    try:
        db.commit()
        db.refresh(log_entry)
        logger.info(f"Upload log created successfully (ID: {log_entry.id}).")
        return log_entry
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating upload log for {uploaded_filename}: {e}", exc_info=True)
        return None # Indicate failure

def get_upload_logs(db: Session, limit: int = 100, offset: int = 0) -> List[UploadLog]:
    """Retrieves recent upload logs, ordered by time descending."""
    logger.debug(f"Querying for upload logs (limit: {limit}, offset: {offset}).")
    logs = db.query(UploadLog).order_by(UploadLog.uploaded_at.desc()).offset(offset).limit(limit).all()
    logger.debug(f"Found {len(logs)} upload logs.")
    return logs

# --- Helper/Utility Functions (Example) ---

def validate_schema_definition(fields: List[Dict[str, Any]]):
    """Validates the structure and content of the fields definition."""
    logger.debug(f"Validating schema definition with {len(fields)} fields...")
    if not isinstance(fields, list) or not fields:
        raise ValueError("Fields definition must be a non-empty list.")

    field_names = set()
    primary_key_count = 0
    valid_types = {'str', 'int', 'float', 'bool', 'vector<float>'}
    # Add 'varchar', 'int64', 'float32', 'boolean' as aliases if needed based on Milvus mapping

    for i, field in enumerate(fields):
        if not isinstance(field, dict):
            raise ValueError(f"Field definition at index {i} must be a dictionary.")

        field_name = field.get('name')
        field_type = field.get('type')
        is_primary = field.get('is_primary', False)
        is_vector = field.get('is_vector', False)
        dimension = field.get('dim')

        # Check required keys
        if not field_name or not isinstance(field_name, str):
            raise ValueError(f"Field at index {i}: 'name' is required and must be a string.")
        if not field_type or not isinstance(field_type, str):
            raise ValueError(f"Field '{field_name}': 'type' is required and must be a string.")

        # Check for duplicate names
        if field_name in field_names:
            raise ValueError(f"Duplicate field name found: '{field_name}'. Field names must be unique.")
        field_names.add(field_name)

        # Validate type string
        if field_type not in valid_types:
            raise ValueError(f"Field '{field_name}': Invalid type '{field_type}'. Must be one of: {valid_types}")

        # Validate primary key
        if is_primary:
            if field_type not in ['int', 'str']: # Milvus primary keys must be INT64 or VARCHAR
                 raise ValueError(f"Primary key field '{field_name}': Type must be 'int' or 'str'.")
            primary_key_count += 1

        # Validate vector fields
        if is_vector:
            if field_type != 'vector<float>':
                 raise ValueError(f"Field '{field_name}': Type must be 'vector<float>' if is_vector is true.")
            if not dimension or not isinstance(dimension, int) or dimension <= 0:
                 raise ValueError(f"Vector field '{field_name}': Requires a positive integer 'dim' (dimension)." )
        elif field.get('is_vector') is None and field_type == 'vector<float>':
            # Infer is_vector if type is vector<float> but flag is missing (leniency)
             logger.warning(f"Field '{field_name}': Type is 'vector<float>', implicitly setting is_vector=True.")
             field['is_vector'] = True # Modify dict in-place? Or just validate based on type?
             # Let's just validate based on type for now, assume is_vector must be explicit
             raise ValueError(f"Field '{field_name}': Type is 'vector<float>', but 'is_vector: true' is missing.")
        elif dimension is not None and not is_vector:
             raise ValueError(f"Field '{field_name}': Dimension ('dim') should only be specified for vector fields.")
             
    # Final checks
    if primary_key_count == 0:
         raise ValueError("Schema definition must include exactly one primary key field (set 'is_primary: true').")
    if primary_key_count > 1:
         raise ValueError("Schema definition cannot have more than one primary key field.")

    logger.debug("Schema definition validation passed.")
    # The function modifies the list in place if needed (e.g., inferring is_vector), or just validates.
    # For now, it only validates.
    return True # Indicate successful validation 