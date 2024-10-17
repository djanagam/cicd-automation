import subprocess

def branch_exists(remote_url, branch_name):
    """Checks if a branch already exists in the remote repository."""
    try:
        # Use subprocess to run 'git ls-remote --heads' and capture the output
        result = subprocess.run(
            ['git', 'ls-remote', '--heads', remote_url],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to check branches: {result.stderr}")
        
        # Check if the branch name exists in the output
        return f"refs/heads/{branch_name}" in result.stdout
    except Exception as e:
        print(f"Error checking branches: {e}")
        return False

def create_and_push_branch(remote_url, new_branch):
    """Clones repo, creates a new branch, and pushes it to the remote repository."""
    try:
        # Clone the repository
        subprocess.run(['git', 'clone', remote_url], check=True)
        repo_name = remote_url.split('/')[-1].replace('.git', '')

        # Navigate into the repository folder
        subprocess.run(['cd', repo_name], shell=True, check=True)

        # Check out the default branch (e.g., 'main')
        subprocess.run(['git', 'checkout', 'main'], check=True)

        # Check if branch already exists
        if branch_exists(remote_url, new_branch):
            print(f"Branch '{new_branch}' already exists. Aborting.")
        else:
            # Create the new branch
            subprocess.run(['git', 'checkout', '-b', new_branch], check=True)

            # Push the new branch to the remote
            subprocess.run(['git', 'push', '--set-upstream', 'origin', new_branch], check=True)

            print(f"Branch '{new_branch}' created and pushed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during branch creation: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Example usage
remote_url = 'git@github.com:user/repo.git'
new_branch = 'feature/new-feature'

create_and_push_branch(remote_url, new_branch)