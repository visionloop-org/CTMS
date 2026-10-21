"""
Unit tests for Cryptographic API Key Gateway and Native MCP Server.
"""

import pytest
from backend.src.mcp.auth import APIKeyAuthenticator, APIKeyMetadata
from backend.src.mcp.server import CTMNativeMCPServer


def test_api_key_authentication_and_scopes():
    auth = APIKeyAuthenticator()
    raw_key = "ctms_live_77281902847192837482910293847581"
    
    meta = APIKeyMetadata(
        key_id="k-test-1",
        tenant_id="tenant-1",
        key_name="Test Key",
        key_prefix="ctms_live_7728",
        key_hash="",
        allowed_scopes=["cylinders:read", "safety:verify"],
        rate_limit_rpm=100,
    )
    auth.register_key(raw_key, meta)

    # Valid key with permitted scope succeeds
    authed = auth.authenticate(raw_key, required_scope="cylinders:read")
    assert authed.key_id == "k-test-1"

    # Missing scope raises PermissionError
    with pytest.raises(PermissionError):
        auth.authenticate(raw_key, required_scope="billing:write")

    # Invalid token raises ValueError
    with pytest.raises(ValueError):
        auth.authenticate("invalid_token")


def test_mcp_server_tools_and_resources():
    server = CTMNativeMCPServer()

    # Verify tool listing
    tools = server.list_tools()
    tool_names = [t["name"] for t in tools]
    assert "verify_peso_safety" in tool_names
    assert "query_cylinder_passport" in tool_names
    assert "get_customer_holding_audit" in tool_names

    # Test verify_peso_safety tool execution (with valid date)
    call_res = server.call_tool(
        "verify_peso_safety",
        {
            "cylinder_serial": "CYL-0099",
            "hydro_test_due_date": "2029-01-01",
            "stamped_tare_kg": 50.0,
            "measured_tare_kg": 50.0,
        }
    )
    assert call_res["isError"] is False

    # Test verify_peso_safety tool execution (with expired date -> error)
    call_res_expired = server.call_tool(
        "verify_peso_safety",
        {
            "cylinder_serial": "CYL-0099",
            "hydro_test_due_date": "2020-01-01",
            "stamped_tare_kg": 50.0,
        }
    )
    assert call_res_expired["isError"] is True

    # Test resources
    res = server.read_resource("ctms://fleet/live-status")
    assert "total_fleet_size" in res["text"]
