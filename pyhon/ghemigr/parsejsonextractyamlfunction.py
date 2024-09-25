def process_json_and_extract_yaml(json_file):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)

        # Check if 'data' is a dictionary
        if not isinstance(data, dict):
            logging.error("The JSON data is not a dictionary. It's likely a list.")
            return

        # Check if the 'repository' key exists in the data
        if REPOSITORY_KEY not in data:
            logging.error(f"Key '{REPOSITORY_KEY}' not found in JSON data.")
            return

        repository_name = data[REPOSITORY_KEY]

        # Create the repository folder if it doesn't exist
        os.makedirs(repository_name, exist_ok=True)

        def format_yaml_content(content):
            try:
                yaml_obj = yaml.safe_load(content)
                return yaml.dump(yaml_obj, sort_keys=False, default_flow_style=False)
            except yaml.YAMLError as exc:
                logging.error(f"Error formatting YAML: {exc}")
                return None

        # Process dbConfigYaml
        if DB_CONFIG_YAML_KEY in data:
            db_config = data[DB_CONFIG_YAML_KEY]
            db_file_name = db_config["fileName"]
            db_file_content = db_config["content"]

            # Save the raw dbConfig YAML content
            db_config_raw_file = os.path.join(repository_name, db_file_name.replace('.yml', '_raw.yml'))
            with open(db_config_raw_file, "w") as f:
                f.write(db_file_content)

            # Format and save dbConfig YAML content
            db_config_formatted_content = format_yaml_content(db_file_content)
            if db_config_formatted_content:
                db_config_file = os.path.join(repository_name, db_file_name)
                with open(db_config_file, "w") as f:
                    f.write(db_config_formatted_content)

        # Process workflowYaml
        if WORKFLOW_YAML_KEY in data:
            workflow_config = data[WORKFLOW_YAML_KEY]
            workflow_file_name = workflow_config["fileName"]
            workflow_file_content = workflow_config["content"]

            # Save the raw workflow YAML content
            workflow_raw_file = os.path.join(repository_name, workflow_file_name.replace('.yml', '_raw.yml'))
            with open(workflow_raw_file, "w") as f:
                f.write(workflow_file_content)

            # Format and save workflow YAML content
            workflow_formatted_content = format_yaml_content(workflow_file_content)
            if workflow_formatted_content:
                workflow_file = os.path.join(repository_name, workflow_file_name)
                with open(workflow_file, "w") as f:
                    f.write(workflow_formatted_content)

        logging.info(f"Files saved and formatted successfully under '{repository_name}' folder.")

    except FileNotFoundError:
        logging.error(f"Error: The JSON file '{json_file}' was not found.")
    except json.JSONDecodeError:
        logging.error(f"Error: The JSON file '{json_file}' is not valid JSON.")
    except KeyError as e:
        logging.error(f"Error: Missing key in JSON data - {e}")