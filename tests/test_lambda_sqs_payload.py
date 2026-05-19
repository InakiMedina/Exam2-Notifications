"""Lambda SQS / SNS body parsing (no AWS)."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lambda_function import _payloads_from_event, _publish_one

pytestmark = pytest.mark.ephemeral


def test_sale_created_sqs_record():
    body = {
        "event": "sale_created",
        "sale_id": 7,
        "folio": "F-001",
        "client_id": 1,
        "total": "106.00",
        "contents": [{"product_id": 100, "quantity": 2, "unit_price": "45.50", "line_total": "91.00"}],
    }
    event = {"Records": [{"body": json.dumps(body)}]}
    payloads = _payloads_from_event(event)
    assert len(payloads) == 1
    subject, message = _publish_one(payloads[0])
    assert subject == "Sale notification — F-001"
    assert "Sale id:    7" in message
    assert "User: Unknown" not in message


def test_sns_wrapped_message():
    inner = {"event": "sale_created", "folio": "F-SNS", "sale_id": 1, "total": "10", "contents": []}
    envelope = {"Type": "Notification", "Message": json.dumps(inner)}
    event = {"Records": [{"body": json.dumps(envelope)}]}
    payloads = _payloads_from_event(event)
    subject, _ = _publish_one(payloads[0])
    assert subject == "Sale notification — F-SNS"


def test_legacy_order_id_payload():
    legacy = {"order_id": "OLD-1", "total": 99.5}
    normalized = _payloads_from_event({"Records": [{"body": json.dumps(legacy)}]})[0]
    subject, message = _publish_one(normalized)
    assert "OLD-1" in subject
    assert "User: Unknown" not in message
