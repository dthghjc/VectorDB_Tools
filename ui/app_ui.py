import gradio as gr
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import os # Import os for file operations
import glob # For listing files
import openai # For catching specific exceptions
from config.settings import load_config # Import config loader

# Import backend functions (assuming they handle database sessions internally or via dependency injection)
from app.schema_manager import create_schema, get_all_schemas, get_schema_by_name, delete_schema_by_name, create_upload_log, get_upload_logs
from app.data_processor import process_uploaded_file, DATA_DIR as PROCESSOR_DATA_DIR
from app.vectorizer import vectorize_jsonl_file, DATA_DIR as VECTORIZER_DATA_DIR
from app.milvus_uploader import upload_jsonl_to_milvus, connect_to_milvus # Import Milvus functions
from app.database import SessionLocal # To create sessions for operations

# Load config at the module level to access defaults
config = load_config()

# Ensure data directories are the same or handle differences if needed
DATA_DIR = PROCESSOR_DATA_DIR 
if VECTORIZER_DATA_DIR != DATA_DIR:
    print("Warning: Data directories differ between processor and vectorizer!")
    # Decide how to handle this, e.g., use one, require consistency, etc.

# --- Helper Functions for UI --- #

def _get_db():
    """Context manager for database sessions in UI functions."""
    return SessionLocal()

def format_fields_for_display(fields_json: Optional[List[Dict[str, Any]]]) -> str:
    """Formats the JSON fields list into a readable string for display."""
    if not fields_json:
        return "No fields defined"
    lines = []
    for field in fields_json:
        details = f"{field.get('name', 'N/A')} ({field.get('type', 'N/A')})"
        if field.get('is_primary'):
            details += " [PK]"
        if field.get('is_vector'):
            details += f" [Vector, Dim={field.get('dim', 'N/A')}]"
        lines.append(details)
    return "\n".join(lines)

def get_schema_names() -> List[str]:
    """Fetches names of all schemas for dropdowns."""
    with _get_db() as db:
        schemas = get_all_schemas(db)
        return sorted([s.name for s in schemas]) # Sort names

def refresh_schema_list() -> pd.DataFrame:
    """Fetches all schemas and formats them into a Pandas DataFrame for Gradio Table."""
    with _get_db() as db:
        schemas = get_all_schemas(db)
        data = {
            "Name": [s.name for s in schemas],
            "Description": [s.description or "-" for s in schemas],
            "Fields": [format_fields_for_display(s.fields) for s in schemas],
            "Created At": [s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "-" for s in schemas]
        }
        df = pd.DataFrame(data, columns=["Name", "Description", "Fields", "Created At"])
        return df.sort_values(by="Name").reset_index(drop=True)

def list_jsonl_files() -> List[str]:
    """Lists .jsonl files in the DATA_DIR."""
    try:
        jsonl_files = glob.glob(os.path.join(DATA_DIR, "*.jsonl"))
        # Return only filenames, not full paths, for display
        return sorted([os.path.basename(f) for f in jsonl_files])
    except Exception as e:
        print(f"Error listing JSONL files in {DATA_DIR}: {e}")
        return []

def get_schema_fields_for_dropdowns(schema_name: Optional[str]) -> (gr.update, gr.update):
    """Fetches text and vector fields for a given schema name to update dropdowns."""
    if not schema_name:
        return gr.update(choices=[], value=None), gr.update(choices=[], value=None)
    
    text_fields = []
    vector_fields = []
    try:
        with _get_db() as db:
            schema = get_schema_by_name(db, schema_name)
            if schema and schema.fields:
                for field in schema.fields:
                    field_name = field.get('name')
                    if not field_name: continue
                    
                    if field.get('is_vector'):
                        vector_fields.append(field_name)
                    # Assuming basic types that can hold text
                    elif field.get('type') in ['str', 'text', 'varchar']: # Be more specific if needed
                         text_fields.append(field_name)
                         
        return gr.update(choices=sorted(text_fields), value=None), gr.update(choices=sorted(vector_fields), value=None)
    except Exception as e:
        print(f"Error fetching fields for schema '{schema_name}': {e}")
        return gr.update(choices=[], value=None), gr.update(choices=[], value=None)

def refresh_upload_history() -> pd.DataFrame:
     """Fetches upload logs and formats them for display."""
     try:
          with _get_db() as db:
               logs = get_upload_logs(db, limit=200) # Get recent 200 logs
          if not logs:
               return pd.DataFrame(columns=["Time", "Schema", "File", "Records", "Status", "Message"])
          
          data = {
               "Time": [log.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if log.uploaded_at else "-" for log in logs],
               "Schema": [log.schema_name for log in logs],
               "File": [log.uploaded_filename for log in logs],
               "Records": [log.record_count for log in logs],
               "Status": [log.status for log in logs],
               "Message": [log.message or "-" for log in logs]
          }
          return pd.DataFrame(data)
     except Exception as e:
          print(f"Error refreshing upload history: {e}")
          return pd.DataFrame({"Error": [f"Failed to load history: {e}"]})

# --- UI Event Handlers --- #

def handle_create_schema(name: str, description: Optional[str], fields_json_str: str) -> Tuple[str, pd.DataFrame, gr.update, gr.update, gr.update]:
    """Handles the button click for creating a new schema."""
    schema_dropdown_update = gr.update(choices=get_schema_names())
    if not name:
        return "Schema name cannot be empty.", gr.update(), schema_dropdown_update, schema_dropdown_update, schema_dropdown_update
    
    # Basic parsing of fields (Robust JSON parsing and validation needed!)
    try:
        # This assumes fields_json_str is a valid JSON list of dicts
        # Example: '[{"name": "id", "type": "int", "is_primary": true}, {"name": "text", "type": "str"}]'
        # In a real UI, you'd likely build this structure from dynamic inputs
        fields = pd.read_json(fields_json_str, orient='records') # Use pandas for easy JSON handling
        fields_list = fields.to_dict(orient='records')
        # TODO: Add validation using validate_schema_definition(fields_list)
    except Exception as e:
        # No need to refresh list on parse error
        return f"Error parsing fields JSON: {e}. Expected format: '[{{"name": ...}}, ...]'.", gr.update(), gr.update(), gr.update(), gr.update()

    if not fields_list:
         return "Schema must have at least one field.", gr.update(), gr.update(), gr.update(), gr.update()

    try:
        with _get_db() as db:
            create_schema(db=db, name=name, description=description, fields=fields_list)
        # Successfully created, now refresh list and update dropdown
        return f"Schema '{name}' created successfully!", refresh_schema_list(), schema_dropdown_update, schema_dropdown_update, schema_dropdown_update
    except ValueError as e:
        # Error during creation (e.g., duplicate name), refresh list to show current state
        return f"Error: {e}", refresh_schema_list(), gr.update(), gr.update(), gr.update()
    except Exception as e:
        # Log the full error server-side
        print(f"Unexpected error creating schema: {e}")
        # Refresh list on unexpected error
        return "An unexpected error occurred.", refresh_schema_list(), gr.update(), gr.update(), gr.update()

def handle_delete_schema(schema_name: str) -> Tuple[str, pd.DataFrame, gr.update, gr.update, gr.update]:
    """Handles the deletion of a schema selected from the list."""
    schema_dropdown_update = gr.update(choices=get_schema_names())
    if not schema_name:
        # No need to refresh list if name is empty
        return "Please enter the name of the schema to delete.", gr.update(), schema_dropdown_update, schema_dropdown_update
    
    # Add a confirmation step in a real UI
    try:
        with _get_db() as db:
            deleted = delete_schema_by_name(db, schema_name)
            refreshed_list = refresh_schema_list() # Refresh the list regardless
            if deleted:
                # TODO: Add logic here to check and potentially delete the corresponding Milvus collection
                return f"Schema '{schema_name}' deleted successfully.", refreshed_list, schema_dropdown_update, schema_dropdown_update
            else:
                return f"Schema '{schema_name}' not found.", refreshed_list, schema_dropdown_update, schema_dropdown_update
    except ValueError as e:
         # Refresh list on known error
         return f"Error deleting schema '{schema_name}': {e}", refresh_schema_list(), gr.update(), gr.update()
    except Exception as e:
        print(f"Unexpected error deleting schema: {e}")
        # Refresh list on unexpected error
        return f"An unexpected error occurred while deleting '{schema_name}'.", refresh_schema_list(), gr.update(), gr.update()

# Data Processing Handler
def handle_process_data(uploaded_file: Optional[Any], selected_schema_name: Optional[str]) -> (str, Optional[str], gr.update):
    jsonl_dropdown_update = gr.update(choices=list_jsonl_files())
    if uploaded_file is None or not selected_schema_name:
        return "Error: Please upload a file (CSV/JSON) and select a schema.", None, jsonl_dropdown_update

    uploaded_file_path = uploaded_file.name # Gradio File object has .name attribute for path
    print(f"File received: {uploaded_file_path}, Schema selected: {selected_schema_name}")

    try:
        with _get_db() as db:
            schema = get_schema_by_name(db, selected_schema_name)
            if not schema:
                return f"Error: Schema '{selected_schema_name}' not found in database.", None, jsonl_dropdown_update
        
        # Call the backend processing function
        jsonl_output_path = process_uploaded_file(uploaded_file_path, schema)
        
        # Make path relative to DATA_DIR for display/download consistency
        # relative_jsonl_path = os.path.relpath(jsonl_output_path, start=DATA_DIR)
        # Gradio File component usually handles the path correctly if it's accessible

        return f"Successfully processed file. Output saved to: {jsonl_output_path}", jsonl_output_path, gr.update(choices=list_jsonl_files(), value=os.path.basename(jsonl_output_path))

    except ValueError as e:
        return f"Processing Error: {e}", None, jsonl_dropdown_update
    except Exception as e:
        print(f"Unexpected error during data processing: {e}") # Log full error
        # Provide a cleaner error message to the user
        return f"An unexpected error occurred during processing. Check logs for details.", None, jsonl_dropdown_update

# Vectorization Handler
def handle_vectorize_data(
    jsonl_filename: Optional[str],
    schema_name: Optional[str],
    text_field: Optional[str],
    vector_field: Optional[str],
    model_type: Optional[str]
) -> (str, Optional[str], gr.update):
    jsonl_dropdown_update = gr.update(choices=list_jsonl_files())
    if not all([jsonl_filename, schema_name, text_field, vector_field, model_type]):
        return "Error: Please select a JSONL file, schema, text field, vector field, and model.", None, jsonl_dropdown_update

    jsonl_file_path = os.path.join(DATA_DIR, jsonl_filename) # Construct full path
    print(f"Starting vectorization for: {jsonl_filename}, Schema: {schema_name}, Text: {text_field}, Vector: {vector_field}, Model: {model_type}")

    try:
        with _get_db() as db:
            schema = get_schema_by_name(db, schema_name)
            if not schema:
                return f"Error: Schema '{schema_name}' not found.", None, jsonl_dropdown_update

        # Call the backend vectorization function
        output_vector_path = vectorize_jsonl_file(
            jsonl_file_path=jsonl_file_path,
            schema=schema,
            model_type=model_type,
            text_field_name=text_field,
            vector_field_name=vector_field
        )
        
        # Refresh the list of JSONL files after successful vectorization
        output_filename = os.path.basename(output_vector_path)
        return f"Vectorization successful. Output saved to: {output_vector_path}", output_vector_path, gr.update(choices=list_jsonl_files(), value=output_filename)

    except FileNotFoundError as e:
         return f"Error: {e}", None, jsonl_dropdown_update
    except ValueError as e:
         return f"Vectorization Error: {e}", None, jsonl_dropdown_update
    except openai.error.AuthenticationError: # Specific error for OpenAI key issue
         return "Vectorization Error: OpenAI API key is invalid or missing. Check .env configuration.", None, jsonl_dropdown_update
    except Exception as e:
        print(f"Unexpected error during vectorization: {e}") # Log full error
        # Consider logging traceback: import traceback; traceback.print_exc()
        return f"An unexpected error occurred during vectorization. Check logs.", None, jsonl_dropdown_update

# --- Gradio UI Construction --- #

def create_schema_ui():
    """Creates the Gradio interface blocks for schema management."""
    with gr.Blocks(analytics_enabled=False) as schema_tab_block:
        gr.Markdown("## Schema Management")
        
        with gr.Tabs():
            with gr.TabItem("Create Schema"):
                with gr.Row():
                    with gr.Column(scale=1):
                        schema_name = gr.Textbox(label="Schema Name", placeholder="e.g., documents_openai")
                        schema_desc = gr.Textbox(label="Description (Optional)", placeholder="Schema for text documents with OpenAI embeddings")
                        # Simple JSON input for fields for now - Needs a dynamic UI builder!
                        gr.Markdown("Define fields as a JSON list (e.g., `[{\"name\": \"id\", \"type\": \"int\", \"is_primary\": true}, {\"name\": \"text\", \"type\": \"str\"}, {\"name\": \"embedding\", \"type\": \"vector<float>\", \"is_vector\": true, \"dim\": 1536}]`)")
                        schema_fields_json = gr.Textbox(
                            label="Fields (JSON List)",
                            lines=5,
                            placeholder='[{"name": "doc_id", "type": "int", "is_primary": true}, ...]',
                            elem_id="schema-fields-json"
                        )
                        create_button = gr.Button("Create Schema", variant="primary")
                    with gr.Column(scale=2):
                        status_message_create = gr.Textbox(label="Status", interactive=False)

            with gr.TabItem("View & Delete Schemas"):
                gr.Markdown("Existing schemas stored in the database.")
                refresh_button = gr.Button("Refresh List")
                schema_table = gr.DataFrame(
                    headers=["Name", "Description", "Fields", "Created At"],
                    datatype=["str", "str", "str", "str"],
                    label="Schema List",
                    interactive=False # Display only
                )
                with gr.Row():
                     delete_name_input = gr.Textbox(label="Schema Name to Delete", placeholder="Enter exact name")
                     delete_button = gr.Button("Delete Schema", variant="stop")
                status_message_delete = gr.Textbox(label="Status", interactive=False)

        # --- Event Listeners --- #
        create_button.click(
            fn=handle_create_schema,
            inputs=[schema_name, schema_desc, schema_fields_json],
            outputs=[status_message_create, schema_table, schema_dropdown_proc, schema_dropdown_vect] # Update table after creation
        )

        delete_button.click(
            fn=handle_delete_schema,
            inputs=[delete_name_input],
            outputs=[status_message_delete, schema_table, schema_dropdown_proc, schema_dropdown_vect] # Update table after deletion
        )

        refresh_button.click(
            fn=refresh_schema_list,
            inputs=[],
            outputs=[schema_table, schema_dropdown_proc, schema_dropdown_vect]
        )

        # Load initial data when the tab is selected or app starts
        schema_tab_block.load(fn=refresh_schema_list, inputs=[], outputs=[schema_table, schema_dropdown_proc, schema_dropdown_vect])

    # Return all interactive components needed for event handling
    return (schema_tab_block, schema_name, schema_desc, schema_fields_json, 
            create_button, status_message_create, refresh_button, schema_table, 
            delete_name_input, delete_button, status_message_delete, schema_dropdown_proc, schema_dropdown_vect)

def create_data_processing_ui():
    # This function defines the UI elements for the data processing tab
    with gr.Blocks(analytics_enabled=False) as processing_tab_block:
        gr.Markdown("## Data Processing: CSV/JSON to JSONL")
        with gr.Row():
            with gr.Column(scale=1):
                file_uploader = gr.File(label="Upload Data File (CSV or JSON)", file_types=['.csv', '.json'])
                schema_dropdown = gr.Dropdown(
                    label="Select Target Schema",
                    # choices=get_schema_names(), # Set initial choices in main UI
                    interactive=True
                )
                process_button = gr.Button("Process Data", variant="primary")
            with gr.Column(scale=2):
                status_message_process = gr.Textbox(label="Status", interactive=False)
                output_file_display = gr.File(label="Generated JSONL File", interactive=False)
        
    # Return components needed for event handling
    return (processing_tab_block, file_uploader, schema_dropdown, 
            process_button, status_message_process, output_file_display)

def create_vectorization_ui():
    # This function defines the UI elements for the vectorization tab
    with gr.Blocks(analytics_enabled=False) as vectorization_tab_block:
        gr.Markdown("## Vectorization: JSONL to Vector")
        with gr.Row():
            with gr.Column(scale=1):
                jsonl_filename = gr.Dropdown(
                    label="Select JSONL File",
                    choices=list_jsonl_files(),
                    interactive=True
                )
                schema_dropdown = gr.Dropdown(
                    label="Select Target Schema",
                    choices=get_schema_names(),
                    interactive=True
                )
                text_field = gr.Dropdown(
                    label="Select Text Field",
                    choices=[],
                    interactive=True
                )
                vector_field = gr.Dropdown(
                    label="Select Vector Field",
                    choices=[],
                    interactive=True
                )
                model_type = gr.Dropdown(
                    label="Select Model Type",
                    choices=["OpenAI", "BGE"],
                    interactive=True
                )
                vectorize_button = gr.Button("Vectorize Data", variant="primary")
            with gr.Column(scale=2):
                status_message_vectorize = gr.Textbox(label="Status", interactive=False)
                output_file_display = gr.File(label="Generated Vector File", interactive=False)
        
    # Return components needed for event handling
    return (vectorization_tab_block, jsonl_filename, schema_dropdown, text_field, vector_field, model_type, vectorize_button, status_message_vectorize, output_file_display)

def create_milvus_upload_ui():
     with gr.Blocks(analytics_enabled=False) as milvus_tab_block:
          gr.Markdown("## Milvus Upload: Insert JSONL Data")
          with gr.Row():
               with gr.Column(scale=1):
                    jsonl_filename = gr.Dropdown(label="Select JSONL File (with vectors)", interactive=True)
                    schema_dropdown = gr.Dropdown(label="Select Target Schema/Collection", interactive=True)
                    gr.Markdown("Milvus Connection Details")
                    # Use loaded config for default values
                    milvus_host = gr.Textbox(label="Host", value=config.milvus_host)
                    milvus_port = gr.Textbox(label="Port", value=str(config.milvus_port)) # Ensure string for Textbox
                    upload_button = gr.Button("Upload to Milvus", variant="primary")
               with gr.Column(scale=2):
                    status_message_upload = gr.Textbox(label="Status", interactive=False)
     # Needs the history table from the other tab to update it
     history_table_placeholder = gr.DataFrame(visible=False)
     return (milvus_tab_block, jsonl_filename, schema_dropdown, milvus_host, milvus_port, 
             upload_button, status_message_upload, history_table_placeholder)

def create_ui(): # Add config as argument if needed later
    """Creates the main Gradio application UI with all tabs."""
    with gr.Blocks(title="Milvus Vector Tools", theme=gr.themes.Default(), analytics_enabled=False) as demo:
        gr.Markdown("# Milvus Vector Tools")
        
        # --- Instantiate UI components --- 
        (schema_tab_block, schema_name, schema_desc, schema_fields_json, 
         create_button, status_message_create, refresh_button, schema_table, 
         delete_name_input, delete_button, status_message_delete, schema_dropdown_proc, schema_dropdown_vect) = create_schema_ui()
        
        (processing_tab_block, file_uploader, schema_dropdown_proc, 
         process_button, status_message_process, output_file_display) = create_data_processing_ui()

        (vectorization_tab_block, jsonl_filename, schema_dropdown_vect, text_field, vector_field, model_type, vectorize_button, status_message_vectorize, output_file_display) = create_vectorization_ui()

        (milvus_tab_block, jsonl_filename_upload, schema_dropdown_upload, milvus_host, milvus_port, 
         upload_button, status_message_upload, history_table_placeholder) = create_milvus_upload_ui()

        # --- Arrange Tabs --- 
        with gr.Tabs():
            with gr.TabItem("Schema Management"):
                # Embed the pre-created block - this might not work as expected with nested Blocks
                # Instead, we define components above and just reference them here for layout
                schema_tab_block.render() # Render the block here
            
            with gr.TabItem("Data Processing"):
                processing_tab_block.render() # Render the block here

            with gr.TabItem("Vectorization"):
                vectorization_tab_block.render() # Render the block here

            with gr.TabItem("Milvus Upload"): # Placeholder
                gr.Markdown("## Milvus Upload (Coming Soon)")
                gr.Markdown("Select JSONL file with vectors, choose target Milvus collection (based on schema), upload data.")
                
            with gr.TabItem("Upload History"): # Placeholder
                gr.Markdown("## Upload History (Coming Soon)")
                gr.Markdown("View logs of past data uploads.")

        # --- Define Event Handlers (outside the tab structure) --- #

        # Schema Create Button
        create_button.click(
            fn=handle_create_schema,
            inputs=[schema_name, schema_desc, schema_fields_json],
            outputs=[status_message_create, schema_table, schema_dropdown_proc, schema_dropdown_vect] 
        )
        
        # Schema Delete Button
        delete_button.click(
            fn=handle_delete_schema,
            inputs=[delete_name_input],
            outputs=[status_message_delete, schema_table, schema_dropdown_proc, schema_dropdown_vect] 
        )

        # Schema Refresh Button (Updates table and dropdown)
        def refresh_all_schema_components():
            return refresh_schema_list(), gr.update(choices=get_schema_names()), gr.update(choices=get_schema_names())
        
        refresh_button.click(
            fn=refresh_all_schema_components,
            inputs=[],
            outputs=[schema_table, schema_dropdown_proc, schema_dropdown_vect] # Update both table and dropdown
        )

        # Data Process Button
        process_button.click(
            fn=handle_process_data,
            inputs=[file_uploader, schema_dropdown_proc],
            outputs=[status_message_process, output_file_display]
        )

        # Vectorize Button
        vectorize_button.click(
            fn=handle_vectorize_data,
            inputs=[jsonl_filename, schema_dropdown_vect, text_field, vector_field, model_type],
            outputs=[status_message_vectorize, output_file_display]
        )

        # Initial data loading for schema table and dropdown when app starts
        def load_initial_data():
            initial_list = refresh_schema_list()
            initial_choices = get_schema_names()
            return initial_list, gr.update(choices=initial_choices), gr.update(choices=initial_choices)

        demo.load(
            fn=load_initial_data,
            inputs=[],
            outputs=[schema_table, schema_dropdown_proc, schema_dropdown_vect]
        )

    return demo

# Example of running this UI standalone (for testing)
if __name__ == "__main__":
    # Initialize DB if running standalone for testing UI
    from app.database import init_db
    try:
        init_db()
    except Exception as e:
        print(f"Standalone UI DB Init Error: {e}")
        # Decide if UI should launch anyway

    ui = create_ui()
    ui.launch(server_name="0.0.0.0", auth=("test", "test1234")) # Use dummy auth for direct testing 