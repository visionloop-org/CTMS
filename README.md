# Cylinder Tracking Management System (CTMS)
### Enterprise Asset Tracking & Logistics ERP with Deep Zoho Ecosystem Integration

---

## 📌 Project Overview

This repository contains the comprehensive system design, functional requirements, technical architecture, database schemas, and integration specifications for the **Cylinder Tracking Management System (CTMS)**. 

Modeled directly on industry-leading workflows found in platforms like [CTMS Gas](https://ctmsgas.com/), this solution is engineered to eliminate cylinder asset shrinkage, automate daily rental billing, enforce statutory PESO/SMPV safety compliance, and provide seamless bi-directional synchronization with the **Zoho Ecosystem (Zoho Books, Zoho Inventory, Zoho CRM, Zoho Analytics, and Zoho Sign)**.

```
                              CTMS ENTERPRISE SYSTEM
                                        │
    ┌───────────────────────────────────┼───────────────────────────────────┐
    │                                   │                                   │
    ▼                                   ▼                                   ▼
[ Plant & Filling Station ]     [ Logistics & Driver App ]       [ Automated Financials ]
• Pre-fill safety interlocks    • Offline-first scanning         • Daily holding engine
• Hydro-test validity locks     • High-speed 2D QR / UHF RFID    • Tiered progressive slabs
• Tare weight verification      • Digital POD & e-Signature      • Security deposit ledgers
• Batch purity & pressure logs  • Trip loading reconciliation    • Automated Zoho Books sync
                                        │
                                        ▼
                           [ Complete Zoho Ecosystem ]
         Zoho Books  │  Zoho Inventory  │  Zoho CRM  │  Zoho Analytics
```

---

## 📁 Planning & Technical Documentation Suite

> 📘 **Detailed End-to-End Project Understanding:** For an exhaustive, high-level and granular overview of the system architecture, domain models, business problem space, and operational mechanics, read the **[PROJECT_OVERVIEW.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/PROJECT_OVERVIEW.md)**.
>
> 📌 **Master Repository Index & File Catalog:** For a complete inventory of every file in the project (including operational rules, agent skills, design guides, and scripts) along with their description and purpose, see **[INDEX.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/INDEX.md)**.

The complete engineering specification is organized into the following modular blueprints within the [`docs/`](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/) directory:

| Document | Key Topics Covered |
| :--- | :--- |
| **[01_SYSTEM_REQUIREMENTS_AND_ARCHITECTURE.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/01_SYSTEM_REQUIREMENTS_AND_ARCHITECTURE.md)** | • High-level cloud & edge architecture<br>• Technology stack (Node/Go, PostgreSQL, Redis, Flutter)<br>• Hardware specs: 2D Matrix QR vs UHF RFID (anti-metal)<br>• Security, encryption, and statutory PESO governance |
| **[02_CORE_FUNCTIONAL_MODULES.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/02_CORE_FUNCTIONAL_MODULES.md)** | • Multi-ownership asset ledger: Company Owned (COC) vs Customer Owned (POC) vs Vendor (VOC)<br>• 10-stage cylinder lifecycle state machine<br>• Filling station validation & batch purity logging<br>• Dispatch trip management & truck reconciliation algorithm<br>• Driver mobile app & digital Proof of Delivery (POD)<br>• Automated rental/holding calculation engine with progressive slabs<br>• Statutory PESO hydrostatic stretch testing tracking |
| **[03_ZOHO_ECOSYSTEM_INTEGRATION_SPEC.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/03_ZOHO_ECOSYSTEM_INTEGRATION_SPEC.md)** | • **Zoho Books:** Automated Delivery Challans, Invoices, Monthly Rental Invoicing, Security Deposit liabilities, Payment sync<br>• **Zoho Inventory:** Gas volume stock ($m^3/kg$) vs serialized cylinder containers, multi-warehouse plant/truck tracking<br>• **Zoho CRM:** Customer contracts, grace days, holding quotas, live holding widgets<br>• **Zoho Analytics:** Fleet utilization, turnaround cycle time (TAT), shrinkage BI<br>• **Zoho Sign:** Digital cylinder loan agreements and deposit pledges<br>• Webhook security, HMAC verification, retry queues & idempotency |
| **[04_DATA_MODELS_AND_SCHEMA_DESIGN.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/04_DATA_MODELS_AND_SCHEMA_DESIGN.md)** | • Complete PostgreSQL DDL schema & ENUM definitions<br>• Master tables: `cylinders`, `bundles` (quads/skids), `customers`, `rental_slabs`<br>• Operational tables: `filling_batches`, `trips`, `delivery_challans`, `challan_items`<br>• Immutable lifetime scan ledger: `cylinder_events`<br>• Asynchronous integration outbox: `zoho_sync_outbox` |
| **[05_API_SPECIFICATION_AND_OFFLINE_SYNC.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/05_API_SPECIFICATION_AND_OFFLINE_SYNC.md)** | • Offline-first synchronization protocol with client-side SQLite outbox<br>• Conflict resolution & idempotency mechanics<br>• REST APIs for authentication, bulk batch scanning, and filling station safety pre-check<br>• Real-time customer holding & accrued rental audit endpoint<br>• Inbound Zoho webhook handler specification |
| **[06_IMPLEMENTATION_ROADMAP_AND_MILESTONES.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/06_IMPLEMENTATION_ROADMAP_AND_MILESTONES.md)** | • 24-week phased implementation plan (Phases 1 to 4)<br>• Milestone exit criteria from initial QR tagging to full Zoho BI deployment<br>• Quality assurance protocols (offline resilience, scan speeds, load tests)<br>• Risk assessment & operational mitigation matrix |
| **[07_NATIVE_ANDROID_APP_SPECIFICATION.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/07_NATIVE_ANDROID_APP_SPECIFICATION.md)** | • **Pure Native Android (Kotlin + Jetpack Compose)** architecture<br>• Sub-100ms camera scanning with CameraX & Google ML Kit<br>• Offline-first SQLite/Room database with outbox event queuing<br>• Background synchronization via Jetpack WorkManager<br>• Hardware SDK integration: Zebra DataWedge, Chainway BLE UHF RFID sleds, ESC/POS Bluetooth thermal printers<br>• Digital e-signature canvas, customer OTP verification, GPS geotagging<br>• Kiosk Mode & Enterprise MDM (ManageEngine / SOTI / Intune) compatibility |
| **[08_ZOHO_API_INTERACTIONS_AND_PAYLOAD_SPECIFICATION.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/08_ZOHO_API_INTERACTIONS_AND_PAYLOAD_SPECIFICATION.md)** | • **Zoho API Architecture & Interaction Sequences:** Books, Inventory, CRM, Analytics, Sign<br>• **Exhaustive Payload Plan:** Exact request/response JSON schemas for Delivery Challans, Invoices, Rental Invoices, Stock Transfers, CRM Account Widgets<br>• **Field-by-Field Mappings:** CTMS PostgreSQL schema $\leftrightarrow$ Zoho API attributes<br>• **Webhook Specifications:** Inbound HMAC-verified payment, customer, and invoice events<br>• **Rate Limiting & Error Recovery:** Leaky-bucket 80 req/min, BullMQ DLQ, exponential retry |
| **[09_AI_DRIVEN_DEVELOPMENT_PROTOCOLS_AND_BEST_PRACTICES.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/09_AI_DRIVEN_DEVELOPMENT_PROTOCOLS_AND_BEST_PRACTICES.md)** | • **The 7 AIDD Protocols:** Spec-First Anchoring, Test-Driven Generation (TDD for AI), Hermetic Mocking, Proof Artifacts, Micro-Commit Hygiene, Defensive State Machines, Self-Correction Loops<br>• **Red-Green-Refactor Loop for AI Pair Programming**<br>• **Unified Verification Runner (`verify_all.sh`)**<br>• Zero-regression sandboxes & property-based testing |
| **[10_DATA_MIGRATION_SECURITY_AND_DISASTER_RECOVERY_PLAN.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/10_DATA_MIGRATION_SECURITY_AND_DISASTER_RECOVERY_PLAN.md)** | • **Phase 0 Data Migration Strategy:** Rolling fleet gate retrofit (zero plant downtime) & CSV ingestion schemas<br>• **Enterprise RBAC Permission Matrix:** 7 user roles with granular authorization<br>• **High Availability & Disaster Recovery:** Multi-AZ replication, $\le 1\text{ min}$ RPO, $\le 15\text{ min}$ RTO, and offline network outage continuity |
| **[11_SYSTEM_UNDERSTANDING_AND_KNOWLEDGE_GRAPH.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/11_SYSTEM_UNDERSTANDING_AND_KNOWLEDGE_GRAPH.md)** | • **Domain Understanding & Conceptual Model:** Container vs Product vs Custodian triad<br>• **Enterprise Knowledge Graph (Ontology & Topology):** 13 core node types, directed predicates, and properties<br>• **Dgraph DQL & Cypher Schema:** Graph types, `@index` directives, and reverse edge navigation<br>• **Critical Graph Query Patterns:** 360° asset history, hospital medical oxygen batch recall, customer holding exposure, and route loss chains |
| **[12_API_KEYS_AND_MCP_SERVER_SPECIFICATION.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/12_API_KEYS_AND_MCP_SERVER_SPECIFICATION.md)** | • **API Key Gateway (`X-API-Key`):** Cryptographic high-entropy tokens (`ctms_live_...`), SHA-256 hash storage, granular scopes (`cylinders:read`, `dispatch:write`), IP whitelisting & Redis leaky-bucket rate limiter<br>• **Model Context Protocol (MCP) Server:** Native MCP over SSE & stdio for external AI agents (Claude, Gemini, Antigravity)<br>• **AI Tool Registry:** `query_cylinder_passport`, `verify_peso_safety`, `get_customer_holding_audit`, `trace_batch_contamination`, `reconcile_trip_manifest`<br>• **Live Context Resources:** `ctms://fleet/live-status`, `ctms://compliance/overdue-test`, `ctms://logistics/active-trips`, `ctms://zoho/sync-health` |
| **[13_HARDWARE_PERIPHERALS_AND_EXCEPTION_PLAYBOOKS.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/13_HARDWARE_PERIPHERALS_AND_EXCEPTION_PLAYBOOKS.md)** | • **Bluetooth Thermal Printers:** Exact ESC/POS hex commands (`1B 40`, `1D 21 11`, `1D 56 42 00` paper cut), 2D QR raster commands, 58mm/80mm e-DC & ECR layouts<br>• **Zebra & Chainway Rugged Scanners:** DataWedge (`com.ctms.app.ACTION_DATAWEDGE_SCAN`) and Chainway broadcast intents<br>• **Operational Exception Playbooks:** Damaged collar QR re-tagging with manager OTP, concurrent offline scan collision arbitration, and ghost cylinder yard audit protocol (`QUARANTINED_AUDIT`) |
| **[14_STATUTORY_PESO_REPORTING_AND_CUSTOMER_PORTAL.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/14_STATUTORY_PESO_REPORTING_AND_CUSTOMER_PORTAL.md)** | • **Statutory PESO Regulatory Engine:** Rule 35 compliance, volumetric water jacket calculations ($\le 10\%$ permanent expansion, $\le 5\%$ tare loss), Form III inspection certificates & Form IV daily logbook exports<br>• **B2B Customer Self-Service Portal:** Hospital & factory manager authentication, real-time cylinder holding matrix, emergency refill & pickup dispatch, NABH hospital audit document vault (medical O2 IP purity certs) |
| **[15_INFRASTRUCTURE_DOCKER_AND_CI_CD_PIPELINE.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/15_INFRASTRUCTURE_DOCKER_AND_CI_CD_PIPELINE.md)** | • **Containerized Topology:** PostgreSQL 16 + TimescaleDB + PostGIS, Redis 7 leaky-bucket cache, Dgraph standalone, and hermetic mock Zoho server<br>• **Local Orchestration:** `docker-compose.yml` configuration and healthcheck strategies<br>• **CI/CD Pipeline Blueprint:** GitHub Actions automated pull-request validation (`verify_all.sh`, pytest suites, Android Room DAO tests) |

---

## 🎨 Element-by-Element Design Guide & UI System

The user interface and hardware interaction designs are documented element-by-element in [`design-guide/`](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/):

| Guide Module | Design Elements & Tokens Specified |
| :--- | :--- |
| **[01_COLOR_SYSTEM_AND_THEMING.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/01_COLOR_SYSTEM_AND_THEMING.md)** | • Semantic UI tokens (WCAG 2.1 AAA contrast for direct sunlight)<br>• **PESO Statutory Cylinder Gas Colors:** Medical/Ind Oxygen (Black/White), Argon (Blue/Peacock Green), Nitrogen (Grey/Black), CO2 (Black/Silver)<br>• Ownership color chips: `COC` (Purple) vs `POC` (Ocean Blue) vs `VOC` (Warm Amber)<br>• Outdoor High-Contrast Sunlight Mode specifications |
| **[02_TYPOGRAPHY_AND_ICONS.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/02_TYPOGRAPHY_AND_ICONS.md)** | • Font pairing: Inter (UI) + **Roboto Mono** (Monospaced serials & pressure gauges)<br>• Tabular numbers (`tnum`) enforcement for zero-jitter counting<br>• Driver-grade accessibility scaling (up to 130%)<br>• Standard 24dp/32dp industrial Material Symbols |
| **[03_FOUNDATIONAL_UI_ELEMENTS.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/03_FOUNDATIONAL_UI_ELEMENTS.md)** | • **56dp Oversized Primary CTAs** (Glove-friendly touch targets)<br>• Numeric keypad optimizations with large digits<br>• Status badges for all 10 schema lifecycle states<br>• Persistent floating offline sync status indicator |
| **[04_SPECIALIZED_SCANNER_AND_HARDWARE_ELEMENTS.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/04_SPECIALIZED_SCANNER_AND_HARDWARE_ELEMENTS.md)** | • CameraX $250\times 250\text{ dp}$ targeting reticle with corner brackets & torch toggle<br>• Continuous batch scan counter HUD (`18 / 20 Delivered`)<br>• ToneGenerator audio frequencies (2,500 Hz pass vs 350 Hz alarm)<br>• Android Haptic vibration waveforms & UHF RFID bulk radar gauges |
| **[05_DOMAIN_CYLINDER_AND_CHALLAN_ELEMENTS.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/05_DOMAIN_CYLINDER_AND_CHALLAN_ELEMENTS.md)** | • Serialized Cylinder Asset Card with tare weight and gas badges<br>• PESO Hydro-Test Expiry Countdown gauge (Green $\rightarrow$ Amber $\rightarrow$ Crimson)<br>• Digital Proof of Delivery (POD) signature canvas with velocity smoothing<br>• Electronic Delivery Challan (e-DC) print and PDF layout |
| **[06_STATE_AND_INTERACTION_PATTERNS.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/06_STATE_AND_INTERACTION_PATTERNS.md)** | • **Full-Screen PESO Safety Hard Lockout** modal (Non-dismissible `403` block on expired test cylinders)<br>• Trip reconciliation truck balance delta table with missing asset highlights<br>• Spring-damping button micro-interactions |

---

## 🎯 Key Business Problems Solved

1. **Elimination of Unbilled Customer Cylinder Hoarding:**
   - Automatically tracks the exact duration every cylinder spends at a customer location.
   - Calculates daily rental fees past contract grace periods (e.g. 15 free days) and automatically posts itemized invoices directly into **Zoho Books** at month-end.
2. **Strict PESO & Statutory Safety Compliance:**
   - Enforces a hard digital interlock at the filling station manifold. Cylinders overdue for hydrostatic testing (5-year cycle) cannot be filled or dispatched under any circumstances.
3. **Dispute-Proof Deliveries & Collections:**
   - Drivers scan every cylinder delivered (filled) and retrieved (empty) using high-speed QR/RFID scanning.
   - Captures customer OTP or digital e-signature with GPS and time stamps.
   - Instantly generates and dispatches an **Electronic Delivery Challan (e-DC)** and **Electronic Cylinder Receipt (e-CR)** via WhatsApp/email.
4. **Party-Owned Cylinders (POC) vs Company Cylinders (COC):**
   - Distinct ownership ledgers ensure customer-owned cylinders brought in for refilling are never charged rental and are strictly returned to the same owner without getting mixed into the company fleet.
5. **Real-time Logistics & Truck Reconciliation:**
   - Reconciles cylinders loaded onto a truck at plant gate dispatch against confirmed customer drop-offs and retrieved empties upon truck return. Any missing cylinder is flagged before the driver departs.

---

## 🏗️ Codebase Architecture & Active Scaffolding

The platform foundation is actively implemented with full scaffolding across both backend and mobile client:

```
CylinderTrackingSystem/
├── backend/                          # Core API Server, Business Engines & Zoho Gateway
│   ├── src/
│   │   ├── api/routes.py             # REST API & Native MCP endpoints
│   │   ├── config.py                 # Central environment & database configuration
│   │   ├── database/migrations/      # 001_initial_schema.sql (18 tables), 002_timescale_setup.sql
│   │   ├── integrations/zoho/        # OAuth token manager & Zoho Books client with idempotency
│   │   ├── mcp/                      # Native MCP Server (tools & resources) & API Key authenticator
│   │   ├── modules/lifecycle/        # 10-state cylinder transition machine & audit log generator
│   │   ├── modules/rental/           # Progressive rental calculator with POC zero-rent exemption
│   │   └── modules/safety/           # PESO statutory pre-fill check (hydro-test 403 interlock)
│   └── tests/                        # Comprehensive unit & integration tests (100% Green)
└── android/                          # Native Android Mobile App (Kotlin + Compose)
    ├── app/
    │   ├── src/main/java/com/ctms/app/
    │   │   ├── data/local/           # Room Database, DAOs, Cylinder & OutboxMutation entities
    │   │   └── presentation/         # Jetpack Compose UI & MainActivity
    │   └── build.gradle.kts          # Android build script (Compose, Room, Hilt, WorkManager)
    └── build.gradle.kts              # Root Android Gradle build script
```

Run all backend verification tests:
```bash
python3 backend/tests/run_tests.py
```
