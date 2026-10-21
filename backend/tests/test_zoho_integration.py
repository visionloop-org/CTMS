"""
Unit tests for Zoho Books Client & Financial Idempotency.
Upholds Prime Invariant #5: Financial Idempotency (Zoho Synchronization).
"""

import pytest
from backend.src.integrations.zoho.books_client import ZohoBooksClient
from backend.src.integrations.zoho.oauth import ZohoOAuthManager


def test_missing_idempotency_key_raises_error():
    """Prime Invariant #5: Every transaction pushed to Zoho must have an Idempotency-Key."""
    client = ZohoBooksClient(base_url="http://localhost:8089", org_id="mock_org")

    with pytest.raises(ValueError) as exc_info:
        client.create_delivery_challan(
            customer_id="cust-101",
            challan_number="DC-2026-001",
            idempotency_key="",  # Missing key
            line_items=[{"item_id": "item-ox", "quantity": 10, "rate": 0}],
        )

    assert "Idempotency-Key is mandatory" in str(exc_info.value)


def test_missing_idempotency_key_invoice_raises_error():
    client = ZohoBooksClient(base_url="http://localhost:8089", org_id="mock_org")

    with pytest.raises(ValueError) as exc_info:
        client.create_sales_invoice(
            customer_id="cust-101",
            invoice_number="INV-2026-001",
            idempotency_key="",
            line_items=[{"item_id": "gas-med-ox", "quantity": 10, "rate": 350}],
        )

    assert "Idempotency-Key is mandatory" in str(exc_info.value)
