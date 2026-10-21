"""
Cylinder Lifecycle 10-State Machine & Transition Validator
Enforces deterministic lifecycle transitions and produces immutable event records.

Prime Invariant #2:
Every physical scan or status transition MUST append an immutable row to cylinder_events
containing cylinder_id, event_type, to_status, to_location_id, actor_user_id, timestamp, and geo_point.
Never update or delete existing history rows.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field


class CylinderStatus(str, Enum):
    PLANT_EMPTY = "PLANT_EMPTY"
    UNDER_INSPECTION = "UNDER_INSPECTION"
    QUARANTINED_DAMAGED = "QUARANTINED_DAMAGED"
    FILLING = "FILLING"
    PLANT_FILLED = "PLANT_FILLED"
    IN_TRANSIT_OUTWARD = "IN_TRANSIT_OUTWARD"
    CUSTOMER_HELD = "CUSTOMER_HELD"
    IN_TRANSIT_INWARD = "IN_TRANSIT_INWARD"
    MAINTENANCE_TESTING = "MAINTENANCE_TESTING"
    SCRAPPED = "SCRAPPED"


class InvalidStateTransitionError(ValueError):
    """Raised when an illegal lifecycle transition is attempted."""
    pass


class ImmutableCylinderEvent(BaseModel):
    cylinder_id: str
    event_type: str
    from_status: Optional[CylinderStatus]
    to_status: CylinderStatus
    from_location_id: Optional[str] = None
    to_location_id: str
    actor_user_id: Optional[str] = None
    scan_device_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    reference_trip_id: Optional[str] = None
    reference_challan_id: Optional[str] = None
    reference_batch_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CylinderStateMachine:
    """Deterministic state machine governing cylinder lifecycle progression."""

    ALLOWED_TRANSITIONS: Dict[CylinderStatus, Set[CylinderStatus]] = {
        CylinderStatus.PLANT_EMPTY: {
            CylinderStatus.UNDER_INSPECTION,
            CylinderStatus.FILLING,
            CylinderStatus.MAINTENANCE_TESTING,
            CylinderStatus.QUARANTINED_DAMAGED,
            CylinderStatus.SCRAPPED,
        },
        CylinderStatus.UNDER_INSPECTION: {
            CylinderStatus.PLANT_EMPTY,
            CylinderStatus.FILLING,
            CylinderStatus.QUARANTINED_DAMAGED,
            CylinderStatus.MAINTENANCE_TESTING,
        },
        CylinderStatus.QUARANTINED_DAMAGED: {
            CylinderStatus.UNDER_INSPECTION,
            CylinderStatus.MAINTENANCE_TESTING,
            CylinderStatus.SCRAPPED,
        },
        CylinderStatus.FILLING: {
            CylinderStatus.PLANT_FILLED,
            CylinderStatus.QUARANTINED_DAMAGED,
            CylinderStatus.PLANT_EMPTY,
        },
        CylinderStatus.PLANT_FILLED: {
            CylinderStatus.IN_TRANSIT_OUTWARD,
            CylinderStatus.QUARANTINED_DAMAGED,
            CylinderStatus.PLANT_EMPTY,
        },
        CylinderStatus.IN_TRANSIT_OUTWARD: {
            CylinderStatus.CUSTOMER_HELD,
            CylinderStatus.PLANT_FILLED,  # Returned upon failed/refused delivery
        },
        CylinderStatus.CUSTOMER_HELD: {
            CylinderStatus.IN_TRANSIT_INWARD,
        },
        CylinderStatus.IN_TRANSIT_INWARD: {
            CylinderStatus.PLANT_EMPTY,
            CylinderStatus.UNDER_INSPECTION,
            CylinderStatus.QUARANTINED_DAMAGED,
        },
        CylinderStatus.MAINTENANCE_TESTING: {
            CylinderStatus.PLANT_EMPTY,
            CylinderStatus.SCRAPPED,
        },
        CylinderStatus.SCRAPPED: set(),  # Terminal state
    }

    @classmethod
    def can_transition(cls, from_status: CylinderStatus, to_status: CylinderStatus) -> bool:
        """Returns True if transition from from_status to to_status is legally permitted."""
        return to_status in cls.ALLOWED_TRANSITIONS.get(from_status, set())

    @classmethod
    def transition(
        cls,
        cylinder_id: str,
        from_status: CylinderStatus,
        to_status: CylinderStatus,
        event_type: str,
        to_location_id: str,
        from_location_id: Optional[str] = None,
        actor_user_id: Optional[str] = None,
        scan_device_id: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        reference_trip_id: Optional[str] = None,
        reference_challan_id: Optional[str] = None,
        reference_batch_id: Optional[str] = None,
    ) -> ImmutableCylinderEvent:
        """
        Validates transition and returns the immutable event ready for insertion into cylinder_events.
        Throws InvalidStateTransitionError if transition is illegal.
        """
        if not cls.can_transition(from_status, to_status):
            raise InvalidStateTransitionError(
                f"Illegal cylinder transition from '{from_status.value}' to '{to_status.value}'. "
                f"Permitted destinations from '{from_status.value}': "
                f"{sorted([s.value for s in cls.ALLOWED_TRANSITIONS.get(from_status, set())])}"
            )

        return ImmutableCylinderEvent(
            cylinder_id=cylinder_id,
            event_type=event_type,
            from_status=from_status,
            to_status=to_status,
            from_location_id=from_location_id,
            to_location_id=to_location_id,
            actor_user_id=actor_user_id,
            scan_device_id=scan_device_id,
            latitude=latitude,
            longitude=longitude,
            reference_trip_id=reference_trip_id,
            reference_challan_id=reference_challan_id,
            reference_batch_id=reference_batch_id,
        )
