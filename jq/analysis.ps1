param (
    [string]$InputJsonFile,
    [string]$OutputCsvFile = "report.csv"
)

# Ensure jq is available
if (-not (Get-Command jq -ErrorAction SilentlyContinue)) {
    Write-Error "jq is not installed or not available in the system PATH."
    exit 1
}

# Write the header to the CSV file
"Shortname,Controllerurl,url" | Out-File -FilePath $OutputCsvFile -Encoding utf8

# Extract the required fields using jq and append to the CSV file
jq -r '
  .Usages[] | .[] | [.plugininfo.Shortname, .Location.Controllerurl, .Location.url] | @csv
' $InputJsonFile | Out-File -FilePath $OutputCsvFile -Encoding utf8 -Append

Write-Output "CSV report generated at: $OutputCsvFile"