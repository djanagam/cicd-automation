import subprocess

def run_command(command):
    """Runs a command and returns the output."""
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise Exception(f"Command failed: {result.stderr}")
    return result.stdout.strip()

def branch_exists(remote_url, branch_name):
    """Checks if a branch already exists in the remote repository."""
    try:
        branches = run_command(['git', 'ls-remote', '--heads', remote_url])
        return f"refs/heads/{branch_name}" in branches
    except Exception as e:
        print(f"Error checking branches: {e}")
        return False

def create_and_push_branch(remote_url, new_branch):
    """Clones repo, creates a new branch, and pushes it to the remote repository."""
    try:
        # Clone the repository
        run_command(['git', 'clone', remote_url])
        repo_name = remote_url.split('/')[-1].replace('.git', '')
        
        # Navigate into the repository folder
        subprocess.run(['cd', repo_name], shell=True)

        # Check out the default branch (e.g., main)
        run_command(['git', 'checkout', 'main'])

        # Check if branch already exists
        if branch_exists(remote_url, new_branch):
            print(f"Branch '{new_branch}' already exists. Aborting.")
        else:
            # Create and push the new branch
            run_command(['git', 'checkout', '-b', new_branch])
            run_command(['git', 'push', '--set-upstream', 'origin', new_branch])
            print(f"Branch '{new_branch}' created and pushed successfully.")
    except Exception as e:
        print(f"Error during branch creation: {e}")

# Example usage
remote_url = 'git@github.com:user/repo.git'
new_branch = 'feature/new-feature'

create_and_push_branch(remote_url, new_branch)