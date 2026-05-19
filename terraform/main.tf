provider "aws" {
  region = var.aws_region
}

data "aws_ecr_repository" "notification" {
  name = "notification-service"
}

data "aws_caller_identity" "current" {}

locals {
  lab_role_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/LabRole"
}

# SNS — email when Lambda publishes (confirm subscription in inbox after apply)
resource "aws_sns_topic" "sales_notifications" {
  name = var.sns_topic_name
}

resource "aws_sns_topic_subscription" "email_target" {
  topic_arn = aws_sns_topic.sales_notifications.arn
  protocol  = "email"
  endpoint  = var.notification_email
}

resource "aws_lambda_function" "notification_service" {
  function_name = var.lambda_function_name
  role          = local.lab_role_arn
  package_type  = "Image"
  image_uri     = "${data.aws_ecr_repository.notification.repository_url}:latest"
  timeout       = 30

  environment {
    variables = {
      SNS_TOPIC_ARN    = aws_sns_topic.sales_notifications.arn
      NOTIFICATION_EMAIL = var.notification_email
    }
  }
}

# Easy trigger: POST to this URL (no SQS). Auth NONE — lab only.
resource "aws_lambda_function_url" "notification_url" {
  function_name      = aws_lambda_function.notification_service.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
    allow_methods = ["POST"]
  }
}

# SQS trigger optional — off by default until Sales sends queue messages
data "aws_sqs_queue" "ticket_queue" {
  count = var.enable_sqs_trigger ? 1 : 0
  name  = "sales-ticket-queue"
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  count = var.enable_sqs_trigger ? 1 : 0

  event_source_arn = data.aws_sqs_queue.ticket_queue[0].arn
  function_name    = aws_lambda_function.notification_service.arn
  enabled          = true
  batch_size       = 10
}
