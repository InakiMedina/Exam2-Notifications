variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "sns_topic_name" {
  description = "The name of the SNS topic"
  type        = string
  default     = "Exam2-Sales-Notifications"
}

variable "lambda_function_name" {
  description = "The name of the Lambda function"
  type        = string
  default     = "SalesNotificationHandler"
}

variable "account_id" {
  description = "The AWS Account ID"
  type        = string
}

variable "notification_email" {
  description = "The email address to subscribe to the SNS topic"
  type        = string
  default     = "inaki.medina@gmail.com"
}

variable "enable_sqs_trigger" {
  description = "Wire Lambda to sales-ticket-queue (leave false until Sales publishes to SQS)"
  type        = bool
  default     = false
}
