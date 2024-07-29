# Define variables
$userDescriptions = @{
    "user1" = "Description for user1"
    "user2" = "Description for user2"
    "user3" = "Description for user3"
}

$emailTo = "recipient@example.com"
$emailFrom = "sender@example.com"
$smtpServer = "smtp.example.com"
$smtpPort = 25

# Function to send email
function Send-Email {
    param (
        [string]$subject,
        [string]$body
    )
    $message = New-Object system.net.mail.mailmessage
    $message.from = $emailFrom
    $message.To.add($emailTo)
    $message.Subject = $subject
    $message.IsBodyHtml = $true
    $message.Body = $body
    $message.Priority = [System.Net.Mail.MailPriority]::High  # Mark email as important
    $smtp = New-Object Net.Mail.SmtpClient($smtpServer, $smtpPort)
    $smtp.Send($message)
}

# Function to check if the account is locked
function Is-AccountLocked {
    param (
        [string]$username
    )
    $user = Get-ADUser -Identity $username -Properties LockedOut
    return $user.LockedOut
}

# Initialize variables
$reportRows = @()
$lockedAccounts = @()

# Check each account's status
foreach ($username in $userDescriptions.Keys) {
    $isLocked = Is-AccountLocked -username $username
    $status = if ($isLocked) { "<span style='color:red'>LOCKED</span>" } else { "<span style='color:green'>UNLOCKED</span>" }
    $description = $userDescriptions[$username]
    $reportRows += "<tr><td style='border: 1px solid black; padding: 8px;'>$username</td><td style='border: 1px solid black; padding: 8px;'>$description</td><td style='border: 1px solid black; padding: 8px;'>$status</td></tr>"
    if ($isLocked) {
        $lockedAccounts += $username
    }
}

# Build HTML email body
$genericNote = "Account locked here is the action to do…"
$reportBody = @"
<html>
<body>
    <p>The following accounts have been checked for lock status:</p>
    <table border='1' style='border-collapse: collapse;'>
        <tr>
            <th style='border: 1px solid black; padding: 8px;'>Username</th>
            <th style='border: 1px solid black; padding: 8px;'>Description</th>
            <th style='border: 1px solid black; padding: 8px;'>Status</th>
        </tr>
        $($reportRows -join "`n")
    </table>
    <br>
    <p>$genericNote</p>
</body>
</html>
"@

# Send email if any account is locked
if ($lockedAccounts.Count -gt 0) {
    $subject = "Account Locked Alert"
    Send-Email -subject $subject -body $reportBody
} else {
    Write-Output "No accounts are locked."
}