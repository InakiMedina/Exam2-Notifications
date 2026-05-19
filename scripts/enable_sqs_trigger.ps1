# One-time fix when Lambda exists but has no SQS event source mapping.
# Run with AWS lab credentials: .\scripts\enable_sqs_trigger.ps1

$region = "us-east-1"
$fn = "SalesNotificationHandler"
$queueName = "sales-ticket-queue"

$queueUrl = aws sqs get-queue-url --queue-name $queueName --region $region --query QueueUrl --output text
$queueArn = aws sqs get-queue-attributes --queue-url $queueUrl --attribute-names QueueArn --region $region --query Attributes.QueueArn --output text

$existing = aws lambda list-event-source-mappings --function-name $fn --region $region --output json | ConvertFrom-Json
$map = $existing.EventSourceMappings | Where-Object { $_.EventSourceArn -eq $queueArn }
if ($map) {
    Write-Host "Already mapped: UUID=$($map.UUID) state=$($map.State) enabled=$($map.Enabled)"
    exit 0
}

Write-Host "Creating event source mapping: $queueArn -> $fn"
aws lambda create-event-source-mapping `
    --function-name $fn `
    --event-source-arn $queueArn `
    --batch-size 10 `
    --enabled `
    --region $region

Write-Host "Done. Re-run Sales\tests\diagnose_sale_email.ps1 — SQS trigger should show Enabled."
