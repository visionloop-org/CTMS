"""
CTMS Core API Routes
Provides endpoints for PESO safety check, state transitions, rental calculations, and Zoho sync.
"""

from datetime import date
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel

from backend.src.modules.safety.peso_engine import CylinderSafetyValidator, SafetyCheckResult
from backend.src.modules.lifecycle.state_machine import (
    CylinderStateMachine,
    CylinderStatus,
    ImmutableCylinderEvent,
    InvalidStateTransitionError,
)
from backend.src.modules.rental.calculator import (
    CylinderHoldingRecord,
    CylinderOwnership,
    RentalCalculator,
    RentalSlabTier,
)
from backend.src.integrations.zoho.books_client import ZohoBooksClient
from backend.src.mcp.auth import api_key_auth
from backend.src.mcp.server import mcp_server

router = APIRouter()
books_client = ZohoBooksClient()


# Dependency for API key authentication
def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )
    try:
        return api_key_auth.authenticate(x_api_key)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


class PreFillCheckRequest(BaseModel):
    cylinder_serial: str
    hydro_test_due_date: date
    stamped_tare_kg: float
    measured_tare_kg: Optional[float] = None
    certified_gas_type: Optional[str] = None
    batch_gas_type: Optional[str] = None


class StateTransitionRequest(BaseModel):
    cylinder_id: str
    from_status: CylinderStatus
    to_status: CylinderStatus
    event_type: str
    to_location_id: str
    from_location_id: Optional[str] = None
    actor_user_id: Optional[str] = None
    scan_device_id: Optional[str] = None


class RentalCalcRequest(BaseModel):
    cylinder_id: str
    serial_number: str
    ownership: CylinderOwnership
    holding_days: int
    grace_days: int = 15


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CTMS Enterprise API",
        "version": "1.0.0",
        "compliance": "PESO Gas Cylinder Rules 2016 Compliant",
    }


@router.post("/api/v1/filling/pre-check", response_model=SafetyCheckResult)
def pre_fill_safety_check(req: PreFillCheckRequest):
    """
    Validates pre-fill safety.
    Prime Invariant #1: Returns 403 Forbidden if overdue for hydrostatic test.
    """
    result = CylinderSafetyValidator.validate_prefill_safety(
        cylinder_serial=req.cylinder_serial,
        hydro_test_due_date=req.hydro_test_due_date,
        stamped_tare_kg=req.stamped_tare_kg,
        measured_tare_kg=req.measured_tare_kg,
        certified_gas_type=req.certified_gas_type,
        batch_gas_type=req.batch_gas_type,
    )
    if not result.allowed:
        raise HTTPException(
            status_code=result.status_code,
            detail=result.model_dump(),
        )
    return result


@router.post("/api/v1/cylinders/transition", response_model=ImmutableCylinderEvent)
def transition_cylinder_state(req: StateTransitionRequest):
    """
    Transitions cylinder state and returns the immutable scan ledger event.
    """
    try:
        event = CylinderStateMachine.transition(
            cylinder_id=req.cylinder_id,
            from_status=req.from_status,
            to_status=req.to_status,
            event_type=req.event_type,
            to_location_id=req.to_location_id,
            from_location_id=req.from_location_id,
            actor_user_id=req.actor_user_id,
            scan_device_id=req.scan_device_id,
        )
        return event
    except InvalidStateTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.post("/api/v1/rental/calculate-single")
def calculate_single_cylinder_rent(req: RentalCalcRequest):
    """
    Calculates progressive holding rental.
    Prime Invariant #3: Returns 0 rent for POC cylinders.
    """
    from datetime import datetime, timedelta, timezone

    # Simulate delivered_at based on holding days
    now = datetime.now(timezone.utc)
    delivered_at = now - timedelta(days=req.holding_days)

    record = CylinderHoldingRecord(
        cylinder_id=req.cylinder_id,
        serial_number=req.serial_number,
        ownership=req.ownership,
        delivered_at=delivered_at,
        returned_at=now,
    )

    breakdown = RentalCalculator.calculate_cylinder_rental(
        cylinder=record,
        grace_days=req.grace_days,
    )
    return breakdown


# MCP Native Endpoints
@router.get("/mcp/tools")
def list_mcp_tools():
    return {"tools": mcp_server.list_tools()}


@router.get("/mcp/resources")
def list_mcp_resources():
    return {"resources": mcp_server.list_resources()}


@router.post("/mcp/call")
def call_mcp_tool(payload: Dict[str, Any]):
    tool_name = payload.get("name")
    arguments = payload.get("arguments", {})
    return mcp_server.call_tool(tool_name, arguments)
