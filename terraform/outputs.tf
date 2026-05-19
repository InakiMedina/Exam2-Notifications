output "lambda_function_url" {
  description = "The public URL of the Lambda function"
  value       = aws_lambda_function_url.notification_url.function_url
}

output "sns_topic_arn" {
  description = "The ARN of the SNS topic"
  value       = aws_sns_topic.sales_notifications.arn
}

output "notification_email" {
  description = "Subscribed email (confirm AWS confirmation link once)"
  value       = var.notification_email
}