# Cylinder Tracking Management System (CTMS)
## Comprehensive Project Overview, Architecture Blueprint & Operational Guide

---

## Executive Summary

The **Cylinder Tracking Management System (CTMS)** is an industrial-grade asset tracking, statutory compliance, and enterprise ERP integration platform specifically engineered for the high-pressure industrial and medical gas manufacturing and distribution sector.

In traditional gas distribution, high-pressure steel cylinders represent the single largest capital expenditure (CapEx) asset of the business, often outstripping the valuation of the gas production plants themselves. However, standard ERP systems (such as SAP, Oracle, or generic accounting tools) treat gas cylinders merely as "packaging" or "inventory quantities", completely failing to track the physical, serialized container throughout its 40-year statutory lifecycle.

CTMS bridges this critical gap by treating the **Gas Cylinder as an Intelligent, Trackable Capital Asset**, natively integrated with the **Zoho Ecosystem (Books, Inventory, CRM, Analytics, Sign)**, backed by a **Pure Native Android Mobile Application (Kotlin + Jetpack Compose)**, and governed by a strict, tamper-proof **PESO Statutory Safety Interlock Engine**.

```
+----------------------------------------------------------------------------------------------------+
|                                    CTMS UNIFIED ECOSYSTEM                                          |
+----------------------------------------------------------------------------------------------------+
                                                  │
                 ┌────────────────────────────────┴────────────────────────────────┐
                 ▼                                                                 ▼
   ┌───────────────────────────┐                                     ┌───────────────────────────┐
   │    Plant & Field Edge     │                                     │     Cloud & ERP Core      │
   ├───────────────────────────┤                                     ├───────────────────────────┤
   │ • Native Android App      │                                     │ • PostgreSQL 16 +         │
   │ • CameraX Sub-100ms Scans │         Bi-Directional Sync         │   TimescaleDB (Hypertable)│
   │ • Offline SQLite Room DB  │ ◄─────────────────────────────────► │ • Redis 7 (Leaky Bucket)  │
   │ • Zebra / Chainway Lasers │          Outbox Mutations           │ • Dgraph Knowledge Graph  │
   │ • ESC/POS Thermal Print   │                                     │ • FastAPI REST Gateway    │
   │ • Bluetooth BLE RFID      │                                     │ • Zoho Enterprise Sync    │
   └───────────────────────────┘                                     └───────────────────────────┘
                 │                                                                 │
                 └────────────────────────────────┬────────────────────────────────┘
                                                  ▼
                                   ┌───────────────────────────┐
                                   │  AI & Extensibility Tier  │
                                   ├───────────────────────────┤
                                   │ • Native MCP Server (SSE) │
                                   │ • API Key Gateway (SHA256)│
                                   │ • B2B Customer Web Portal │
                                   │ • Statutory PESO Exporters│
                                   └───────────────────────────┘
```

---

## 1. Prime Business Problems Solved

Industrial gas manufacturers and distributors face multi-crore annual losses caused by operational blind spots:

### 1.1 Unbilled Customer Hoarding & Cylinder Shrinkage
- **Problem:** Customers hoard empty cylinders on-site as free gas buffers, keeping them idle for 60–180 days. Distributors lose millions of rupees in unbilled holding fees and are forced to purchase costly new cylinders.
- **CTMS Solution:** Tracks the exact dwell time of every cylinder at customer premises to the minute. Applies contract-specific grace periods (e.g., 14 free days) and automatically computes daily rental fees using progressive holding slabs (e.g., ₹10/day for Days 15–30; ₹20/day thereafter), generating itemized monthly rental tax invoices in Zoho Books.

### 1.2 Life-Threatening Safety & PESO Violations
- **Problem:** Cylinders operate under extreme pressure (150 to 300 bar). Overdue cylinders that miss their mandatory 5-year **PESO (Petroleum and Explosives Safety Organization)** hydrostatic stretch testing risk catastrophic rupture and fatal plant explosions.
- **CTMS Solution:** A hard digital interlock at the filling station manifold. If `CurrentDate >= hydro_test_due_date`, the system triggers an immediate non-dismissible `403 FORBIDDEN` lockout, preventing filling batch assignment.

### 1.3 Multi-Ownership Mixing (Company-Owned vs Party-Owned)
- **Problem:** When customers bring their own cylinders (**Party-Owned Cylinders - POC**) for contract filling, distributors accidentally mix them into company inventory (**Company-Owned Cylinders - COC**) or illegally bill rental fees on customer-owned assets.
- **CTMS Solution:** Strict ledger segregation. POC assets are permanently linked to `owner_customer_id`, completely exempt from rental billing, and enforced by dispatch validation to be returned exclusively to their rightful owner.

### 1.4 Route Theft & Truck Load Reconciliation Failures
- **Problem:** Drivers leave the plant with 120 full cylinders, drop off gas at 8 customer sites, collect empties, and return with unaccounted cylinder discrepancies.
- **CTMS Solution:** Automated plant gate reconciliation. The system matches outward manifest scans against customer electronic Delivery Challans (e-DC) and collected empties upon return. Any discrepancy generates an immediate gate supervisor alert.

---

## 2. The 5 Prime Invariants (Non-Negotiable Rules)

Every module, algorithm, and test suite in CTMS enforces 5 inviolable engineering laws:

```
+---+----------------------------------+-------------------------------------------------------------+
| # | Prime Invariant                  | Core Behavioral Mandate                                     |
+---+----------------------------------+-------------------------------------------------------------+
| 1 | PESO Safety Zero-Tolerance       | Never allow an overdue cylinder (CurrentDate >= test_due)   |
|   | (Filling Station Hard Interlock) | to be filled or dispatched. Return explicit HTTP 403.       |
+---+----------------------------------+-------------------------------------------------------------+
| 2 | Immutable Scan Event Ledger      | Every scan, movement, or state transition appends a new row |
|   |                                  | to cylinder_events. Existing rows are never updated/deleted.|
+---+----------------------------------+-------------------------------------------------------------+
| 3 | Multi-Ownership Integrity        | Party-Owned Cylinders (POC) must NEVER incur rental charges |
|   | (COC vs POC Segregation)         | and must strictly return to their verified customer owner.  |
+---+----------------------------------+-------------------------------------------------------------+
| 4 | Offline-First Mobile Resilience  | Android client must commit all scans, signatures, and GPS   |
|   |                                  | locally to Room SQLite first. UI never blocks on network.   |
+---+----------------------------------+-------------------------------------------------------------+
| 5 | Financial Idempotency            | Every outbound Zoho Books/Inventory API transaction must    |
|   | (Zoho Synchronization)           | send an explicit Idempotency-Key. Zero duplicate invoices.  |
+---+----------------------------------+-------------------------------------------------------------+
```

---

## 3. Domain Model: The Core Entity Triad

Unlike standard inventory software, CTMS models the physical reality of gas distribution across three distinct, decoupled dimensions:

```
               ┌────────────────────────────────────────────────────────┐
               │                     1. CONTAINER                       │
               │  (Physical High-Pressure Steel Cylinder Asset)         │
               │  - Serial Number, Tare Weight, Hydro Test Date, Owner  │
               └───────────────────────────┬────────────────────────────┘
                                           │
                        Encapsulates       │ Filled At Plant
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │                      2. PRODUCT                        │
               │  (Compressed / Liquefied Gas Consumable)               │
               │  - Medical O2 IP, Argon, Nitrogen, Purity %, Volume m3 │
               └───────────────────────────┬────────────────────────────┘
                                           │
                         Delivered Under   │ Governed By Contract
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │                     3. CUSTODIAN                       │
               │  (Legal Holder / Commercial Agreement)                 │
               │  - Plant Yard, Truck Trip In-Transit, Customer Site    │
               │  - Security Deposit, Grace Days, Daily Rental Slab     │
               └────────────────────────────────────────────────────────┘
```

---

## 4. The 10-Stage Lifecycle State Machine

A cylinder transitions through 10 deterministic states throughout its continuous operational loop:

```
      ┌────────────────┐      Safety Inspection       ┌────────────────┐
      │  PLANT_EMPTY   │ ───────────────────────────► │  IN_INSPECTION │
      └────────────────┘                              └────────────────┘
               ▲                                               │
               │ Returned Empty                                │ Passed PESO Check
               │                                               ▼
      ┌────────────────┐                              ┌────────────────┐
      │ CUSTOMER_HELD  │                              │    FILLING     │
      └────────────────┘                              └────────────────┘
               ▲                                               │
               │ Customer POD Received                         │ Manifold Fill Done
               │                                               ▼
      ┌────────────────┐       Gate Outward           ┌────────────────┐
      │  IN_TRANSIT    │ ◄─────────────────────────── │  PLANT_FILLED  │
      └────────────────┘                              └────────────────┘
```

### Complete State Reference Table:
1. `PLANT_EMPTY`: Empty cylinder sitting in plant sorting yard waiting for pre-fill inspection.
2. `IN_INSPECTION`: Undergoing visual, neck thread, tare loss, and PESO hydro-test expiry check.
3. `FILLING`: Connected to filling manifold; gas actively being compressed into cylinder.
4. `PLANT_FILLED`: Filled, analyzed for gas purity, sealed with safety tamper cap, stored in full yard.
5. `LOADED_TRUCK`: Scanned onto truck bed; manifest linked to active logistics `trip_id`.
6. `IN_TRANSIT`: Truck has passed plant outward gate; cylinders are under driver custody.
7. `CUSTOMER_HELD`: Delivered to customer; receipt confirmed via digital e-DC, e-signature, or OTP.
8. `COLLECTED_EMPTY`: Empty cylinder collected from customer site and scanned onto returning truck.
9. `UNDER_MAINTENANCE`: Withdrawn from service for valve replacement, shot blasting, or painting.
10. `CONDEMNED_PESO`: Permanently decommissioned due to failed hydrostatic stretch test ($>10\%$ permanent expansion) or excessive tare weight loss ($>5\%$).

---

## 5. Zoho Cloud Suite Integration (The Core Document Triad)

CTMS acts as the physical edge execution engine, while **Zoho Books, Zoho Inventory, and Zoho CRM** serve as the financial and commercial system of record.

```
+----------------------------------------------------------------------------------------------------+
|                               THE ZOHO CORE DOCUMENT TRIAD                                         |
+----------------------------------------------------------------------------------------------------+
| Zoho Document Type         | CTMS Operational Direction       | Business & Financial Impact        |
+----------------------------+----------------------------------+------------------------------------+
| 1. Sales Orders (SO)       | CYLINDER INFLOW                  | Customer request for full gas or   |
|                            | (Customer Demand Entry)          | empty cylinder pickup.             |
| 2. Invoices (INV)          | CYLINDER OUTFLOW                 | Consumable gas product sold, tax   |
|                            | (Consumable Gas Revenue)         | invoiced, and accounts receivable. |
| 3. Delivery Challans (DC)  | CYLINDER UNDER SECURITY / RENT   | Container asset loaned to customer |
|                            | (Asset Holding & Bailment)       | under security deposit & rental.   |
+----------------------------+----------------------------------+------------------------------------+
```

### Integration Highlights:
- **Zoho Books:** Automatically generates GST Delivery Challans on customer delivery, invoices for gas volume, and monthly consolidated rental bills with itemized cylinder serial audit trails.
- **Zoho Inventory:** Tracks serialized asset containers separately from consumable gas volumes in cubic meters ($m^3$) or kilograms ($kg$).
- **Zoho CRM:** Syncs customer credit limits, free grace periods, and injects a real-time "Live Cylinder Holding Widget" into customer account pages.
- **Zoho Sign:** Collects legally binding digital signatures on Master Cylinder Loan Agreements and security deposit pledges.
- **Zoho Analytics:** Generates business intelligence on turnaround cycle time (TAT), truck utilization, and customer cylinder hoarders.

---

## 6. Native Android Mobile Architecture (Kotlin + Jetpack Compose)

Field drivers and plant operators work in harsh environments (direct sunlight, industrial yards, metal warehouses) without reliable 4G/5G connectivity.

```
       ┌─────────────────────────────────────────────────────────────┐
       │             Presentation Tier (Jetpack Compose)             │
       │  • Oversized 56dp Touch Targets (Glove-Friendly)            │
       │  • High-Contrast Sunlight Theme (WCAG AAA Compliance)       │
       │  • Tabular Numbers (tnum) for Jitter-Free Scan Counters     │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │            Scanner & Hardware Abstraction Tier              │
       │  • CameraX + Google ML Kit (Sub-100ms Continuous 2D QR)     │
       │  • Zebra DataWedge & Chainway Laser Gun Broadcast Receivers │
       │  • ESC/POS Thermal Print Engine (58mm / 80mm Bluetooth)     │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │             Offline-First Data Tier (Room SQLite)           │
       │  • Local Room Entities: cylinders, challans, customers      │
       │  • Outbox Mutation Queue (outbox_mutations)                 │
       │  • Jetpack WorkManager Background Synchronizer              │
       └─────────────────────────────────────────────────────────────┘
```

---

## 7. Hardware Peripherals & Operational Exception Playbooks

Real-world factory floors and delivery routes encounter physical anomalies that break naive software:

### 7.1 Bluetooth ESC/POS Thermal Printer Engine
- Generates field **Electronic Delivery Challans (e-DC)** and **Electronic Cylinder Receipts (ECR)** on 58mm (32-column) and 80mm (48-column) belt-clip printers.
- **Raster-First QR (`GS v 0`):** Universal bitmap printing as standard; bypasses firmware bugs in low-cost printers lacking native `GS ( k`.
- **Tear Bar vs. Guillotine Cutters:** Issues line feed `1B 64 04` past the manual tear bar on 58mm printers; partial cut `1D 56 42 00` on 80mm cutters.
- **Currency & Unicode:** Uses standard ASCII `Rs.` or pre-renders Devanagari text on Android bitmaps to avoid code-page corruption.
- **Reprint Invariant:** Reprinted challans carry bold `*** DUPLICATE COPY ***` header and append an auditable `RECEIPT_REPRINTED` event to the ledger.

### 7.2 Dedicated Android Rugged Gun Scanners
- Zero code-rewrites for industrial laser barcode terminals (Zebra TC26, Chainway C66).
- **Auto-Provisioning:** On first launch, the app dispatches DataWedge `SET_CONFIG` via `com.symbol.datawedge.api.ACTION` to self-configure the profile.
- **ScannerSource Interface:** Decouples CameraX ML Kit, Zebra DataWedge, and Chainway laser hardware behind a unified reactive `StateFlow<ScanEvent>` abstraction.

### 7.3 Operational Edge Playbooks:
1. **Damaged Collar QR Code Re-Tagging:** When a QR collar tag is destroyed by grit blasting or impact, an authorized operator searches the hard-stamped metal serial number, photographs the shoulder, scans an unassigned QR tag, and requests manager OTP approval. The backend updates the temporal `tag_bindings` table, retiring the old tag while permanently preserving the 40-year event history on the cylinder UUID.
2. **Concurrent Offline Scan Collision (HLC & State Machine Replay):** When two offline drivers scan the same cylinder simultaneously, arbitration does NOT rely on drifting system clocks or indoor-failing GPS. Events carry a **Hybrid Logical Clock (HLC)** and device monotonic sequence numbers. The cloud replays events strictly through the custody state machine; conflicting transitions are flagged as `REJECTED_CONFLICT` without overwriting state, and an audit task with GPS/photo evidence is queued for human-in-the-loop review.
3. **Ghost / Unaccounted Cylinder Audit:** When unrecorded cylinders are discovered in the plant yard, they transition to `QUARANTINED_AUDIT` and daily rental fee accrual is **immediately paused** to protect customer relations during reconciliation.

---

## 8. Statutory PESO Compliance & B2B Customer Portal

### 8.1 PESO Rule 35 Mathematical Validation & Template Exporter
High-pressure gas cylinders must undergo mandatory hydraulic stretch testing every 5 years under Rule 35 of the Gas Cylinders Rules, 2016:
- **Expansion Ratio Calculation:**
  $$\text{Expansion Ratio} = \left(\frac{\text{Permanent Expansion (cc)}}{\text{Total Volumetric Expansion (cc)}}\right) \times 100 \le 10.0\%$$
- **Tare Weight Loss Calculation:**
  $$\text{Tare Loss} = \left(\frac{\text{Original Tare} - \text{Current Clean Tare}}{\text{Original Tare}}\right) \times 100 \le 5.0\%$$
- **Template-Driven Exporter:** Separates raw hydrostatic measurements from statutory layouts, rendering cryptographically signed **PESO Form III** (Stretch Test Certificates) and **PESO Form IV** (Daily Testing Registers) without code rewrites upon regulatory format changes.

### 8.2 B2B Customer Self-Service Portal
Institutional buyers (hospitals, industrial fabrication plants) access a dedicated portal:
- **PostgreSQL Row-Level Security (RLS):** Strict multi-tenant isolation keyed on `customer_id`.
- **Role-Based Access Control:** Distinct roles for `PURCHASE_MANAGER`, `STORE_KEEPER`, and `CLINICAL_AUDITOR`.
- Passwordless magic link + SMS/WhatsApp MFA authentication.
- Live holding matrix displaying cylinder counts by gas type and individual countdowns to rent commencement, with CSV export.
- One-click emergency refill requests triggering driver WhatsApp alerts with 2-hour ICU SLA timers.
- **Hospital NABH Audit Vault:** Instant download of gas purity analysis certificates (Medical $O_2$ IP $99.5\%+$) and hydro-test validity certificates via HMAC-signed, expiring Presigned URLs.

---

## 9. Developer API Gateway & AI MCP Server

CTMS provides enterprise extensibility for external business software and autonomous AI agents:

```
+----------------------------------------------------------------------------------------------------+
|                                    EXTENSIBILITY INTERFACES                                        |
+----------------------------------------------------------------------------------------------------+
| 1. Cryptographic API Key Gateway       | 2. Native Model Context Protocol (MCP) Server             |
+----------------------------------------+-----------------------------------------------------------+
| • High-entropy keys (ctms_live_...)    | • Native MCP over Server-Sent Events (SSE) & stdio        |
| • Granular RBAC scopes                 | • AI Tools: query_cylinder_passport, verify_peso_safety,   |
| • IP CIDR whitelisting                 |   get_customer_holding_audit, trace_batch_contamination    |
| • Redis leaky-bucket rate limiting     | • Streaming Resources: ctms://fleet/live-status,          |
|   (300 req/min with 429 backoff)       |   ctms://compliance/overdue-test, ctms://zoho/sync-health  |
+----------------------------------------+-----------------------------------------------------------+
```

---

## 10. Technical Stack & Local Docker Topology

```
+----------------------------------------------------------------------------------------------------+
| Component               | Technology Selected             | Operational Purpose                    |
+-------------------------+---------------------------------+----------------------------------------+
| Primary Database        | PostgreSQL 16 + PostGIS         | Relational customer, order & RLS data  |
| Time-Series Ledger      | TimescaleDB (Weekly Hypertables)| High-throughput cylinder_events audits |
| Lineage & Custody Graph | PostgreSQL Recursive CTEs       | Fast (<10ms) custody chain traversal   |
| Enterprise Graph DB     | Dgraph Standalone (Optional)    | Secondary deep multi-hop supply graph  |
| Cache & Rate Limiting   | Redis 7.2 (Alpine)              | Sync queues, leaky-bucket rate limits  |
| Backend API Gateway     | Python 3.12+ (FastAPI)          | Business logic, Zoho integration       |
| Mobile Application      | Kotlin 2.0+ & Jetpack Compose   | Pure native offline-first mobile app   |
| Mobile Local Security   | SQLCipher for Room SQLite       | Full AES-256 local database encryption |
| Hermetic Test Mock      | Python 3 Mock Zoho Server       | Zero-dependency offline CI/CD testing  |
| Orchestration           | Docker Compose v3.8             | Local containerized developer sandbox  |
| Continuous Integration  | GitHub Actions                  | Automated link audits & test suites    |
+-------------------------+---------------------------------+----------------------------------------+
```

---

## 11. Multi-Agent Development Swarm (ADD Framework)

CTMS is developed following the **Agent-Driven Development (ADD)** methodology, dividing complex engineering across 8 specialized AI domain agents located in [`.agents/agents/`](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/):

1. **[01_zoho_integration_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/01_zoho_integration_agent.md):** Governs Books, Inventory, CRM, and Zoho Document Triad synchronization.
2. **[02_android_app_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/02_android_app_agent.md):** Governs Kotlin, Jetpack Compose, CameraX, and Room SQLite offline mechanics.
3. **[03_backend_api_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/03_backend_api_agent.md):** Governs FastAPI endpoints, 10-state lifecycle logic, and progressive rental calculation math.
4. **[04_industrial_design_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/04_industrial_design_agent.md):** Governs UI/UX tokens, high-contrast sunlight mode, and 56dp glove-friendly touch targets.
5. **[05_interaction_protocol_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/05_interaction_protocol_agent.md):** Governs API Key security, Redis rate limiting, and Model Context Protocol (MCP) servers.
6. **[06_database_ledger_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/06_database_ledger_agent.md):** Governs TimescaleDB hypertables, compression policies, and Dgraph knowledge graph queries.
7. **[07_agent_coordinator.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/07_agent_coordinator.md):** Coordinates cross-agent handoffs, sprint tracking, and index maintenance.
8. **[08_quality_test_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/08_quality_test_agent.md):** Enforces Red-Green-Refactor testing, hermetic mocks, and proof artifacts.

---

## 12. Complete Documentation & Navigation Directory

| Document Path | Purpose |
| :--- | :--- |
| **[README.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/README.md)** | Public repository landing page and executive architecture summary. |
| **[INDEX.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/INDEX.md)** | Authoritative master directory cataloguing every file, its description, and its purpose. |
| **[AGENTS.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/AGENTS.md)** | Agent-Driven Development rules, 5 Prime Invariants, and Red-Green-Refactor execution protocols. |
| **[TASK_QUEUE.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/TASK_QUEUE.md)** | Engineering sprint backlog, acceptance criteria, and task verification commands. |
| **[docker-compose.yml](file:///home/server/GoogleDrive/CylinderTrackingSystem/docker-compose.yml)** | Multi-container local infrastructure (Postgres, TimescaleDB, Redis, Dgraph, Mock Zoho). |
| **[docs/01_SYSTEM_REQUIREMENTS_AND_ARCHITECTURE.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/01_SYSTEM_REQUIREMENTS_AND_ARCHITECTURE.md)** | Cloud & edge architecture, hardware selection (QR vs UHF RFID), and security governance. |
| **[docs/02_CORE_FUNCTIONAL_MODULES.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/02_CORE_FUNCTIONAL_MODULES.md)** | 10-stage lifecycle, multi-ownership rules (COC/POC), and progressive rental math. |
| **[docs/03_ZOHO_ECOSYSTEM_INTEGRATION_SPEC.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/03_ZOHO_ECOSYSTEM_INTEGRATION_SPEC.md)** | Deep Zoho Books, Inventory, CRM, and Analytics integration blueprint. |
| **[docs/04_DATA_MODELS_AND_SCHEMA_DESIGN.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/04_DATA_MODELS_AND_SCHEMA_DESIGN.md)** | Complete PostgreSQL DDL, ENUM definitions, tables, and hypertable event ledgers. |
| **[docs/05_API_SPECIFICATION_AND_OFFLINE_SYNC.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/05_API_SPECIFICATION_AND_OFFLINE_SYNC.md)** | REST API specifications, offline SQLite outbox sync, and inbound webhook contracts. |
| **[docs/06_IMPLEMENTATION_ROADMAP_AND_MILESTONES.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/06_IMPLEMENTATION_ROADMAP_AND_MILESTONES.md)** | 24-week phased delivery schedule across 5 phases and QA exit benchmarks. |
| **[docs/07_NATIVE_ANDROID_APP_SPECIFICATION.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/07_NATIVE_ANDROID_APP_SPECIFICATION.md)** | Native Android (Kotlin + Compose) architecture, CameraX, Room DB, and WorkManager. |
| **[docs/08_ZOHO_API_INTERACTIONS_AND_PAYLOAD_SPECIFICATION.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/08_ZOHO_API_INTERACTIONS_AND_PAYLOAD_SPECIFICATION.md)** | Exact JSON request/response payloads, field mappings, rate limits, and idempotency. |
| **[docs/09_AI_DRIVEN_DEVELOPMENT_PROTOCOLS_AND_BEST_PRACTICES.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/09_AI_DRIVEN_DEVELOPMENT_PROTOCOLS_AND_BEST_PRACTICES.md)** | The 7 AIDD protocols, TDD for AI, and automated link auditing tools. |
| **[docs/10_DATA_MIGRATION_SECURITY_AND_DISASTER_RECOVERY_PLAN.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/10_DATA_MIGRATION_SECURITY_AND_DISASTER_RECOVERY_PLAN.md)** | Phase 0 fleet retrofitting, 7-role enterprise RBAC matrix, and disaster recovery. |
| **[docs/11_SYSTEM_UNDERSTANDING_AND_KNOWLEDGE_GRAPH.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/11_SYSTEM_UNDERSTANDING_AND_KNOWLEDGE_GRAPH.md)** | Dgraph DQL graph schema and recall queries for hospital batch contamination. |
| **[docs/12_API_KEYS_AND_MCP_SERVER_SPECIFICATION.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/12_API_KEYS_AND_MCP_SERVER_SPECIFICATION.md)** | Cryptographic API Key Gateway and native Model Context Protocol (MCP) server. |
| **[docs/13_HARDWARE_PERIPHERALS_AND_EXCEPTION_PLAYBOOKS.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/13_HARDWARE_PERIPHERALS_AND_EXCEPTION_PLAYBOOKS.md)** | Bluetooth ESC/POS printers, Zebra/Chainway lasers, damaged QR re-tagging playbooks. |
| **[docs/14_STATUTORY_PESO_REPORTING_AND_CUSTOMER_PORTAL.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/14_STATUTORY_PESO_REPORTING_AND_CUSTOMER_PORTAL.md)** | PESO Rule 35 Form III/IV compliance dossiers and hospital NABH customer portal. |
| **[docs/15_INFRASTRUCTURE_DOCKER_AND_CI_CD_PIPELINE.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/15_INFRASTRUCTURE_DOCKER_AND_CI_CD_PIPELINE.md)** | Local container infrastructure and GitHub Actions automated CI/CD pipeline. |
| **[scripts/verify_all.sh](file:///home/server/GoogleDrive/CylinderTrackingSystem/scripts/verify_all.sh)** | Single-command master CI/verification script validating 100% link integrity and syntax. |

---

## 13. Active Software Scaffolding & Codebase Foundation

As of Phase 1 implementation, the codebase scaffolding is active across both the backend server and Android mobile subsystems:

### 13.1 Backend Architecture (`backend/`)
- **Database Migrations:** [`backend/src/database/migrations/001_initial_schema.sql`](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/database/migrations/001_initial_schema.sql) deploys the complete relational schema (18 tables, enums, indexes, and constraints). [`002_timescale_setup.sql`](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/database/migrations/002_timescale_setup.sql) configures TimescaleDB weekly hypertable partitioning and 30-day compression policies for `cylinder_events`.
- **PESO Safety Validation Engine:** [`backend/src/modules/safety/peso_engine.py`](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/modules/safety/peso_engine.py) strictly enforces statutory pre-fill safety rules (Prime Rule #1: `403 Forbidden` on overdue hydrostatic test; $\le 5.0\%$ tare loss threshold; cross-contamination gas lock).
- **10-State Lifecycle Machine:** [`backend/src/modules/lifecycle/state_machine.py`](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/modules/lifecycle/state_machine.py) enforces deterministic state progression and generates immutable audit ledger events for every scan (Prime Rule #2).
- **Progressive Rental Engine:** [`backend/src/modules/rental/calculator.py`](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/modules/rental/calculator.py) calculates multi-tier progressive holding charges and strictly guarantees Party-Owned Cylinders (POC) are exempt from holding rental (Prime Rule #3).
- **Zoho Books Client:** [`backend/src/integrations/zoho/books_client.py`](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/integrations/zoho/books_client.py) pushes Delivery Challans and Tax Invoices with mandatory `Idempotency-Key` headers (Prime Rule #5).
- **API Key Gateway & Native MCP Server:** [`backend/src/mcp/auth.py`](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/mcp/auth.py) validates SHA-256 hashed API keys with leaky-bucket rate limiting. [`backend/src/mcp/server.py`](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/mcp/server.py) implements the Model Context Protocol exposing tools and live streaming resources for external AI assistants.
- **REST API Server:** [`backend/src/main.py`](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/main.py) and [`backend/src/api/routes.py`](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/api/routes.py) expose core endpoints for pre-check, state transitions, rental calculations, and MCP dispatch.

### 13.2 Native Android Mobile Client (`android/`)
- **Build Infrastructure:** Configured with Gradle Kotlin DSL, Jetpack Compose, Room 2.6, WorkManager, Dagger Hilt, and CameraX + Google ML Kit in [`android/app/build.gradle.kts`](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/app/build.gradle.kts) and [`android/build.gradle.kts`](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/build.gradle.kts).
- **Offline-First Room SQLite Ledger:** Structured in [`android/app/src/main/java/com/ctms/app/data/local/`](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/app/src/main/java/com/ctms/app/data/local/) with transactional outbox [`OutboxMutationEntity.kt`](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/app/src/main/java/com/ctms/app/data/local/entity/OutboxMutationEntity.kt) and [`OutboxDao.kt`](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/app/src/main/java/com/ctms/app/data/local/dao/OutboxDao.kt) to guarantee zero UI network blocking (Prime Rule #4), and local cylinder cache [`CylinderCacheEntity.kt`](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/app/src/main/java/com/ctms/app/data/local/entity/CylinderCacheEntity.kt).
- **Main Compose Activity:** [`android/app/src/main/java/com/ctms/app/presentation/MainActivity.kt`](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/app/src/main/java/com/ctms/app/presentation/MainActivity.kt) initialized with Material 3 theming.

### 13.3 Test Verification & Proof
All unit test suites in [`backend/tests/`](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/tests/) and [`scripts/verify_all.sh`](file:///home/server/GoogleDrive/CylinderTrackingSystem/scripts/verify_all.sh) execute with 100% green pass status, verified against [`TASK_QUEUE.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/TASK_QUEUE.md).
