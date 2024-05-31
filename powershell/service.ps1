# Get all services whose name contains 'Jenkins'
$services = Get-Service | Where-Object { $_.Name -like "*Jenkins*" }

foreach ($service in $services) {
    # Get the service details including the executable path
    $serviceDetails = Get-WmiObject -Class Win32_Service | Where-Object { $_.Name -eq $service.Name }
    
    # Get the root directory of the executable path
    $exePath = $serviceDetails.PathName
    $rootDirectory = Split-Path $exePath -Parent

    # Find files with names matching 'jenkins*.xml' in the root directory
    $xmlFiles = Get-ChildItem -Path $rootDirectory -Filter "jenkins*.xml"

    foreach ($xmlFile in $xmlFiles) {
        # Stop the service
        Stop-Service -Name $service.Name -Force

        # Read the XML file
        $content = Get-Content -Path $xmlFile.FullName

        # Replace 'D:\apps\java11' with 'D:\apps\java17'
        $newContent = $content -replace 'D:\\apps\\java11', 'D:\\apps\\java17'

        # Save the modified XML file
        Set-Content -Path $xmlFile.FullName -Value $newContent

        # Start the service
        Start-Service -Name $service.Name
    }
}