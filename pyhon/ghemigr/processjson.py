import os
import json
import yaml
import requests

# Function 1: Fetch the JSON result from API using a payload and save it to a file
def fetch_and_save_json(api_url, payload, output_file):
    try:
        headers = {'Content-Type': 'application/json'}
        
        # Perform the POST request with the input JSON payload
        response = requests.post(api_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # Raise an error if the request was unsuccessful

        # Parse JSON response
        json_data = response.json()

        # Save the JSON result to a file
        with open(output_file, 'w') as f:
            json.dump(json_data, f, indent=4)

        print(f"JSON data fetched and saved to {output_file}")
        return json_data

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch JSON data from API: {e}")
        return None

# Function 2: Process the saved JSON result and extract the YAML files
def process_json_and_extract_yaml(json_file):
    try:
        # Load the JSON content from the file
        with open(json_file, 'r') as f:
            data = json.load(f)

        # Extract relevant details
        repository_name = data["repository"]
        db_config = data["dbConfigYaml"]
        workflow_config = data["workflowYaml"]

        # Create directory for the repository
        os.makedirs(repository_name, exist_ok=True)

        # Function to format YAML content
        def format_yaml_content(content):
            try:
                # Parse the content as a YAML object
                yaml_obj = yaml.safe_load(content)
                # Dump it back into a properly formatted YAML string
                return yaml.dump(yaml_obj, sort_keys=False, default_flow_style=False)
            except yaml.YAMLError as exc:
                print(f"Error formatting YAML: {exc}")
                return content

        # Write the _raw files
        db_config_raw_file = os.path.join(repository_name, db_config["fileName"].replace('.yml', '_raw.yml'))
        with open(db_config_raw_file, "w") as f:
            f.write(db_config["content"])

        workflow_raw_file = os.path.join(repository_name, workflow_config["fileName"].replace('.yml', '_raw.yml'))
        with open(workflow_raw_file, "w") as f:
            f.write(workflow_config["content"])

        # Format the YAML content and write to actual file names
        db_config_formatted_content = format_yaml_content(db_config["content"])
        db_config_file = os.path.join(repository_name, db_config["fileName"])
        with open(db_config_file, "w") as f:
            f.write(db_config_formatted_content)

        workflow_formatted_content = format_yaml_content(workflow_config["content"])
        workflow_file = os.path.join(repository_name, workflow_config["fileName"])
        with open(workflow_file, "w") as f:
            f.write(workflow_formatted_content)

        print(f"Files saved and formatted successfully under '{repository_name}' folder.")

    except FileNotFoundError:
        print(f"Error: The JSON file '{json_file}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The JSON file '{json_file}' is not valid JSON.")
    except KeyError as e:
        print(f"Error: Missing key in JSON data - {e}")

# Function 3: Generate a CSV report with specific fields including folderName
def generate_csv_report(json_file, report_file):
    try:
        # Load the JSON content from the file
        with open(json_file, 'r') as f:
            data = json.load(f)

        # Extract fields
        repository = data["repository"]
        branch = data["branch"]
        folder_name = data["folderName"]
        team_name = data["githubTeam"]["teamName"]
        members = data["githubTeam"]["members"]

        # Members as pipe-separated string
        members_str = "|".join(members)

        # Prepare the CSV row
        csv_row = f"{repository},{branch},{folder_name},{team_name},{members_str}\n"

        # Write the row to the report file
        with open(report_file, 'w') as f:
            # Write header first
            f.write("repository,branch,folderName,teamName,members\n")
            # Write data
            f.write(csv_row)

        print(f"CSV report generated and saved to {report_file}")

    except FileNotFoundError:
        print(f"Error: The JSON file '{json_file}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The JSON file '{json_file}' is not valid JSON.")
    except KeyError as e:
        print(f"Error: Missing key in JSON data - {e}")

# Example usage
if __name__ == "__main__":
    api_url = "https://dfhg.org.config/asfryg"
    json_output_file = "api_result.json"
    report_file = "report.csv"

    # Input payload to send with the API request
    input_payload = {
        "key1": "value1",
        "key2": "value2"
    }

    # Fetch JSON result using the input payload and save to file
    json_data = fetch_and_save_json(api_url, input_payload, json_output_file)

    if json_data:
        # Process the JSON file to extract YAMLs
        process_json_and_extract_yaml(json_output_file)
        
        # Generate CSV report from the JSON result
        generate_csv_report(json_output_file, report_file)