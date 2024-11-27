import csv

# Function 4: Manage GitHub environments and add reviewers based on the CSV report
def manage_github_environments_from_csv(csv_file, github_token):
    """
    Manage GitHub environments and add a GitHub team as a reviewer for environments with 'e3' in their name,
    if not already added, based on data from a CSV report file.

    :param csv_file: Path to the CSV report file.
    :param github_token: GitHub API token for authentication.
    """
    try:
        # Read the CSV file
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]

        for row in rows:
            repo = row['repository']
            team_name = row['teamName']

            logging.info(f"Processing repository: {repo} | Team: {team_name}")

            api_url = f"https://api.github.com/repos/{repo}/environments"
            headers = {
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json"
            }

            # Fetch all environments
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            environments = response.json().get("environments", [])

            # Filter environments containing 'e3' in their name
            target_environments = [env["name"] for env in environments if "e3" in env["name"]]

            if not target_environments:
                logging.info(f"No environments found with 'e3' in the name for repository '{repo}'.")
                continue

            logging.info(f"Environments to update in repository '{repo}': {target_environments}")

            for env_name in target_environments:
                env_url = f"{api_url}/{env_name}/protection/restrictions/teams"

                # Check existing reviewers for the environment
                response = requests.get(env_url, headers=headers)
                response.raise_for_status()
                existing_teams = [team["slug"] for team in response.json()]

                if team_name in existing_teams:
                    logging.info(f"Team '{team_name}' is already a reviewer for environment '{env_name}' in repository '{repo}'.")
                    continue

                # Add the team as a reviewer
                payload = {"teams": [team_name]}
                response = requests.post(env_url, headers=headers, json=payload)

                if response.status_code == 201 or response.status_code == 200:
                    logging.info(f"Successfully added team '{team_name}' as a reviewer for environment '{env_name}' in repository '{repo}'.")
                else:
                    logging.error(
                        f"Failed to add team '{team_name}' as a reviewer for environment '{env_name}' in repository '{repo}'. "
                        f"Status code: {response.status_code}, Response: {response.text}"
                    )

    except FileNotFoundError:
        logging.error(f"Error: The CSV file '{csv_file}' was not found.")
    except csv.Error as e:
        logging.error(f"Error reading CSV file '{csv_file}': {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error managing GitHub environments: {e}")