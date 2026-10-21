---
name: mcp-gateway-engine
description: Guides the implementation, debugging, and testing of the Model Context Protocol (MCP) server and cryptographic API key gateway for external AI agents and partner applications.
---

# Model Context Protocol (MCP) & API Gateway Runbook

## Overview
This skill provides runbooks and integration protocols for running, testing, and verifying the **CTMS MCP Server** and the **Cryptographic API Key Gateway**.

---

## 1. Running the MCP Server Locally

The CTMS MCP Server can be executed via Standard I/O (stdio) for local development or via Server-Sent Events (SSE) for remote agents:

### 1.1 Local Stdio Transport
```bash
# Start local MCP server
python3 -m ctms.mcp_server --transport stdio --api-key ctms_live_test_key_here
```

### 1.2 Remote SSE Transport
```bash
# Start FastAPI server with MCP SSE endpoint at /mcp/sse
uvicorn ctms.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 2. MCP Tools Testing Matrix

| Tool Name | Test Command / Payload | Expected Output |
| :--- | :--- | :--- |
| `query_cylinder_passport` | `{"identifier": "OX-47-0912"}` | Full JSON passport containing tare weight, gas type, hydro due date, and holding status. |
| `verify_peso_safety` | `{"cylinder_id": "cyl-123", "target_gas": "OXYGEN_MEDICAL"}` | `{"status": "APPROVED"}` or `{"status": "BLOCKED", "reason": "HYDRO_TEST_OVERDUE"}` |
| `get_customer_holding_audit`| `{"customer_id": "cust-456"}` | Holding duration breakdown, billable cylinder-days, and unbilled rental fee. |
| `trace_batch_contamination` | `{"batch_number": "MED-OX-20261021-01"}` | Graph traversal returning all customer locations holding cylinders from the batch. |
| `reconcile_trip_manifest` | `{"trip_id": "trip-789"}` | Truck load vs delivered & returned count delta. |

---

## 3. API Key Validation & Rate Limiting

### 3.1 Key Generation Standard
- Format: `ctms_live_<32_hex_chars>`
- Hash algorithm: SHA-256 (`hashlib.sha256(raw_key.encode()).hexdigest()`)
- Storage: In table `tenant_api_keys(key_hash, scopes, rate_limit_per_minute)`

### 3.2 Testing Rate Limiter (Redis Leaky-Bucket)
```bash
# Test rate limiter by firing 305 requests rapidly
for i in {1..305}; do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/v1/cylinders/live-status \
    -H "X-API-Key: ctms_live_test_key"
done
# First 300 requests return 200 OK; request 301+ returns 429 Too Many Requests
```
