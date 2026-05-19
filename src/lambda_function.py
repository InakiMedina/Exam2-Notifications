import json
import os

import boto3

PREWRITTEN_TEST_MESSAGE = """Exam2 — test notification

Hello Inaki,

This is a prewritten test email from the Notification Lambda.
Trigger: POST to the Lambda Function URL (no SQS required).

Sale summary (demo):
  User:  Inaki Medina
  Item:  ITESO Lab Flask
  Price: $15.00

If you received this, SNS + Lambda are working.
"""


def lambda_handler(event, context):
    try:
        if "body" in event and event["body"]:
            data = json.loads(event["body"]) if isinstance(event["body"], str) else event["body"]
        else:
            data = event if isinstance(event, dict) else {}
    except Exception as e:
        print(f"Error parsing body: {e}")
        data = {}

    if data.get("test") is True or data.get("use_prewritten"):
        message = PREWRITTEN_TEST_MESSAGE
        subject = "Exam2 Notification — prewritten test"
    else:
        item = data.get("item", "N/A")
        price = data.get("price", "0")
        user = data.get("user", "Unknown")
        message = f"New sale!\nUser: {user}\nItem: {item}\nPrice: ${price}"
        subject = "Successful Sale Notification"

    sns = boto3.client("sns")
    sns.publish(
        TopicArn=os.environ["SNS_TOPIC_ARN"],
        Message=message,
        Subject=subject,
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"status": "published_to_sns", "subject": subject}),
    }
