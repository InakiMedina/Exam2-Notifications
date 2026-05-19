# POST to Lambda Function URL — sends prewritten test email via SNS.
# 1) Run Notifications terraform apply (or CI)
# 2) Confirm SNS subscription email from AWS (inbox)
# 3) Set $url from: terraform output -raw lambda_function_url
# 4) Run: .\send_email_test.ps1

param(
    [string]$Url = $env:NOTIFICATION_LAMBDA_URL
)

if (-not $Url) {
    Write-Error "Set `$Url or env NOTIFICATION_LAMBDA_URL to terraform output lambda_function_url"
    exit 1
}

$payload = @{ test = $true } | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri $Url -Method Post -Body $payload -ContentType "application/json"
    Write-Host "Success — check inaki.medina@gmail.com (and spam) for the test email."
    $response | ConvertTo-Json -Depth 5
}
catch {
    Write-Error "Request failed: $_"
    exit 1
}
