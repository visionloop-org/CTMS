"""
Unit tests for Automated Rental & Holding Calculation Engine.
Upholds Prime Invariant #3: Multi-Ownership Integrity (COC vs POC).
"""

from datetime import datetime, timedelta, timezone
import pytest
from backend.src.modules.rental.calculator import (
    CylinderHoldingRecord,
    CylinderOwnership,
    RentalCalculator,
    RentalSlabTier,
)


def test_poc_cylinder_strictly_zero_rental():
    """Party-Owned Cylinders (POC) must NEVER be charged rental or holding fees (Prime Invariant #3)."""
    now = datetime.now(timezone.utc)
    delivered = now - timedelta(days=90)  # Customer held POC cylinder for 90 days

    poc_record = CylinderHoldingRecord(
        cylinder_id="poc-cyl-001",
        serial_number="POC-OX-8821",
        ownership=CylinderOwnership.POC,
        delivered_at=delivered,
        returned_at=now,
    )

    breakdown = RentalCalculator.calculate_cylinder_rental(poc_record)

    assert breakdown.ownership == CylinderOwnership.POC
    assert breakdown.holding_days == 90
    assert breakdown.billable_days == 0
    assert breakdown.total_rental_inr == 0.00
    assert len(breakdown.daily_slab_charges) == 0


def test_coc_cylinder_progressive_slabs():
    """Company-Owned Cylinders follow contract grace period and progressive rate slabs."""
    now = datetime.now(timezone.utc)
    delivered = now - timedelta(days=40)  # 40 days held

    coc_record = CylinderHoldingRecord(
        cylinder_id="coc-cyl-001",
        serial_number="COC-OX-1102",
        ownership=CylinderOwnership.COC,
        delivered_at=delivered,
        returned_at=now,
    )

    breakdown = RentalCalculator.calculate_cylinder_rental(coc_record)

    assert breakdown.ownership == CylinderOwnership.COC
    assert breakdown.holding_days == 40
    # Days 1-15: ₹0 (15 days grace)
    # Days 16-30: 15 days * ₹10 = ₹150
    # Days 31-40: 10 days * ₹25 = ₹250
    # Total = ₹150 + ₹250 = ₹400
    assert breakdown.billable_days == 25
    assert breakdown.total_rental_inr == 400.00


def test_customer_batch_mixed_fleet():
    """Calculates consolidated customer batch accurately separating POC from COC."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=30)

    cylinders = [
        # 10 COC cylinders held 30 days:
        # Days 1-15: ₹0, Days 16-30: 15 days * ₹10 = ₹150 each -> 10 * ₹150 = ₹1,500
        *[
            CylinderHoldingRecord(
                cylinder_id=f"coc-{i}",
                serial_number=f"COC-{i}",
                ownership=CylinderOwnership.COC,
                delivered_at=start,
                returned_at=now,
            )
            for i in range(10)
        ],
        # 5 POC cylinders held 30 days: ₹0 each
        *[
            CylinderHoldingRecord(
                cylinder_id=f"poc-{i}",
                serial_number=f"POC-{i}",
                ownership=CylinderOwnership.POC,
                delivered_at=start,
                returned_at=now,
            )
            for i in range(5)
        ],
    ]

    summary = RentalCalculator.calculate_customer_batch(
        customer_id="cust-apex-hospitals",
        cylinders=cylinders,
        period_start=start,
        period_end=now,
    )

    assert summary.total_coc_cylinders == 10
    assert summary.total_poc_cylinders == 5
    assert summary.subtotal_inr == 1500.00
    assert summary.gst_amount_inr == 270.00  # 18% of 1500
    assert summary.total_payable_inr == 1770.00
