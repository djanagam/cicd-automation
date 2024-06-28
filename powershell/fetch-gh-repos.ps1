# Replace with your GitHub organization name
$orgName = "your-org-name"

# Number of repositories per page
$perPage = 100

# Initialize page number
$page = 1

# Initialize an array to store all repository names
$repos = @()

# Fetch all repositories in the organization
do {
    # Fetch repositories for the current page
    $currentRepos = gh repo list $orgName --limit $perPage --page $page --json name --jq '.[].name'
    
    if ($currentRepos) {
        $repos += $currentRepos
        $page++
    }
} while ($currentRepos)

# Loop through each repository to check if GitHub Actions is enabled
foreach ($repo in $repos) {
    # Fetch GitHub Actions settings for the repository
    $actionsEnabled = gh api "/repos/$orgName/$repo/actions/permissions" --jq '.enabled'
    
    if ($actionsEnabled -eq "true") {
        Write-Output "$repo has GitHub Actions enabled"
    }
}