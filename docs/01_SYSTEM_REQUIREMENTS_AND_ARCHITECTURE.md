# System Architecture & Technical Specifications
## Cylinder Tracking Management System (CTMS) with Zoho Ecosystem Integration

---

## 1. Executive Summary & Vision

The **Cylinder Tracking Management System (CTMS)** is a cloud-native, offline-first enterprise asset tracking and logistics management platform engineered specifically for the industrial, medical, and LPG gas industry. 

The system models, monitors, and optimizes the complete lifecycle of high-pressure gas cylinders, cryogenic vessels, manifold pallets, and quad skids. By combining dual-technology identification (**tamper-evident 2D Matrix QR codes** and **UHF RFID tags**) with a rugged, driver-grade mobile application and automated background billing engines, CTMS eliminates the industry's four largest operational drains:
1. **Unreturned / Hoarded Cylinders:** Customers holding cylinders indefinitely without paying rental.
2. **Missing & Lost Assets:** Cylinders misplaced across trucks, filling docks, distributor networks, or customer yards.
3. **Safety & Regulatory Violations:** Filling cylinders past their statutory hydrostatic testing due date (PESO/SMPV/DOT regulations).
4. **Billing & Accounting Discrepancies:** Manual delivery paper challans not matching billing in the financial ledger, resulting in customer disputes and lost revenue.

Through deep, native bi-directional integration with the **Zoho Ecosystem (Zoho Books, Zoho Inventory, Zoho CRM, Zoho Analytics, Zoho Sign, and Zoho Flow)**, the system creates a single source of operational and financial truth.

```
       +-------------------------------------------------------------+
       |               CLIENTS, PARTNER APPS & AI AGENTS             |
       |  +--------------------+   +-------------------------------+ |
       |  | Native Android App |   | Plant Kiosk / Gate Reader     | |
       |  | (Driver & Field)   |   | (UHF RFID Tunnel / Fixed QR)  | |
       |  +---------+----------+   +---------------+---------------+ |
       |            | HTTPS                        | MQTT / HTTPS    |
       |  +---------+----------+   +---------------+---------------+ |
       |  | Partner Apps / HMIS|   | Autonomous AI Agents          | |
       |  | (REST API Keys)    |   | (Model Context Protocol / MCP)| |
       |  +---------+----------+   +---------------+---------------+ |
       +------------|------------------------------|-----------------+
                    | HTTPS (`X-API-Key`)          | MCP JSON-RPC
                    v                              v
       +-------------------------------------------------------------+
       |                      CTMS CLOUD CORE                        |
       |  +-------------------------------------------------------+  |
       |  | API Gateway & Auth (OAuth2, JWT, API Keys, MCP Server)|  |
       |  +-------------------------------------------------------+  |
       |  | Microservices & Business Engines:                     |  |
       |  |  • Cylinder Asset Engine     • In-App Rental Engine   |  |
       |  |  • Plant & Filling Station   • PESO Compliance Service|  |
       |  |  • Dispatch & POD Service    • Offline Sync Processor |  |
       |  +-------------------------------------------------------+  |
       |  | Databases & Cache:                                    |  |
       |  |  • PostgreSQL 16 + TimescaleDB (Multi-Tenant RLS)     |  |
       |  |  • Redis (Cache, Geo-Tracking, Sync Queue)            |  |
       |  +-------------------------------------------------------+  |
       +-----------------------------+-------------------------------+
                                     |
                       Webhooks / REST API (OAuth 2.0)
                                     v
       +-------------------------------------------------------------+
       |                       ZOHO ECOSYSTEM                        |
       |  +--------------+  +----------------+  +------------------+ |
       |  |  Zoho Books  |  | Zoho Inventory |  |     Zoho CRM     | |
       |  |  (Invoices,  |  |  (Gas Stock,   |  | (Accounts, SLAs, | |
       |  |  Deposits)   |  |   Warehouses)  |  |     Quotas)      | |
       |  +--------------+  +----------------+  +------------------+ |
       |  +--------------+  +----------------+  +------------------+ |
       |  | Zoho Sign    |  | Zoho Analytics |  |    Zoho Flow     | |
       |  | (Agreements) |  |  (BI Reports)  |  |   (Automation)   | |
       |  +--------------+  +----------------+  +------------------+ |
       +-------------------------------------------------------------+
```

---

## 2. Technology Stack & Component Architecture

### 2.1 Backend Services & Multi-Tenant SaaS Core
- **Runtime & Language:** Python 3.12+ (FastAPI) for high-performance async REST APIs, state machine validation, and rental calculations.
- **Web Dashboard Architecture:** Unified server-driven dynamic UI using **FastAPI + Jinja2 + HTMX + Tailwind CSS** (eliminating heavy client-side JS bundle overhead for plant dispatchers and finance officers).
- **Tenancy Architecture:** Multi-Tenant SaaS model. Each gas distributor/company operates as an isolated tenant (`tenant_id`) with its own plants, fleet, pricing tiers, and dedicated Zoho OAuth connection.
- **Database Engine:** PostgreSQL 16+ with TimescaleDB extension for immutable scan event series and spatial indexing (PostGIS).
- **In-Memory Store & Message Broker:** Redis 7+ for caching customer active holdings, live driver GPS coordinates, and session management.
- **Asynchronous Job Processing:** Celery (with Redis broker) for background rental calculation jobs, webhook dispatching, and Zoho synchronization queues.

### 2.2 Mobile Application (Driver & Field Operations)
- **Framework:** **Pure Native Android (Kotlin 2.0+ & Jetpack Compose)**, targeting Android 8.0+ to Android 15+.
- **Database (Local/Embedded):** Jetpack Room (SQLite) with encrypted local tables.
- **Offline Architecture:** Offline-first synchronization with an append-only event outbox pattern (`outbox_mutations`). All scans, signatures, and pickups commit immediately locally before attempting network calls.
- **Hardware Integrations:**
  - Fast Camera QR Code scanning using Google ML Kit Barcode Scanning API (sub-100ms continuous batch scan).
  - Bluetooth Low Energy (BLE) connectivity for UHF RFID Handheld Readers (Zebra RFD8500, Chainway C72).
  - Geolocation & GPS tracking with background breadcrumb logging.
  - Digital signature capture and direct thermal Bluetooth receipt printer integration (ESC/POS).

### 2.3 Web Administration & Finance Portal
- **Framework:** FastAPI + Jinja2 + HTMX with Tailwind CSS.
- **In-App Rental Management & Approval:** Dedicated finance dashboard to review calculated cylinder-holding days, apply fee adjustments/waivers, and approve batches before pushing to Zoho Books.
- **Role-Based Access Control (RBAC):** Granular permissions for Super Admin, Tenant Plant Manager, Filling Station Operator, Dispatcher, Driver, and Finance Officer.

### 2.4 External Developer APIs & Model Context Protocol (MCP) Server for AI Agents
- **Cryptographic API Key Gateway (`X-API-Key`):**
  - Allows third-party software (hospital HMIS, enterprise ERPs, distributor mobile apps) to securely interact with CTMS.
  - API keys use high-entropy tokens (`ctms_live_<32_hex>`) with SHA-256 storage, granular permission scopes (`cylinders:read`, `dispatch:write`, `rental:read`), CIDR IP whitelisting, and Redis leaky-bucket rate limiting (300 to 1,200 req/min).
- **Native Model Context Protocol (MCP) Server:**
  - Implements the open Model Context Protocol (MCP) over Server-Sent Events (SSE) and stdio to empower external autonomous AI agents (Claude Desktop, Cursor, Antigravity, Gemini CLI).
  - Exposes operational tools: `query_cylinder_passport`, `verify_peso_safety`, `get_customer_holding_audit`, `trace_batch_contamination`, `reconcile_trip_manifest`, and `trigger_zoho_books_sync`.
  - Exposes live read-only URI resources: `ctms://fleet/live-status`, `ctms://compliance/overdue-test`, `ctms://logistics/active-trips`, and `ctms://zoho/sync-health`.
  - Detailed in [docs/12_API_KEYS_AND_MCP_SERVER_SPECIFICATION.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/12_API_KEYS_AND_MCP_SERVER_SPECIFICATION.md).

---

## 3. Hardware & Identification Engineering

Gas cylinders operate in harsh industrial environments (outdoor weathering, high pressure, contact with lubricants, paint stripping, shot blasting, and hydraulic pressure testing). The identification media must endure these conditions.

| Parameter | 2D QR Code Tags | UHF RFID Tags (Anti-Metal) |
| :--- | :--- | :--- |
| **Technology** | Laser-etched Stainless Steel (SS304/SS316) or Anodized Aluminum tags, riveted or epoxy-bonded to the cylinder collar. | Passive EPC Gen2 (ISO 18000-6C) on-metal ceramic/ABS tags (865–868 MHz India/EU, 902–928 MHz US). |
| **Data Payload** | Alphanumeric Unique Identifier (UUID / Hash: e.g., `CYL-OX-47L-009281`) encoded as high-density Data Matrix or Micro QR. | 96-bit or 128-bit EPC Memory containing Encoded Cylinder Serial Number + 32-bit User Memory. |
| **Scanning Speed** | 1 cylinder per 0.5 – 1.0 second via smartphone camera. | Bulk scanning: up to 100+ cylinders simultaneously in 3 seconds using handheld or fixed RFID portal. |
| **Typical Use Case** | Driver delivery/pickup at customer premises, emergency refilling, manual audits. | Truck loading/unloading manifests, filling plant automated gate-pass, pallet/quad batching. |
| **Durability** | Heat resistant up to 600°C; resistant to acid, alkaline wash, and hydraulic test water. | IP68/IP69K rated; shock and vibration resistant; shielded against metal interference. |

---

## 4. Security, Compliance & Data Governance

1. **PESO & SMPV Compliance (India) / DOT Compliance (US):**
   - Hard enforcement of **Hydrostatic Stretch Testing** intervals (every 5 years for industrial/medical seamless steel cylinders, every 2 years for toxic/corrosive gases).
   - The system initiates an automated **Filling Interlock**: cylinders overdue for testing cannot be assigned a batch or marked as filled.
2. **Data Encryption:**
   - Transport Security: TLS 1.3 for all web, mobile, and API communications.
   - Storage Security: AES-256 encryption at rest for databases, backups, and customer documents.
3. **Audit Trail & Non-Repudiation:**
   - Every movement creates an immutable event record: `CylinderID`, `Timestamp`, `ActorID`, `ActionType`, `FromLocation`, `ToLocation`, `GeoCoordinates`, `BatchNumber`, and `ZohoInvoiceReference`.
   - Edits or manual overrides require managerial approval and reason tagging.
