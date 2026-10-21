"""
Unit tests for 10-State Cylinder Lifecycle Machine.
Upholds Prime Invariant #2: Immutable Scan Audit Trail.
"""

import pytest
from backend.src.modules.lifecycle.state_machine import (
    CylinderStateMachine,
    CylinderStatus,
    InvalidStateTransitionError,
)


def test_valid_lifecycle_progression():
    """Valid transitions succeed and return complete immutable events."""
    event = CylinderStateMachine.transition(
        cylinder_id="cyl-uuid-001",
        from_status=CylinderStatus.PLANT_EMPTY,
        to_status=CylinderStatus.FILLING,
        event_type="BATCH_FILLING_START",
        to_location_id="plant-manifold-bay-1",
        actor_user_id="operator-123",
    )

    assert event.cylinder_id == "cyl-uuid-001"
    assert event.from_status == CylinderStatus.PLANT_EMPTY
    assert event.to_status == CylinderStatus.FILLING
    assert event.to_location_id == "plant-manifold-bay-1"
    assert event.timestamp is not None


def test_illegal_jump_throws_error():
    """Skipping necessary operational steps (e.g. PLANT_EMPTY directly to CUSTOMER_HELD) is forbidden."""
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        CylinderStateMachine.transition(
            cylinder_id="cyl-uuid-002",
            from_status=CylinderStatus.PLANT_EMPTY,
            to_status=CylinderStatus.CUSTOMER_HELD,
            event_type="ILLEGAL_DELIVERY",
            to_location_id="customer-site-xyz",
        )

    assert "Illegal cylinder transition" in str(exc_info.value)


def test_scrapped_is_terminal():
    """Scrapped cylinders cannot transition back into operational use."""
    assert len(CylinderStateMachine.ALLOWED_TRANSITIONS[CylinderStatus.SCRAPPED]) == 0
    with pytest.raises(InvalidStateTransitionError):
        CylinderStateMachine.transition(
            cylinder_id="cyl-uuid-003",
            from_status=CylinderStatus.SCRAPPED,
            to_status=CylinderStatus.PLANT_EMPTY,
            event_type="ATTEMPTED_REVIVAL",
            to_location_id="plant-yard",
        )
