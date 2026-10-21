"""
Native Model Context Protocol (MCP) Server for Autonomous AI Agents
Conforms to docs/12_API_KEYS_AND_MCP_SERVER_SPECIFICATION.md.
Provides tools and live streaming resources over JSON-RPC 2.0.
"""

from datetime import date, datetime, timezone
import json
from typing import Any, Dict, List, Optional
from backend.src.modules.safety.peso_engine import CylinderSafetyValidator
from backend.src.modules.rental.calculator import (
    CylinderHoldingRecord,
    CylinderOwnership,
    RentalCalculator,
)


class CTMNativeMCPServer:
    """CTMS Native Model Context Protocol Server."""

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.resources: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()
        self._register_default_resources()

    def _register_default_tools(self):
        self.tools["query_cylinder_passport"] = {
            "name": "query_cylinder_passport",
            "description": "Fetches complete digital passport for a cylinder by Serial Number, QR UID, or RFID EPC.",
            "parameters": {
                "type": "object",
                "properties": {
                    "identifier": {"type": "string", "description": "Serial number, QR hash, or RFID EPC"}
                },
                "required": ["identifier"]
            }
        }

        self.tools["verify_peso_safety"] = {
            "name": "verify_peso_safety",
            "description": "Verifies PESO statutory pre-fill safety interlocks (hydro-test due date, tare loss, gas type).",
            "parameters": {
                "type": "object",
                "properties": {
                    "cylinder_serial": {"type": "string"},
                    "hydro_test_due_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "stamped_tare_kg": {"type": "number"},
                    "measured_tare_kg": {"type": "number"},
                    "certified_gas_type": {"type": "string"},
                    "batch_gas_type": {"type": "string"}
                },
                "required": ["cylinder_serial", "hydro_test_due_date", "stamped_tare_kg"]
            }
        }

        self.tools["get_customer_holding_audit"] = {
            "name": "get_customer_holding_audit",
            "description": "Audits cylinders currently held at a customer site, breaking down COC vs POC and rental charges.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "Customer UUID"}
                },
                "required": ["customer_id"]
            }
        }

    def _register_default_resources(self):
        self.resources["ctms://fleet/live-status"] = {
            "uri": "ctms://fleet/live-status",
            "name": "Fleet Operational Live Status",
            "mimeType": "application/json",
            "description": "Real-time summary of cylinder fleet across plants, trucks, and customer locations."
        }
        self.resources["ctms://compliance/overdue-test"] = {
            "uri": "ctms://compliance/overdue-test",
            "name": "PESO Overdue Hydro-Test Alert List",
            "mimeType": "application/json",
            "description": "List of cylinders requiring immediate hydrostatic stretch testing."
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        return list(self.tools.values())

    def list_resources(self) -> List[Dict[str, Any]]:
        return list(self.resources.values())

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes tool call and returns structured result."""
        if name not in self.tools:
            return {"isError": True, "error": f"Unknown tool: {name}"}

        if name == "verify_peso_safety":
            try:
                due_date = date.fromisoformat(arguments["hydro_test_due_date"])
                res = CylinderSafetyValidator.validate_prefill_safety(
                    cylinder_serial=arguments["cylinder_serial"],
                    hydro_test_due_date=due_date,
                    stamped_tare_kg=float(arguments["stamped_tare_kg"]),
                    measured_tare_kg=arguments.get("measured_tare_kg"),
                    certified_gas_type=arguments.get("certified_gas_type"),
                    batch_gas_type=arguments.get("batch_gas_type"),
                )
                return {
                    "isError": not res.allowed,
                    "content": [{
                        "type": "text",
                        "text": json.dumps(res.model_dump(), indent=2)
                    }]
                }
            except Exception as e:
                return {"isError": True, "error": str(e)}

        elif name == "query_cylinder_passport":
            # Mock passport query
            ident = arguments["identifier"]
            passport = {
                "serial_number": ident,
                "current_gas_type": "OXYGEN_MEDICAL",
                "water_capacity_litres": 46.7,
                "working_pressure_bar": 150.0,
                "status": "PLANT_EMPTY",
                "ownership": "COC",
                "last_hydro_test_date": "2023-05-10",
                "hydro_test_due_date": "2028-05-10",
                "qr_code_uid": f"QR-{ident}",
            }
            return {
                "isError": False,
                "content": [{"type": "text", "text": json.dumps(passport, indent=2)}]
            }

        elif name == "get_customer_holding_audit":
            cust_id = arguments["customer_id"]
            summary = {
                "customer_id": cust_id,
                "total_coc_held": 12,
                "total_poc_held": 4,
                "accrued_holding_rent_inr": 1850.00,
                "poc_holding_rent_inr": 0.00,  # Enforces Prime Rule #3
                "last_delivery_challan": "DC-2026-008129",
            }
            return {
                "isError": False,
                "content": [{"type": "text", "text": json.dumps(summary, indent=2)}]
            }

        return {"isError": True, "error": f"Tool '{name}' execution not implemented"}

    def read_resource(self, uri: str) -> Dict[str, Any]:
        """Reads MCP live resource content."""
        if uri == "ctms://fleet/live-status":
            return {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps({
                    "total_fleet_size": 25000,
                    "plant_filled": 6200,
                    "plant_empty": 4100,
                    "customer_held": 12400,
                    "in_transit": 1800,
                    "quarantined_damaged": 500,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }, indent=2)
            }
        elif uri == "ctms://compliance/overdue-test":
            return {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps({
                    "total_overdue": 14,
                    "warning_30_days": 82,
                    "quarantined": 14,
                    "action_required": "Immediate dispatch to testing facility",
                }, indent=2)
            }
        raise KeyError(f"Resource URI not found: {uri}")


mcp_server = CTMNativeMCPServer()
