# API Key Gateway & Model Context Protocol (MCP) Specification
## External Developer APIs, Cryptographic Key Management & AI Agent Integration

---

## 1. Executive Summary & Integration Architecture

To enable third-party systems (Hospital HMIS, ERPs like SAP/Oracle, logistics tracking platforms) and **autonomous AI agents** (Antigravity, Claude Desktop, Cursor, Gemini CLI) to securely interact with the Cylinder Tracking Management System, the platform exposes two dedicated interfaces:

1. **Cryptographic API Key Gateway:** High-performance REST interface authenticated via scoped, rate-limited Bearer API keys (`X-API-Key`).
2. **Native Model Context Protocol (MCP) Server:** Standardized interface implementing the open **Anthropic/Model Context Protocol (MCP)** specification over Server-Sent Events (SSE) and stdio, providing AI agents with structured tools and live resources.

```
+--------------------------------------------------------------------------------------------------+
|                                    EXTERNAL CONSUMERS & AGENTS                                   |
+--------------------------------------------------------------------------------------------------+
|  Partner ERPs & Hospital HMIS        External Mobile / Web Apps         Autonomous AI Agents     |
|  (SAP, Oracle, Custom Apps)          (Distributor Portals)             (Claude, Gemini, AGY)     |
+---------------------+-------------------------------+-----------------------------+--------------+
                      |                               |                             |
                      | HTTPS REST (`X-API-Key`)      | HTTPS REST (`X-API-Key`)    | MCP JSON-RPC 
                      |                               |                             | (SSE / stdio)
                      v                               v                             v
+--------------------------------------------------------------------------------------------------+
|                                 CTMS EXTERNAL INTEGRATION GATEWAY                                |
|  +-------------------------------------------------------+  +----------------------------------+ |
|  | Cryptographic API Key Authenticator                   |  | Native MCP Server                | |
|  | • SHA-256 Key Hashing & Tenant Scoping                |  | • Tool Registry & Dispatcher     | |
|  | • Fine-Grained Permissions (RBAC Scopes)              |  | • Live Resource URI Provider     | |
|  | • Redis Leaky-Bucket Rate Limiter (Per-Key Quotas)    |  | • Human-in-the-Loop Safety Locks | |
|  | • Real-Time Usage Analytics & Latency Logging         |  | • Context Compaction Protocol    | |
|  +-------------------------------------------------------+  +----------------------------------+ |
+--------------------------------------------------------------------------------------------------+
                                                 │
                                                 ▼
+--------------------------------------------------------------------------------------------------+
|                                      CTMS CORE BACKEND & ENGINES                                 |
|  • Cylinder State Machine   • PESO Safety Validator   • Timescale Event Log   • Zoho Gateway     |
+--------------------------------------------------------------------------------------------------+
```

---

## 2. API Key Management Architecture

### 2.1 Cryptographic Storage & Format
API Keys are generated using high-entropy cryptographically secure random bytes:
- **Key Format:** `ctms_live_<32_hex_characters>` (e.g. `ctms_live_a8f9c10293b4819d028193847291a82f`)
- **Storage Standard:** The raw key is displayed to the administrator **only once** upon creation. The database stores only the **SHA-256 hash** (`api_key_hash`) along with key metadata.
- **Header Transmission:** `X-API-Key: ctms_live_...` or `Authorization: Bearer ctms_live_...`

### 2.2 Relational Schema (`tenant_api_keys`)
```sql
CREATE TABLE tenant_api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    key_name VARCHAR(128) NOT NULL,                     -- e.g. "Apex Hospital HMIS Integration"
    key_prefix VARCHAR(16) NOT NULL,                    -- e.g. "ctms_live_a8f9..." for identification
    key_hash VARCHAR(64) NOT NULL UNIQUE,               -- SHA-256 hash of the full token
    
    -- Scopes & Granular Permissions
    scopes TEXT[] NOT NULL DEFAULT ARRAY['cylinders:read'],
    allowed_ips CIDR[] DEFAULT NULL,                    -- Optional IP Whitelist restriction
    
    -- Rate Limiting & Lifecycle
    rate_limit_per_minute INT NOT NULL DEFAULT 300,
    expires_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    created_by_user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_api_key_lookup ON tenant_api_keys(key_hash, is_active);
```

### 2.3 Supported API Key Scopes
- `cylinders:read`: Lookup cylinder location, tare weight, gas type, and hydro test dates.
- `cylinders:write`: Register new cylinders, update collar codes, report damaged tags.
- `filling:check`: Execute pre-fill safety validations (overdue check, tare verification).
- `dispatch:read`: View trip manifests, gate-passes, and vehicle loading status.
- `dispatch:write`: Create delivery challans (e-DC) and submit digital Proof of Delivery (POD).
- `rental:read`: Retrieve customer holding statements, unbilled days, and deposit ledgers.
- `zoho:sync`: Trigger manual sync or inspect invoice dispatch status in Zoho Books.

---

## 3. Model Context Protocol (MCP) Server Specification

The CTMS MCP Server allows external AI agents to act as intelligent assistants for operations managers, logistics dispatchers, and compliance auditors.

### 3.1 MCP Server Architecture
- **Transport Modes:**
  1. **Server-Sent Events (SSE):** `https://api.ctmsgas.com/mcp/sse` (For web/remote AI agents).
  2. **Standard I/O (stdio):** Local process execution (`python -m ctms.mcp_server`) for desktop AI tools (Claude Desktop, Cursor).
- **Authentication:** Authenticates using tenant API keys (`ctms_live_...`).

---

### 3.2 Registered MCP Tools for AI Agents

```
+---------------------------------------------------------------------------------------------------+
| Tool Name                   | Input Schema (Arguments)     | Description & Output                 |
+-----------------------------+------------------------------+--------------------------------------+
| `query_cylinder_passport`   | `{ serial_or_qr: string }`   | Full 360° lifecycle passport: tare,  |
|                             |                              | gas type, owner, status, hydro due.  |
+-----------------------------+------------------------------+--------------------------------------+
| `verify_peso_safety`        | `{ cylinder_id: string,      | Executes pre-fill safety interlock.  |
|                             |    target_gas: string }`     | Returns PASS/FAIL with penalty codes.|
+-----------------------------+------------------------------+--------------------------------------+
| `get_customer_holding_audit`| `{ customer_id: string }`    | Days held, billable cylinder-days,   |
|                             |                              | active deposit, unbilled rent INR.   |
+-----------------------------+------------------------------+--------------------------------------+
| `trace_batch_contamination` | `{ batch_number: string }`   | Graph traversal finding all hospital |
|                             |                              | wards holding defective cylinders.   |
+-----------------------------+------------------------------+--------------------------------------+
| `reconcile_trip_manifest`   | `{ trip_id: string }`        | Compares outward dispatch against    |
|                             |                              | delivered & empties; detects delta.  |
+-----------------------------+------------------------------+--------------------------------------+
| `trigger_zoho_books_sync`   | `{ challan_id: string }`     | Enqueues delivery challan to Zoho    |
|                             |                              | Books with idempotency key.          |
+---------------------------------------------------------------------------------------------------+
```

#### Detailed Tool Schema Example: `query_cylinder_passport`
```json
{
  "name": "query_cylinder_passport",
  "description": "Retrieve complete operational and safety passport for any high-pressure gas cylinder by serial number, QR hash, or RFID EPC.",
  "parameters": {
    "type": "object",
    "properties": {
      "identifier": {
        "type": "string",
        "description": "Stamped metal serial number (e.g. 'OX-47-0912'), QR code UID, or RFID EPC."
      }
    },
    "required": ["identifier"]
  }
}
```

#### Tool Response Example:
```json
{
  "cylinder_id": "908a71b2-1849-41a2-b882-990184291842",
  "serial_number": "OX-47-0912",
  "ownership": "COC (Company Owned)",
  "current_gas_type": "OXYGEN_MEDICAL",
  "status": "CUSTOMER_HELD",
  "current_custodian": "Apex Memorial Hospital (Zoho Contact: 982000000184291)",
  "holding_since": "2026-10-18T10:14:00Z",
  "holding_days_elapsed": 3,
  "contract_grace_days": 15,
  "accrued_rental_inr": 0.0,
  "peso_compliance": {
    "specification": "IS 7285 / Seamless Steel",
    "stamped_tare_weight_kg": 52.4,
    "last_hydro_test_date": "2023-04-10",
    "hydro_test_due_date": "2028-04-10",
    "days_until_hydro_due": 536,
    "is_test_valid": true
  }
}
```

---

### 3.3 Live MCP Resources for AI Context
AI agents can subscribe to read-only URI resources for real-time situational awareness:

| Resource URI | Description & Context Provided |
| :--- | :--- |
| `ctms://fleet/live-status` | Real-time counts of fleet by state (`PLANT_FILLED`, `CUSTOMER_HELD`, `QUARANTINED`). |
| `ctms://compliance/overdue-test` | Streaming list of all cylinders approaching or past PESO test due dates. |
| `ctms://logistics/active-trips` | Active vehicle manifests, driver locations, and delivery completion percentages. |
| `ctms://zoho/sync-health` | BullMQ/Celery outbox queue depth, last synced invoice ID, and error retry count. |

---

## 4. Rate Limiting, Throttling & Security Governance

```
+--------------------------------------------------------------------------------------------------+
|                                    GATEWAY SECURITY PIPELINE                                     |
+--------------------------------------------------------------------------------------------------+
|  1. TLS 1.3 Handshake                                                                            |
|  2. IP Whitelist Validation (Optional per API key)                                               |
|  3. Redis Leaky-Bucket Rate Limiter:                                                             |
|     - Default Tier: 300 requests / minute                                                        |
|     - Enterprise Tier: 1,200 requests / minute                                                   |
|  4. Scope Verification (`has_scope('dispatch:write')`)                                           |
|  5. Tenant RLS Isolation: Inject `current_tenant_id` into all DB queries                          |
|  6. Telemetry Logger: Latency, Endpoint, Response Code, Tokens consumed                          |
+--------------------------------------------------------------------------------------------------+
```

### Response Headers on API Key Requests:
```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 284
X-RateLimit-Reset: 1729512000
Content-Type: application/json; charset=utf-8
```
