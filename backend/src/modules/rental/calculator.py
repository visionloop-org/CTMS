"""
Automated Rental & Holding Calculation Engine
Enforces multi-tier progressive slabs and multi-ownership integrity.

Prime Invariant #3:
Party-Owned Cylinders (POC) must NEVER be charged rental or holding fees.
Company-Owned Cylinders (COC) are subject to rental slabs only after the customer's
agreed grace period expires.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import ceil
from typing import List, Optional
from pydantic import BaseModel


class CylinderOwnership(str, Enum):
    COC = "COC"  # Company Owned Cylinder
    POC = "POC"  # Party Owned Cylinder
    VOC = "VOC"  # Vendor Owned Cylinder


class RentalSlabTier(BaseModel):
    from_day: int
    to_day: Optional[int] = None  # None indicates infinity
    daily_rate_inr: float


@dataclass
class CylinderHoldingRecord:
    cylinder_id: str
    serial_number: str
    ownership: CylinderOwnership
    delivered_at: datetime
    returned_at: Optional[datetime] = None  # None if still held


@dataclass
class CylinderRentalBreakdown:
    cylinder_id: str
    serial_number: str
    ownership: CylinderOwnership
    holding_days: int
    grace_days_applied: int
    billable_days: int
    daily_slab_charges: List[dict]
    total_rental_inr: float


@dataclass
class CustomerRentalSummary:
    customer_id: str
    billing_period_start: datetime
    billing_period_end: datetime
    total_coc_cylinders: int
    total_poc_cylinders: int
    subtotal_inr: float
    gst_percent: float = 18.0
    gst_amount_inr: float = 0.0
    total_payable_inr: float = 0.0
    cylinder_breakdowns: List[CylinderRentalBreakdown] = field(default_factory=list)


class RentalCalculator:
    """Calculates progressive cylinder holding fees and enforces POC zero-rental rule."""

    DEFAULT_SLABS: List[RentalSlabTier] = [
        RentalSlabTier(from_day=1, to_day=15, daily_rate_inr=0.0),    # Grace period
        RentalSlabTier(from_day=16, to_day=30, daily_rate_inr=10.0),  # Base tier
        RentalSlabTier(from_day=31, to_day=60, daily_rate_inr=25.0),  # Penalty tier
        RentalSlabTier(from_day=61, to_day=None, daily_rate_inr=50.0), # Deterrent tier
    ]

    @classmethod
    def calculate_holding_days(
        cls, delivered_at: datetime, returned_at: Optional[datetime] = None
    ) -> int:
        """Returns elapsed calendar holding days, ceiling to full day."""
        if returned_at is None:
            returned_at = datetime.now(timezone.utc)
            
        elapsed_seconds = (returned_at - delivered_at).total_seconds()
        if elapsed_seconds <= 0:
            return 0
        return ceil(elapsed_seconds / 86400.0)

    @classmethod
    def calculate_cylinder_rental(
        cls,
        cylinder: CylinderHoldingRecord,
        slabs: Optional[List[RentalSlabTier]] = None,
        grace_days: int = 15,
        as_of_date: Optional[datetime] = None,
    ) -> CylinderRentalBreakdown:
        """
        Calculates rental charge for a single cylinder.
        Enforces Prime Rule #3: POC cylinders ALWAYS evaluate to 0 INR.
        """
        holding_days = cls.calculate_holding_days(
            cylinder.delivered_at, cylinder.returned_at or as_of_date
        )

        # PRIME RULE #3: Party-Owned Cylinders (POC) are strictly EXEMPT from rent
        if cylinder.ownership == CylinderOwnership.POC:
            return CylinderRentalBreakdown(
                cylinder_id=cylinder.cylinder_id,
                serial_number=cylinder.serial_number,
                ownership=CylinderOwnership.POC,
                holding_days=holding_days,
                grace_days_applied=holding_days,
                billable_days=0,
                daily_slab_charges=[],
                total_rental_inr=0.0,
            )

        active_slabs = slabs if slabs is not None else cls.DEFAULT_SLABS
        sorted_slabs = sorted(active_slabs, key=lambda s: s.from_day)

        total_fee = 0.0
        daily_breakdowns = []
        billable_days = 0

        for day in range(1, holding_days + 1):
            day_rate = 0.0
            matched_tier = None
            for slab in sorted_slabs:
                if day >= slab.from_day and (slab.to_day is None or day <= slab.to_day):
                    day_rate = slab.daily_rate_inr
                    matched_tier = slab
                    break

            if day_rate > 0.0:
                billable_days += 1
                total_fee += day_rate
                daily_breakdowns.append({
                    "day": day,
                    "rate_inr": day_rate,
                    "slab_from": matched_tier.from_day if matched_tier else None,
                    "slab_to": matched_tier.to_day if matched_tier else None,
                })

        return CylinderRentalBreakdown(
            cylinder_id=cylinder.cylinder_id,
            serial_number=cylinder.serial_number,
            ownership=cylinder.ownership,
            holding_days=holding_days,
            grace_days_applied=holding_days - billable_days,
            billable_days=billable_days,
            daily_slab_charges=daily_breakdowns,
            total_rental_inr=round(total_fee, 2),
        )

    @classmethod
    def calculate_customer_batch(
        cls,
        customer_id: str,
        cylinders: List[CylinderHoldingRecord],
        period_start: datetime,
        period_end: datetime,
        slabs: Optional[List[RentalSlabTier]] = None,
        gst_percent: float = 18.0,
    ) -> CustomerRentalSummary:
        """Calculates consolidated monthly holding charges for a customer fleet."""
        breakdowns = []
        subtotal = 0.0
        coc_count = 0
        poc_count = 0

        for cyl in cylinders:
            if cyl.ownership == CylinderOwnership.POC:
                poc_count += 1
            else:
                coc_count += 1

            bd = cls.calculate_cylinder_rental(
                cylinder=cyl,
                slabs=slabs,
                as_of_date=period_end,
            )
            breakdowns.append(bd)
            subtotal += bd.total_rental_inr

        gst_amount = round((subtotal * gst_percent) / 100.0, 2)
        total_payable = round(subtotal + gst_amount, 2)

        return CustomerRentalSummary(
            customer_id=customer_id,
            billing_period_start=period_start,
            billing_period_end=period_end,
            total_coc_cylinders=coc_count,
            total_poc_cylinders=poc_count,
            subtotal_inr=round(subtotal, 2),
            gst_percent=gst_percent,
            gst_amount_inr=gst_amount,
            total_payable_inr=total_payable,
            cylinder_breakdowns=breakdowns,
        )
