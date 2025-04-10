import pandas as pd
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from .models import SchemaModel
from config.logging_config import get_logger # Import logger

logger = get_logger(__name__) # Get logger for this module

# Define data directory relative to this file's location
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
if not os.path.exists(DATA_DIR):
    logger.info(f"Creating data directory: {DATA_DIR}")
    os.makedirs(DATA_DIR)

def load_data_from_file(file_path: str) -> Optional[pd.DataFrame]:
    """Loads data from CSV or JSON file into a pandas DataFrame."""
    logger.info(f"Attempting to load data from: {file_path}")
    try:
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} rows from CSV file.")
            return df
        elif file_path.lower().endswith('.json'):
            # Assuming JSON contains a list of records
            df = pd.read_json(file_path, orient='records')
            logger.info(f"Loaded {len(df)} rows from JSON file.")
            return df
        else:
            logger.error(f"Unsupported file format for {file_path}. Please use CSV or JSON.")
            raise ValueError("Unsupported file format. Please use CSV or JSON.")
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}", exc_info=True)
        raise

def validate_and_transform_data(df: pd.DataFrame, schema: SchemaModel) -> List[Dict[str, Any]]:
    """Validates DataFrame against schema and transforms it into a list of dicts (JSONL rows)."""
    logger.info(f"Validating and transforming {len(df)} rows against schema '{schema.name}'.")
    transformed_data = []
    schema_fields = {field['name']: field for field in schema.fields}
    schema_field_names = set(schema_fields.keys())
    df_columns = set(df.columns)

    # Basic check: Are all non-vector schema fields present in the DataFrame?
    required_data_fields = {f_name for f_name, f_def in schema_fields.items() if not f_def.get('is_vector')}
    missing_fields = required_data_fields - df_columns
    if missing_fields:
        logger.error(f"Validation failed: Missing required columns in input data for schema '{schema.name}': {missing_fields}")
        raise ValueError(f"Missing required columns in input data: {missing_fields}")

    # Warn about extra columns
    extra_columns = df_columns - schema_field_names
    if extra_columns:
        logger.warning(f"Input data contains extra columns not defined in schema '{schema.name}': {extra_columns}. These will be ignored.")

    skipped_rows = 0
    for index, row in df.iterrows():
        record = {}
        valid_record = True
        for field_name, field_def in schema_fields.items():
            if not valid_record: continue # Skip further processing if row is already marked invalid

            if field_def.get('is_vector'):
                record[field_name] = None
            elif field_name in df.columns:
                value = row[field_name]
                target_type = field_def.get('type')
                
                # Handle potential NaN/None values before conversion
                if pd.isna(value):
                     # Decide how to handle missing values: Use None, default, or raise error?
                     # For simplicity, let's use None if field is nullable (not implemented), else skip row?
                     # Using None for now.
                     record[field_name] = None
                     continue
                     
                # Attempt Type Conversion
                try:
                    converted_value = None
                    if target_type == 'int':
                        converted_value = int(value)
                    elif target_type == 'float':
                        converted_value = float(value)
                    elif target_type == 'bool':
                         # Handle common string representations of bool
                         if isinstance(value, str) and value.lower() in ['true', 'false']:
                             converted_value = value.lower() == 'true'
                         else:
                             converted_value = bool(value)
                    elif target_type == 'str':
                        # Ensure it's a string, handle potential non-string types
                        converted_value = str(value)
                    else: # Should not happen if schema is validated
                        converted_value = value 
                        
                    record[field_name] = converted_value
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Skipping row {index}: Failed to convert value '{value}' (type: {type(value)}) to target type '{target_type}' for field '{field_name}'. Error: {e}")
                    valid_record = False # Mark record as invalid
                    skipped_rows += 1
                    break # Stop processing fields for this invalid row
                    
            else:
                 # This case should not be hit due to the check above
                 logger.error(f"Logic error: Required field '{field_name}' missing in row {index} for schema '{schema.name}'.")
                 valid_record = False
                 skipped_rows += 1
                 break
                 
        if valid_record:
            transformed_data.append(record)
             
    if skipped_rows > 0:
         logger.warning(f"Skipped {skipped_rows} rows during transformation due to type conversion or other errors.")
         
    logger.info(f"Transformation complete. {len(transformed_data)} rows prepared for JSONL output.")
    return transformed_data

def save_to_jsonl(data: List[Dict[str, Any]], schema_name: str, original_filename: str) -> str:
    """Saves the transformed data to a JSONL file in the data directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = os.path.splitext(os.path.basename(original_filename))[0]
    safe_base_filename = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in base_filename)
    # Consistent naming convention
    output_filename = f"{schema_name}_{safe_base_filename}_processed_{timestamp}.jsonl"
    output_path = os.path.join(DATA_DIR, output_filename)

    logger.info(f"Attempting to save {len(data)} records to JSONL file: {output_path}")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, record in enumerate(data):
                 try:
                     json.dump(record, f, ensure_ascii=False)
                     f.write('\n')
                 except TypeError as json_err:
                      logger.error(f"JSON serialization error on record {i} for {output_path}: {json_err}. Record: {record}")
                      # Decide: skip record, raise error, write placeholder?
                      # For now, let's skip the problematic record and log it.
                      continue 
                      
        logger.info(f"Successfully saved transformed data to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error saving data to {output_path}: {e}", exc_info=True)
        raise

def process_uploaded_file(uploaded_file_path: str, schema: SchemaModel) -> str:
    """Orchestrates the loading, validation, transformation, and saving process."""
    logger.info(f"Starting data processing for file: {uploaded_file_path} with schema: {schema.name}")
    try:
        df = load_data_from_file(uploaded_file_path)
        if df is None or df.empty:
            logger.warning(f"No data loaded from {uploaded_file_path} or file is empty.")
            raise ValueError("Failed to load data or file is empty.")
        
        transformed_data = validate_and_transform_data(df, schema)
        if not transformed_data:
             logger.warning(f"Transformation resulted in empty dataset for {uploaded_file_path} and schema {schema.name}.")
             # Decide if an empty JSONL should be created or raise error
             raise ValueError("No valid data produced after transformation.")
        
        jsonl_path = save_to_jsonl(transformed_data, schema.name, uploaded_file_path)
        logger.info(f"Data processing successful. Output JSONL: {jsonl_path}")
        return jsonl_path

    except Exception as e:
        logger.error(f"Data processing pipeline failed for file {uploaded_file_path}: {e}", exc_info=True)
        # Re-raise the exception so the UI can catch it
        raise 