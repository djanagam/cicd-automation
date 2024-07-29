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
    $message.Body = $body
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

# Initialize report
$report = @()
$lockedAccounts = @()

# Check each account's status
foreach ($username in $userDescriptions.Keys) {
    $isLocked = Is-AccountLocked -username $username
    $status = if ($isLocked) { "Locked" } else { "Not Locked" }
    $description = $userDescriptions[$username]
    $report += "$username ($description): $status"
    if ($isLocked) {
        $lockedAccounts += $username
    }
}

# Join report into a single string
$reportBody = $report -join "`n"

# Send email if any account is locked
if ($lockedAccounts.Count -gt 0) {
    $subject = "Account Locked Alert"
    $body = "The following accounts have been checked for lock status:`n`n$reportBody"
    Send-Email -subject $subject -body $body
} else {
    Write-Output "No accounts are locked."
}