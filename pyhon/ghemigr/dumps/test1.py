def print_json_key_value_pairs(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)  # Load the JSON data
            
            if isinstance(data, dict):  # Check if data is a dictionary
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"{key}:")
                        for item in value:
                            if isinstance(item, dict):  # Check if each item is a dictionary
                                print("  - Key-Value Pairs:")
                                for k, v in item.items():
                                    print(f"    {k}: {v}")
                        print()  # Print a newline for better readability
            else:
                print("The JSON data is not in the expected format (dictionary).")
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage
file_path = 'data.json'  # Replace with your actual file path
print_json_key_value_pairs(file_path)