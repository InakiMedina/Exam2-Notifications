"""
Send prewritten test email via Lambda Function URL → SNS → inbox.

Requires:
  - Notifications CI applied (Lambda + SNS)
  - SNS subscription confirmed for inaki.medina@gmail.com
  - NOTIFICATION_LAMBDA_URL from: terraform output -raw lambda_function_url

  pytest tests/test_send_prewritten_email.py -v
  # or
  NOTIFICATION_LAMBDA_URL=https://... python tests/test_send_prewritten_email.py
"""

import json
import os
import sys

import pytest
import requests

URL = os.getenv("NOTIFICATION_LAMBDA_URL", "").rstrip("/")


@pytest.mark.skipif(not URL, reason="Set NOTIFICATION_LAMBDA_URL (terraform output lambda_function_url)")
def test_prewritten_email():
    r = requests.post(
        URL,
        json={"test": True},
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("status") == "published_to_sns"


if __name__ == "__main__":
    if not URL:
        print("Set NOTIFICATION_LAMBDA_URL first.", file=sys.stderr)
        sys.exit(1)
    r = requests.post(URL, json={"test": True}, timeout=30)
    print(r.status_code, r.text)
    sys.exit(0 if r.ok else 1)
