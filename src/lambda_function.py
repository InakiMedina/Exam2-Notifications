import json
import os

import boto3

PREWRITTEN_TEST_MESSAGE = """Exam2 — test notification

Hello Inaki,

This is a prewritten test email from the Notification Lambda.
Trigger: POST to the Lambda Function URL.

Sale summary (demo):
  User:  Inaki Medina
  Item:  ITESO Lab Flask
  Price: $15.00

If you received this, SNS + Lambda are working.
"""


def _format_sale_email(data: dict) -> tuple[str, str]:
    folio = data.get("folio", "N/A")
    sale_id = data.get("sale_id", "N/A")
    client_id = data.get("client_id", "N/A")
    total = data.get("total", "0")

    lines = []
    for i, line in enumerate(data.get("contents") or [], start=1):
        pid = line.get("product_id", "?")
        qty = line.get("quantity", "?")
        price = line.get("unit_price", line.get("unit_price", "?"))
        line_total = line.get("line_total", "")
        lines.append(
            f"  Line {i}: product_id={pid} qty={qty} @ {price}"
            + (f" → {line_total}" if line_total != "" else "")
        )
    lines_text = "\n".join(lines) if lines else "  (no line items)"

    message = (
        f"New sale recorded in Sales\n\n"
        f"Sale id:    {sale_id}\n"
        f"Folio:      {folio}\n"
        f"Client id:  {client_id}\n"
        f"Total:      ${total}\n\n"
        f"Contents:\n{lines_text}\n"
    )
    subject = f"Sale notification — {folio}"
    return subject, message


def _payloads_from_event(event) -> list[dict]:
    if isinstance(event, dict) and event.get("Records"):
        out = []
        for record in event["Records"]:
            raw = record.get("body", "{}")
            try:
                out.append(json.loads(raw) if isinstance(raw, str) else raw)
            except json.JSONDecodeError:
                print(f"Invalid SQS body: {raw!r}")
        return out

    if isinstance(event, dict) and "body" in event and event["body"]:
        raw = event["body"]
        data = json.loads(raw) if isinstance(raw, str) else raw
        return [data] if isinstance(data, dict) else []

    if isinstance(event, dict):
        return [event]
    return []


def _publish_one(data: dict) -> tuple[str, str]:
    if data.get("test") is True or data.get("use_prewritten"):
        return "Exam2 Notification — prewritten test", PREWRITTEN_TEST_MESSAGE

    if data.get("event") == "sale_created" or data.get("folio"):
        return _format_sale_email(data)

    item = data.get("item", "N/A")
    price = data.get("price", "0")
    user = data.get("user", "Unknown")
    return (
        "Successful Sale Notification",
        f"New sale!\nUser: {user}\nItem: {item}\nPrice: ${price}",
    )


def lambda_handler(event, context):
    payloads = _payloads_from_event(event)
    if not payloads:
        print(f"No payloads in event: {event}")
        return {"statusCode": 400, "body": json.dumps({"error": "no payload"})}

    sns = boto3.client("sns")
    subjects = []
    for data in payloads:
        subject, message = _publish_one(data)
        sns.publish(
            TopicArn=os.environ["SNS_TOPIC_ARN"],
            Message=message,
            Subject=subject,
        )
        subjects.append(subject)
        print(f"Published to SNS: {subject}")

    return {
        "statusCode": 200,
        "body": json.dumps({"status": "published_to_sns", "count": len(subjects), "subjects": subjects}),
    }
