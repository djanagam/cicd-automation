function SendEmail {
    param(
        [string]$Subject,
        [string]$Body,
        [string]$To,
        [string]$Cc,
        [string]$Bcc
    )

    # Convert comma-separated strings to arrays
    $toAddresses = $To -split ','
    $ccAddresses = $Cc -split ','
    $bccAddresses = $Bcc -split ','

    # Join arrays back into single strings
    $toString = $toAddresses -join ','
    $ccString = $ccAddresses -join ','
    $bccString = $bccAddresses -join ','

    Send-MailMessage -To $toString -Cc $ccString -Bcc $bccString -Subject $Subject -Body $Body -SmtpServer "smtp.example.com"
}

# Usage
SendEmail -Subject "Test Email" -Body "This is a test email" -To "email1@example.com,email2@example.com" -Cc "cc1@example.com,cc2@example.com" -Bcc "bcc1@example.com,bcc2@example.com"