# Get all services whose name contains 'Jenkins'
$services = Get-Service | Where-Object { $_.Name -like "*Jenkins*" }

foreach ($service in $services) {
    # Get the service details including the executable path
    $serviceDetails = Get-WmiObject -Class Win32_Service | Where-Object { $_.Name -eq $service.Name }
    
    # Output the service name and executable path
    [PSCustomObject]@{
        ServiceName = $service.Name
        DisplayName = $service.DisplayName
        ExecutablePath = $serviceDetails.PathName
    }
}