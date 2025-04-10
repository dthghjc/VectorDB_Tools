from pymilvus import (connections, utility, Collection, CollectionSchema, FieldSchema, DataType)
import json
import os
from typing import List, Dict, Any, Optional, Tuple
import traceback # For detailed error logging

from .models import SchemaModel, UploadLog # Correct name
from config.settings import Settings # Import Settings class
from .database import SessionLocal # Import SessionLocal for DB operations
from .schema_manager import create_upload_log, get_schema_by_name # Import the logging function and get_schema_by_name
from config.logging_config import get_logger # Import logger

logger = get_logger(__name__) # Get logger for this module

# Load configuration
try:
    settings = Settings()
except Exception as e:
    logger.critical(f"Failed to load settings in milvus_uploader.py: {e}", exc_info=True)
    raise RuntimeError(f"Milvus uploader configuration failed: {e}") from e

# Define data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# Default Milvus connection alias
DEFAULT_ALIAS = "default"

# --- Milvus Connection Management --- #

def connect_to_milvus(alias: str = DEFAULT_ALIAS, host: str = 'localhost', port: int = 19530, **kwargs):
    """Connects to the Milvus server."""
    existing_connections = connections.list_connections()
    if alias in [conn[0] for conn in existing_connections]:
        logger.debug(f"Already connected to Milvus with alias '{alias}'.")
        return True
    
    try:
        logger.info(f"Connecting to Milvus ({alias}) at {host}:{port}...")
        connections.connect(alias=alias, host=host, port=str(port), **kwargs)
        logger.info(f"Milvus connection successful ({alias}).")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Milvus ({alias}) at {host}:{port}: {e}", exc_info=True)
        raise ConnectionError(f"Could not connect to Milvus: {e}") from e

def disconnect_from_milvus(alias: str = DEFAULT_ALIAS):
    """Disconnects from the Milvus server."""
    try:
        if alias in connections.list_connections():
            connections.disconnect(alias)
            logger.info(f"Disconnected from Milvus ({alias}).")
        else:
            logger.debug(f"No active Milvus connection found for alias '{alias}' to disconnect.")
    except Exception as e:
        logger.error(f"Error disconnecting from Milvus ({alias}): {e}", exc_info=True)

# --- Schema Mapping and Collection Management --- #

def map_schema_to_milvus(schema_def: SchemaModel) -> CollectionSchema:
    """Maps the internal schema definition to a Milvus CollectionSchema."""
    logger.info(f"Mapping schema '{schema_def.name}' to Milvus format.")
    milvus_fields = []
    primary_key_count = 0
    vector_field_count = 0

    if not schema_def.fields:
        msg = f"Schema '{schema_def.name}' has no fields defined."
        logger.error(msg)
        raise ValueError(msg)

    for field in schema_def.fields:
        field_name = field.get('name')
        field_type_str = field.get('type')
        is_primary = field.get('is_primary', False)
        is_vector = field.get('is_vector', False)
        dimension = field.get('dim')
        max_length = field.get('max_length', 65535) # Default for VARCHAR

        if not field_name or not field_type_str:
             msg = f"Invalid field definition in schema '{schema_def.name}': {field}"
             logger.error(msg)
             raise ValueError(msg)

        milvus_type = DataType.UNKNOWN
        kwargs = {}

        if is_vector:
            if field_type_str != 'vector<float>': # Enforce type string for clarity
                msg = f"Invalid type '{field_type_str}' for vector field '{field_name}'. Use 'vector<float>'."
                logger.error(msg)
                raise ValueError(msg)
            if not dimension or not isinstance(dimension, int) or dimension <= 0:
                msg = f"Vector field '{field_name}' requires a positive integer dimension ('dim')."
                logger.error(msg)
                raise ValueError(msg)
            milvus_type = DataType.FLOAT_VECTOR
            kwargs['dim'] = dimension
            vector_field_count += 1
        elif field_type_str in ['str', 'string', 'varchar']:
             milvus_type = DataType.VARCHAR
             kwargs['max_length'] = int(max_length)
        elif field_type_str in ['int', 'int64']:
            milvus_type = DataType.INT64
        elif field_type_str in ['float', 'float32']:
            milvus_type = DataType.FLOAT
        elif field_type_str in ['bool', 'boolean']:
             milvus_type = DataType.BOOL
        # Add mappings for DOUBLE, JSON if needed
        else:
            msg = f"Unsupported field type '{field_type_str}' for field '{field_name}'."
            logger.error(msg)
            raise ValueError(msg)

        if is_primary:
             if primary_key_count > 0:
                 msg = f"Schema '{schema_def.name}' defines multiple primary keys. Milvus allows only one."
                 logger.error(msg)
                 raise ValueError(msg)
             if milvus_type not in [DataType.INT64, DataType.VARCHAR]:
                 msg = f"Primary key field '{field_name}' must be INT64 or VARCHAR type."
                 logger.error(msg)
                 raise ValueError(msg)
             kwargs['is_primary'] = True
             # Ensure auto_id is False if this is the primary key
             kwargs['auto_id'] = False 
             primary_key_count += 1
        # else: # auto_id defaults to False, no need to set explicitly
        #      kwargs['is_primary'] = False
             
        milvus_fields.append(FieldSchema(name=field_name, dtype=milvus_type, **kwargs))

    if primary_key_count == 0:
        # Milvus requires a primary key
        # Option 1: Raise error
        msg = f"Schema '{schema_def.name}' must define exactly one primary key field (is_primary=True, type INT64 or VARCHAR)."
        logger.error(msg)
        raise ValueError(msg)
        # Option 2: Add default INT64 PK with auto_id=True
        # print(f"Warning: No primary key defined in schema '{schema_def.name}'. Adding default INT64 'milvus_id' with auto_id=True.")
        # milvus_fields.append(FieldSchema(name="milvus_id", dtype=DataType.INT64, is_primary=True, auto_id=True))
        # primary_field_name = "milvus_id"
        # primary_key_count = 1 # Ensure count is updated
        # else: # Find the explicitly defined primary field name
    primary_field_name = next((f.name for f in milvus_fields if f.is_primary), None)

    if vector_field_count == 0:
         logger.warning(f"Schema '{schema_def.name}' does not contain any vector fields.")

    schema_description = schema_def.description or f"Collection for schema {schema_def.name}"
    logger.info(f"Finished mapping schema '{schema_def.name}'. Primary key: '{primary_field_name}'. Vector fields: {vector_field_count}.")

    # Ensure primary_field is correctly set in CollectionSchema constructor
    return CollectionSchema(fields=milvus_fields, description=schema_description, primary_field=primary_field_name, auto_id=False if primary_key_count > 0 else True) # Set auto_id based on whether PK was found

def get_or_create_collection(schema_def: SchemaModel, connection_alias: str = DEFAULT_ALIAS, **kwargs) -> Collection:
    """Gets a Milvus collection if it exists, otherwise creates it based on the schema."""
    collection_name = schema_def.name # Use schema name as collection name
    
    # Ensure connection exists
    if connection_alias not in connections.list_connections():
        # Attempt to reconnect using default/config settings
        # TODO: Pass host/port from UI or config
        logger.warning(f"No active Milvus connection '{connection_alias}'. Attempting to connect...")
        connect_to_milvus(alias=connection_alias) # Add host/port args
        
    if utility.has_collection(collection_name, using=connection_alias):
        logger.info(f"Collection '{collection_name}' already exists. Fetching...")
        collection = Collection(name=collection_name, using=connection_alias)
        # Optional: Validate existing collection schema against schema_def?
        # print(f"Existing collection schema: {collection.schema}")
        return collection
    else:
        logger.info(f"Collection '{collection_name}' does not exist. Creating...")
        try:
            milvus_schema = map_schema_to_milvus(schema_def)
            logger.debug(f"Mapped Milvus schema for '{collection_name}': {milvus_schema}")
            
            # Add collection creation options like consistency level if needed
            consistency_level = kwargs.get('consistency_level', "Bounded") # e.g., Strong, Bounded, Session, Eventually
            
            collection = Collection(
                name=collection_name,
                schema=milvus_schema,
                using=connection_alias,
                consistency_level=consistency_level
            )
            logger.info(f"Collection '{collection_name}' created successfully with consistency level '{consistency_level}'.")
            
            # --- Create Index After Collection Creation --- 
            # Indexing is crucial for search performance. Define index params based on vector type.
            # This is a basic example; parameters depend heavily on data and use case.
            vector_fields = [f for f in schema_def.fields if f.get('is_vector')]
            if not vector_fields:
                 logger.info(f"No vector fields found in schema '{schema_def.name}', skipping index creation.")
            else:
                for vec_field_def in vector_fields:
                    vec_field_name = vec_field_def['name']
                    logger.info(f"Creating index for vector field '{vec_field_name}' in collection '{collection_name}'...")
                    # Example index: HNSW for float vectors. Adjust params as needed.
                    # Refer to Milvus docs for index types (FLAT, IVF_FLAT, IVF_SQ8, HNSW, etc.)
                    index_params = {
                        "metric_type": "L2", # Or IP (Inner Product) for cosine similarity
                        "index_type": "HNSW",
                        "params": {"M": 16, "efConstruction": 200} # Example params for HNSW
                    }
                    try:
                        collection.create_index(
                            field_name=vec_field_name,
                            index_params=index_params
                        )
                        logger.info(f"Index created successfully for field '{vec_field_name}'.")
                        # Optional: Load collection after index creation if needed for immediate search
                        # print(f"Loading collection '{collection_name}' into memory...")
                        # collection.load()
                        # print("Collection loaded.")
                    except Exception as index_e:
                         logger.error(f"Error creating index for field '{vec_field_name}': {index_e}", exc_info=True)
                         # Decide how to handle: raise error, continue without index? 
                         raise RuntimeError(f"Failed to create index for {vec_field_name}") from index_e
                         
            return collection

        except Exception as e:
            logger.error(f"Failed to create collection '{collection_name}': {e}", exc_info=True)
            traceback.print_exc()
            raise

# --- Data Insertion with Logging --- #

def upload_jsonl_to_milvus(
    schema_name: str, # Use schema name to fetch schema def
    jsonl_file_path: str,
    milvus_host: str = 'localhost',
    milvus_port: int = 19530,
    batch_size: int = 1000,
    connection_alias: str = DEFAULT_ALIAS
) -> Tuple[int, str, Optional[str]]:
    """Orchestrates connecting, getting/creating collection, inserting data, and logging."""
    logger.info(f"Starting Milvus upload process for schema '{schema_name}' from file '{jsonl_file_path}'.")
    total_inserted_count = 0
    log_status = 'Failed'
    log_message = None
    db_session = SessionLocal() # Create a DB session for logging

    try:
        if not os.path.exists(jsonl_file_path):
             logger.error(f"Input JSONL file not found: {jsonl_file_path}")
             raise FileNotFoundError(f"Input JSONL file not found: {jsonl_file_path}")

        # 1. Get Schema Definition from DB
        logger.debug(f"Fetching schema definition for '{schema_name}' from database.")
        schema_def = get_schema_by_name(db_session, schema_name)
        if not schema_def:
            msg = f"Schema '{schema_name}' not found in database."
            logger.error(msg)
            raise ValueError(msg)

        # 2. Connect to Milvus
        connect_to_milvus(alias=connection_alias, host=milvus_host, port=milvus_port)

        # 3. Get or Create Milvus Collection
        collection = get_or_create_collection(schema_def, connection_alias=connection_alias)
        logger.info(f"Using Milvus Collection: '{collection.name}' (Current entities: {collection.num_entities})")
        
        # 4. Insert Data
        total_inserted_count = _insert_data_internal(collection, jsonl_file_path, batch_size)
        log_status = 'Success'
        log_message = f"Successfully inserted {total_inserted_count} records."
        logger.info(log_message)

    except Exception as e:
        logger.error(f"Error during Milvus upload process for schema '{schema_name}': {e}", exc_info=True)
        log_status = 'Failed'
        log_message = str(e)[:1020] # Truncate long error messages for DB log
        traceback.print_exc() # Log full traceback to console/server logs
        # Re-raise the exception so the UI handler knows about the failure
        raise
    
    finally:
        # 5. Log the upload attempt (always, whether success or fail)
        logger.debug("Attempting to log upload result to database.")
        try:
            create_upload_log(
                db=db_session,
                schema_name=schema_name,
                uploaded_filename=os.path.basename(jsonl_file_path),
                record_count=total_inserted_count, # Log inserted count, could also log attempted count
                status=log_status,
                message=log_message,
                # We might need to pass original/processed/vectorized filenames if available
            )
        except Exception as log_e:
             logger.critical(f"Failed to log upload status to database: {log_e}", exc_info=True)
             # Handle this critical error, maybe log to a file as fallback
             
        # 6. Close DB session
        if db_session: # Check if session was created
             logger.debug("Closing database session.")
             db_session.close()
        
        # 7. Disconnect from Milvus (optional, depends on connection strategy)
        # disconnect_from_milvus(connection_alias)

    return total_inserted_count, log_status, log_message

def _insert_data_internal(
    collection: Collection,
    jsonl_file_path: str,
    batch_size: int
) -> int:
    """Internal function to handle reading and batch insertion into Milvus."""
    logger.info(f"Starting data insertion from {jsonl_file_path} into collection '{collection.name}' (batch size: {batch_size}).")
    schema_fields_map = {field.name: field for field in collection.schema.fields}
    primary_field_name = collection.schema.primary_field.name
    auto_id = getattr(collection.schema, 'auto_id', False) # Safer check for auto_id presence
    
    fields_to_extract = list(schema_fields_map.keys())
    if auto_id:
        logger.debug(f"Collection uses auto_id for primary key '{primary_field_name}'. It will not be extracted from input.")
        fields_to_extract.remove(primary_field_name)
         
    batch_data = {field_name: [] for field_name in fields_to_extract} # Use dict of lists for pymilvus >= 2.1
    batch_count = 0
    total_inserted_count = 0
    line_num = 0
    skipped_records = 0

    logger.info(f"Reading '{jsonl_file_path}' and preparing batches...")
    with open(jsonl_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_num += 1
            if not line.strip():
                continue
            
            try:
                record = json.loads(line)
            except json.JSONDecodeError as json_e:
                logger.warning(f"Skipping line {line_num} due to JSON decode error: {json_e}")
                skipped_records += 1
                continue

            # Prepare data for insertion (list for each field)
            try:
                for field_name in fields_to_extract:
                    if field_name not in record:
                        # Handle missing fields - Default based on type? Nullable? Error?
                        # For now, assume schema validation happened before/during vectorization
                        # If field is nullable, maybe insert None, otherwise error.
                        # Let's raise an error for now for missing required fields.
                        raise ValueError(f"Missing required field '{field_name}' in record at line {line_num}.")
                    
                    value = record[field_name]
                    
                    # Basic Type Validation/Coercion (Optional but recommended)
                    milvus_field = schema_fields_map[field_name]
                    if milvus_field.dtype == DataType.VARCHAR and not isinstance(value, str):
                         value = str(value) # Coerce to string
                    elif milvus_field.dtype == DataType.INT64 and not isinstance(value, int):
                         value = int(value) # Coerce to int
                    elif milvus_field.dtype == DataType.FLOAT and not isinstance(value, float):
                         value = float(value) # Coerce to float
                    elif milvus_field.dtype == DataType.BOOL and not isinstance(value, bool):
                         value = bool(value) # Coerce to bool
                    elif milvus_field.dtype == DataType.FLOAT_VECTOR and (not isinstance(value, list) or not all(isinstance(v, (float, int)) for v in value)):
                         # Allow ints in vectors, but ensure it's a list
                         if isinstance(value, list):
                             # Attempt conversion if elements look numeric
                             try:
                                 value = [float(v) for v in value]
                             except (ValueError, TypeError):
                                  raise TypeError(f"Invalid element type in vector for field '{field_name}' at line {line_num}. Expected numbers.")
                         else:
                             raise TypeError(f"Invalid type for vector field '{field_name}' at line {line_num}. Expected list, got {type(value)}.")
                         # Dimension check (optional, Milvus might handle it)
                         if milvus_field.dim != len(value):
                             raise ValueError(f"Vector dimension mismatch for field '{field_name}' at line {line_num}. Expected {milvus_field.dim}, got {len(value)}.")
                         
                    batch_data[field_name].append(value)
                
                batch_count += 1
                
            except (ValueError, TypeError) as validation_e:
                logger.warning(f"Skipping record at line {line_num} due to validation error: {validation_e}")
                skipped_records += 1
                # Reset batch_data if error occurs mid-record? No, just skip append for this record.
                # Need to backtrack appends if we used list-of-lists. Dict of lists is easier.
                continue # Skip this record
            except json.JSONDecodeError as e:
                 logger.warning(f"Skipping record at line {line_num} due to JSON decode error: {e}")
                 continue

            # Insert batch if full
            if batch_count >= batch_size:
                logger.debug(f"Inserting batch of {batch_count} records...")
                try:
                    # Use dict of lists format for insert
                    mutation_result = collection.insert([batch_data[fname] for fname in fields_to_extract])
                    inserted_count = mutation_result.insert_count
                    total_inserted_count += inserted_count
                    logger.debug(f"Inserted {inserted_count} records. Total: {total_inserted_count}")
                    # Reset batch
                    batch_data = {field_name: [] for field_name in fields_to_extract}
                    batch_count = 0
                except Exception as insert_e:
                     logger.error(f"Error inserting batch ending around line {line_num}: {insert_e}", exc_info=True)
                     traceback.print_exc()
                     # Decide how to handle batch errors: skip, retry, raise?
                     raise RuntimeError(f"Failed to insert batch: {insert_e}") from insert_e

    # Insert any remaining records in the last batch
    if batch_count > 0:
        logger.debug(f"Inserting final batch of {batch_count} records...")
        try:
            mutation_result = collection.insert([batch_data[fname] for fname in fields_to_extract])
            inserted_count = mutation_result.insert_count
            total_inserted_count += inserted_count
            logger.debug(f"Inserted {inserted_count} records. Total: {total_inserted_count}")
        except Exception as insert_e:
            logger.error(f"Error inserting final batch: {insert_e}", exc_info=True)
            traceback.print_exc()
            raise RuntimeError(f"Failed to insert final batch: {insert_e}") from insert_e

    logger.info(f"Finished insertion process. Lines processed: {line_num}, Records skipped: {skipped_records}, Records successfully inserted: {total_inserted_count}")
    
    # Optional: Flush collection after all insertions
    logger.info("Flushing collection...")
    try:
        collection.flush()
        logger.info("Collection flushed successfully.")
    except Exception as flush_e:
         logger.error(f"Error flushing collection '{collection.name}': {flush_e}", exc_info=True)
         # Decide if this should be a fatal error
    
    return total_inserted_count

# --- Upload History Model and Logging --- (To be implemented next)

# Need a new SQLAlchemy model (e.g., UploadLog in models.py)
# Need functions to create log entries in schema_manager.py or here 