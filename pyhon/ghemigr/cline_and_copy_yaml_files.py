import os
import shutil
import json
import logging

def clone_and_copy_yaml_files(json_file, target_directory):
    """
    Reads JSON data to copy YAML files from a source to a target directory dynamically based on JSON keys.
    """
    try:
        # Load JSON data
        with open(json_file, 'r') as f:
            data = json.load(f)

        # Retrieve repository name
        repository_name = data.get("repository", "default_repo")
        
        # Retrieve file names dynamically for YAMLs
        db_config_file_name = data.get("dbConfigYaml", {}).get("fileName")
        workflow_file_name = data.get("workflowYaml", {}).get("fileName")

        # Validate that the filenames exist in the JSON
        if not db_config_file_name or not workflow_file_name:
            raise ValueError("Missing required file names in the JSON.")

        # Build the source paths dynamically based on repository structure
        db_config_source_path = os.path.join(repository_name, db_config_file_name)
        workflow_source_path = os.path.join(repository_name, workflow_file_name)

        # Ensure target directory exists
        os.makedirs(target_directory, exist_ok=True)

        # Copy the files to the target directory
        shutil.copy(db_config_source_path, os.path.join(target_directory, db_config_file_name))
        shutil.copy(workflow_source_path, os.path.join(target_directory, workflow_file_name))

        logging.info(f"Copied '{db_config_file_name}' and '{workflow_file_name}' to '{target_directory}' successfully.")
    
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in file: {json_file}")
    except ValueError as e:
        logging.error(f"Validation error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")