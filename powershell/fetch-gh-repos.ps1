# Replace with your GitHub organization name
$orgName = "your-org-name"

# Number of repositories per page
$perPage = 100

# Initialize variables
$page = 1
$repos = @()

# Function to fetch repositories for a specific page
function FetchRepositories($orgName, $perPage, $page) {
    $repos = gh repo list $orgName --limit $perPage --json name --jq '.[].name'
    return $repos
}

# Fetch repositories until all are fetched
do {
    $currentRepos = FetchRepositories $orgName $perPage $page
    
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