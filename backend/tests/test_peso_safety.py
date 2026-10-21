"""
Unit tests for PESO Statutory Safety Validation Engine.
Upholds Prime Invariant #1: PESO & Safety Zero-Tolerance.
"""

from datetime import date, timedelta
import pytest
from backend.src.modules.safety.peso_engine import CylinderSafetyValidator


def test_hydro_test_overdue_rejected_with_403():
    """Overdue cylinder must be rejected with 403 Forbidden (Prime Invariant #1)."""
    today = date(2026, 10, 21)
    overdue_date = date(2026, 10, 20)  # 1 day overdue

    result = CylinderSafetyValidator.validate_prefill_safety(
        cylinder_serial="CYL-OX-47L-009281",
        hydro_test_due_date=overdue_date,
        stamped_tare_kg=52.5,
        measured_tare_kg=52.4,
        certified_gas_type="OXYGEN_MEDICAL",
        batch_gas_type="OXYGEN_MEDICAL",
        current_date=today,
    )

    assert result.allowed is False
    assert result.status_code == 403
    assert "PESO VIOLATION" in result.lockout_reason
    assert result.days_until_hydro_test < 0


def test_hydro_test_valid_passes():
    """Cylinder within valid test interval passes safety check."""
    today = date(2026, 10, 21)
    future_date = date(2028, 5, 10)  # > 1 year remaining

    result = CylinderSafetyValidator.validate_prefill_safety(
        cylinder_serial="CYL-OX-47L-009281",
        hydro_test_due_date=future_date,
        stamped_tare_kg=52.5,
        measured_tare_kg=52.3,
        certified_gas_type="OXYGEN_MEDICAL",
        batch_gas_type="OXYGEN_MEDICAL",
        current_date=today,
    )

    assert result.allowed is True
    assert result.status_code == 200
    assert result.lockout_reason is None
    assert result.warning_message is None
    assert result.days_until_hydro_test > 30


def test_tare_loss_exceeding_5_percent_quarantined():
    """Tare loss > 5.0% must reject with structural failure lockout."""
    today = date(2026, 10, 21)
    future_date = date(2028, 5, 10)

    # Stamped tare: 50.0 kg. Measured tare: 47.0 kg (6% loss)
    result = CylinderSafetyValidator.validate_prefill_safety(
        cylinder_serial="CYL-OX-47L-009282",
        hydro_test_due_date=future_date,
        stamped_tare_kg=50.0,
        measured_tare_kg=47.0,
        certified_gas_type="OXYGEN_INDUSTRIAL",
        batch_gas_type="OXYGEN_INDUSTRIAL",
        current_date=today,
    )

    assert result.allowed is False
    assert result.status_code == 403
    assert "STRUCTURAL INTEGRITY FAILURE" in result.lockout_reason
    assert result.tare_weight_loss_percent == 6.0


def test_gas_type_mismatch_rejected():
    """Attempting to fill cylinder with incompatible gas raises safety error."""
    today = date(2026, 10, 21)
    future_date = date(2028, 5, 10)

    result = CylinderSafetyValidator.validate_prefill_safety(
        cylinder_serial="CYL-OX-47L-009283",
        hydro_test_due_date=future_date,
        stamped_tare_kg=50.0,
        measured_tare_kg=50.0,
        certified_gas_type="OXYGEN_MEDICAL",
        batch_gas_type="ARGON",
        current_date=today,
    )

    assert result.allowed is False
    assert result.status_code == 400
    assert "CROSS-CONTAMINATION RISK" in result.lockout_reason
