"""
PESO Statutory Safety Validation Engine
Enforces Indian Gas Cylinder Rules, 2016 and PESO statutory safety interlocks.

Prime Invariant #1:
Under no circumstances may a cylinder overdue for hydrostatic stretch testing
(CurrentDate >= hydro_test_due_date) be assigned to a filling batch or marked as PLANT_FILLED.
Any API or UI flow attempting to bypass this rule must return an explicit 403 FORBIDDEN.
"""

from datetime import date, datetime
from typing import Optional, Tuple
from pydantic import BaseModel, Field


class SafetyCheckResult(BaseModel):
    allowed: bool
    status_code: int = 200
    lockout_reason: Optional[str] = None
    warning_message: Optional[str] = None
    days_until_hydro_test: int
    tare_weight_loss_percent: float = 0.0


class CylinderSafetyValidator:
    """Validates pre-fill safety parameters according to PESO standards."""

    MAX_TARE_LOSS_PERCENT: float = 5.0
    WARNING_DAYS_THRESHOLD: int = 30

    @classmethod
    def validate_prefill_safety(
        cls,
        cylinder_serial: str,
        hydro_test_due_date: date,
        stamped_tare_kg: float,
        measured_tare_kg: Optional[float] = None,
        certified_gas_type: Optional[str] = None,
        batch_gas_type: Optional[str] = None,
        current_date: Optional[date] = None,
    ) -> SafetyCheckResult:
        """
        Validates whether a cylinder can be accepted for refilling.
        Returns SafetyCheckResult with allowed=False and HTTP 403 status code if violated.
        """
        if current_date is None:
            current_date = date.today()

        days_remaining = (hydro_test_due_date - current_date).days

        # 1. PESO Hydrostatic Stretch Test Overdue Check (Prime Invariant #1)
        if days_remaining <= 0:
            return SafetyCheckResult(
                allowed=False,
                status_code=403,
                lockout_reason=(
                    f"PESO VIOLATION: Cylinder {cylinder_serial} is OVERDUE for hydrostatic test. "
                    f"Due date was {hydro_test_due_date.isoformat()} ({abs(days_remaining)} days overdue). "
                    "Filling is strictly prohibited."
                ),
                days_until_hydro_test=days_remaining,
            )

        # 2. Gas Compatibility Check
        if certified_gas_type and batch_gas_type and certified_gas_type != batch_gas_type:
            return SafetyCheckResult(
                allowed=False,
                status_code=400,
                lockout_reason=(
                    f"CROSS-CONTAMINATION RISK: Cylinder {cylinder_serial} is certified for {certified_gas_type}, "
                    f"cannot be filled with {batch_gas_type} without de-valving, statutory purging, and recertification."
                ),
                days_until_hydro_test=days_remaining,
            )

        # 3. Tare Weight Loss Threshold Check (Max 5.0% wall loss)
        tare_loss_percent = 0.0
        if measured_tare_kg is not None and stamped_tare_kg > 0:
            if measured_tare_kg < stamped_tare_kg:
                tare_loss_percent = round(
                    ((stamped_tare_kg - measured_tare_kg) / stamped_tare_kg) * 100.0, 2
                )
                if tare_loss_percent > cls.MAX_TARE_LOSS_PERCENT:
                    return SafetyCheckResult(
                        allowed=False,
                        status_code=403,
                        lockout_reason=(
                            f"STRUCTURAL INTEGRITY FAILURE: Measured tare weight {measured_tare_kg}kg "
                            f"is {tare_loss_percent}% below stamped weight {stamped_tare_kg}kg "
                            f"(limit {cls.MAX_TARE_LOSS_PERCENT}%). Cylinder must be quarantined for ultrasonic wall test."
                        ),
                        days_until_hydro_test=days_remaining,
                        tare_weight_loss_percent=tare_loss_percent,
                    )

        # 4. Approaching Expiry Warning (Within 30 days)
        warning_msg = None
        if days_remaining <= cls.WARNING_DAYS_THRESHOLD:
            warning_msg = (
                f"SAFETY WARNING: Hydrostatic test due in {days_remaining} days ({hydro_test_due_date.isoformat()}). "
                "Schedule testing upon return."
            )

        return SafetyCheckResult(
            allowed=True,
            status_code=200,
            warning_message=warning_msg,
            days_until_hydro_test=days_remaining,
            tare_weight_loss_percent=tare_loss_percent,
        )
