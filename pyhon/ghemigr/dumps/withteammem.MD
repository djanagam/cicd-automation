To avoid fetching all teams and instead directly check if a specific team exists, you can use GitHub’s API to get the team by its name (or slug) without listing all teams. This is more efficient, especially for organizations with a large number of teams.

You can use the following endpoint to check if a specific team exists:

	•	GET /orgs/{org}/teams/{team_slug}: This endpoint allows you to directly check if a team exists by its slug.

Here’s how you can modify your function to use this approach:

Updated Code:

import csv
import requests
import logging

# Initialize logging (reuse the existing configuration)
logging.basicConfig(filename='execution.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"
# Example: Your GitHub organization
ORG_NAME = "your_organization"
# Your personal access token with 'repo', 'admin:org' permissions
GITHUB_TOKEN = "your_personal_access_token"

# Function to check if a specific team exists
def team_exists(team_slug):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    check_team_url = f"{GITHUB_API_URL}/orgs/{ORG_NAME}/teams/{team_slug}"
    response = requests.get(check_team_url, headers=headers)
    
    if response.status_code == 200:
        return True  # Team exists
    elif response.status_code == 404:
        return False  # Team does not exist
    else:
        logging.error(f"Error checking if team exists: {response.status_code}")
        return None

# Function to create a team, add members, and set permissions
def manage_teams_and_permissions(csv_file_path):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Read the CSV report file
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            repo_name = row['Repo']
            branch = row['branch']
            dirname = row['dirname']
            team_name = row['teamname']
            users = row['user1|user2|user3'].split('|')
            new_branch = row['new_branch']
            pull_request_url = row['pull_request_url']

            # Step 1: Check if team exists using the slug
            team_slug = team_name.lower().replace(' ', '-')
            logging.info(f"Checking if team '{team_name}' exists...")

            if team_exists(team_slug):
                logging.info(f"Team '{team_name}' already exists with slug '{team_slug}'.")
            else:
                # Step 2: Create team if it doesn't exist
                logging.info(f"Creating new team '{team_name}'.")
                create_team_url = f"{GITHUB_API_URL}/orgs/{ORG_NAME}/teams"
                team_payload = {
                    "name": team_name,
                    "repo_names": [f"{ORG_NAME}/{repo_name}"],
                    "permission": "push"  # Read/write access
                }

                team_response = requests.post(create_team_url, json=team_payload, headers=headers)
                if team_response.status_code == 201:
                    logging.info(f"Team '{team_name}' created successfully.")
                    team_data = team_response.json()
                    team_slug = team_data['slug']
                else:
                    logging.error(f"Failed to create team '{team_name}'. Status Code: {team_response.status_code}")
                    continue

            # Step 3: Add users to the team
            for user in users:
                logging.info(f"Adding user '{user}' to team '{team_name}'.")
                add_user_url = f"{GITHUB_API_URL}/orgs/{ORG_NAME}/teams/{team_slug}/memberships/{user}"
                add_user_response = requests.put(add_user_url, headers=headers)
                if add_user_response.status_code == 200:
                    logging.info(f"User '{user}' added to team '{team_name}'.")
                else:
                    logging.error(f"Failed to add user '{user}' to team '{team_name}'. Status Code: {add_user_response.status_code}")

            # Step 4: Grant read/write access to the repo for the team
            logging.info(f"Granting read/write access to team '{team_name}' for repository '{repo_name}'.")
            grant_access_url = f"{GITHUB_API_URL}/orgs/{ORG_NAME}/teams/{team_slug}/repos/{ORG_NAME}/{repo_name}"
            access_payload = {
                "permission": "push"  # Grant push (read/write) access
            }
            access_response = requests.put(grant_access_url, json=access_payload, headers=headers)
            if access_response.status_code == 204:
                logging.info(f"Granted read/write access to team '{team_name}' for repository '{repo_name}'.")
            else:
                logging.error(f"Failed to grant access to team '{team_name}'. Status Code: {access_response.status_code}")

# Example usage
csv_file_path = 'report.csv'
manage_teams_and_permissions(csv_file_path)

Key Updates:

	1.	Direct team check: The team_exists() function now queries GET /orgs/{org}/teams/{team_slug} to check if the specific team exists. This avoids fetching all teams.
	•	If the team exists (status_code == 200), the function returns True.
	•	If the team does not exist (status_code == 404), it returns False.
	•	Other errors are logged, and None is returned.
	2.	Team slug creation: The team slug is created by converting the team_name to lowercase and replacing spaces with hyphens (as GitHub commonly handles slugs in this format).

Benefits:

	•	Efficiency: Only the specific team you care about is queried instead of fetching all teams.
	•	Scalability: This approach is more scalable for organizations with a large number of teams.
	•	Logging: Logs important actions such as team existence checks, team creation, user addition, and permission grants to execution.log.

This method will perform efficiently even with many teams in your organization. Let me know if you need any more adjustments!