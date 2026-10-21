# CTMS Engineering Task Queue & Agent Work Board

This backlog drives autonomous agent and developer tasks. Each task defines clear **Acceptance Criteria** and **Verification Commands**.

---

## 🎯 Active Milestone: Phase 1 — Core Schema, Outbox & Zoho Gateway

### Epic 1: Database Architecture & Migrations
- [x] **TASK-101: PostgreSQL Database Migration Scripts** [Completed: 2026-10-21]
  - **Spec Reference:** `docs/04_DATA_MODELS_AND_SCHEMA_DESIGN.md`
  - **Details:** Write executable SQL migration files for `cylinders`, `bundles`, `customers`, `rental_slabs`, `filling_batches`, `trips`, `delivery_challans`, `cylinder_events`, and `zoho_sync_outbox`.
  - **Verification Evidence:** Created `backend/src/database/migrations/001_initial_schema.sql` and `002_timescale_setup.sql`. Verified all 18 tables, enums, indexes, and constraints.
  
- [ ] **TASK-102: TimescaleDB Hypertable & Scan Event Ingest Benchmark**
  - **Spec Reference:** `docs/04_DATA_MODELS_AND_SCHEMA_DESIGN.md`
  - **Details:** Convert `cylinder_events` into a TimescaleDB hypertable partitioned by week; write batch insert benchmark script simulating 5,000 scans/sec.
  - **Verification:** Execute `scripts/benchmark_events.py` and verify throughput $>2,000\text{ ops/sec}$.

---

### Epic 2: Core Safety & State Machine Services
- [x] **TASK-201: Pre-Fill Safety Validation Engine** [Completed: 2026-10-21]
  - **Spec Reference:** `docs/02_CORE_FUNCTIONAL_MODULES.md`
  - **Details:** Implement the pre-fill check service validating hydrostatic testing due date (`hydro_test_due_date`), gas compatibility, and tare weight loss tolerance.
  - **Acceptance Criteria:** Reject any cylinder where `NOW() >= hydro_test_due_date` with HTTP 403 and write safety violation to audit log.
  - **Verification Evidence:** `backend/src/modules/safety/peso_engine.py` passes 4/4 tests in `test_peso_safety.py` (overdue 403, valid pass, tare loss > 5% quarantine, gas mismatch 400).

- [x] **TASK-202: 10-State Cylinder Lifecycle Transition Validator** [Completed: 2026-10-21]
  - **Spec Reference:** `docs/02_CORE_FUNCTIONAL_MODULES.md`
  - **Details:** Implement deterministic state machine guardrails (e.g., prevent transitioning directly from `PLANT_EMPTY` to `DELIVERED` without `FILLING` and `GATE_OUTWARD`).
  - **Verification Evidence:** `backend/src/modules/lifecycle/state_machine.py` passes 3/3 tests in `test_state_machine.py` asserting deterministic progression, illegal transition prevention, and immutable event ledger creation.

---

### Epic 3: Zoho Integration Layer
- [x] **TASK-301: Zoho OAuth 2.0 Token Manager with Auto-Refresh** [Completed: 2026-10-21]
  - **Spec Reference:** `docs/03_ZOHO_ECOSYSTEM_INTEGRATION_SPEC.md`
  - **Details:** Implement a background worker maintaining active Zoho OAuth tokens with caching and automatic rotation before expiration.
  - **Verification Evidence:** Implemented in `backend/src/integrations/zoho/oauth.py` with auto-refresh mechanism.

- [x] **TASK-302: Zoho Books Delivery Challan & Sales Invoice Dispatcher** [Completed: 2026-10-21]
  - **Spec Reference:** `docs/03_ZOHO_ECOSYSTEM_INTEGRATION_SPEC.md`
  - **Details:** Queue dispatcher generating Delivery Challans and Tax Invoices in Zoho Books with `Idempotency-Key` and serialized items.
  - **Verification Evidence:** `backend/src/integrations/zoho/books_client.py` passes 2/2 tests in `test_zoho_integration.py` enforcing mandatory Idempotency-Key.

- [x] **TASK-303: Midnight Rental Calculation & Automated Invoicing Engine** [Completed: 2026-10-21]
  - **Spec Reference:** `docs/02_CORE_FUNCTIONAL_MODULES.md` & `docs/03_ZOHO_ECOSYSTEM_INTEGRATION_SPEC.md`
  - **Details:** Scheduled job calculating progressive holding days, grace periods, and generating monthly consolidated invoices in Zoho Books with day-by-day audit PDF attachments.
  - **Verification Evidence:** `backend/src/modules/rental/calculator.py` passes 3/3 tests in `test_rental_engine.py` verifying strict POC zero-rental exemption, progressive slab math, and consolidated customer batches.

---

### Epic 4: Native Android Mobile Client (Kotlin + Compose)
- [x] **TASK-401: Android Project Scaffolding & Room DB Entities** [Completed: 2026-10-21]
  - **Spec Reference:** `docs/07_NATIVE_ANDROID_APP_SPECIFICATION.md`
  - **Details:** Initialize Android project structure with Gradle Kotlin DSL, Room database, DAOs, and `outbox_mutations` entity.
  - **Verification Evidence:** Scaffolding created in `android/` with `build.gradle.kts`, `settings.gradle.kts`, `app/build.gradle.kts`, `AppDatabase.kt`, `CylinderCacheEntity.kt`, `OutboxMutationEntity.kt`, and DAOs.

- [ ] **TASK-402: CameraX & Google ML Kit Continuous Scanner UI**
  - **Spec Reference:** `docs/07_NATIVE_ANDROID_APP_SPECIFICATION.md`
  - **Details:** Build Jetpack Compose full-screen camera viewfinder with real-time multi-code 2D QR scanning, 500ms debounce, beep ToneGenerator, and tactile haptic vibration.
  - **Verification:** Test scanner composable with mock CameraX ImageAnalysis stream.

- [ ] **TASK-403: Offline Outbox Queue & Jetpack WorkManager Sync Worker**
  - **Spec Reference:** `docs/07_NATIVE_ANDROID_APP_SPECIFICATION.md`
  - **Details:** Implement `SyncWorker` processing queued mutations on network reconnect with exponential backoff and idempotency headers.
  - **Verification:** Run WorkManager test asserting offline mutations sync upon network connection trigger.

- [ ] **TASK-404: Digital Proof of Delivery (POD) Canvas & e-DC Generator**
  - **Spec Reference:** `docs/07_NATIVE_ANDROID_APP_SPECIFICATION.md`
  - **Details:** Touch-enabled signature canvas in Compose, receiver name/phone inputs, SMS/WhatsApp OTP modal, and thermal receipt print layout.
  - **Verification:** Test signature capture to SVG/PNG export and PDF challan rendering.

---

### Epic 5: External Developer API Gateway & MCP Server for AI Agents
- [x] **TASK-501: Cryptographic API Key Authenticator & Rate Limiting Middleware** [Completed: 2026-10-21]
  - **Spec Reference:** `docs/12_API_KEYS_AND_MCP_SERVER_SPECIFICATION.md`
  - **Details:** Implement FastAPI middleware for `X-API-Key` authentication validating `ctms_live_...` tokens via SHA-256 hash lookup in `tenant_api_keys`, checking granular scopes (`cylinders:read`, `dispatch:write`), CIDR IP filters, and leaky-bucket rate limiting.
  - **Verification Evidence:** `backend/src/mcp/auth.py` verified with unit tests for SHA-256 validation, RBAC scopes, and token formats.

- [x] **TASK-502: Native Model Context Protocol (MCP) Server Implementation** [Completed: 2026-10-21]
  - **Spec Reference:** `docs/12_API_KEYS_AND_MCP_SERVER_SPECIFICATION.md`
  - **Details:** Implement MCP Server over SSE (`/mcp/sse`) and stdio transport with tools (`query_cylinder_passport`, `verify_peso_safety`, `get_customer_holding_audit`, `trigger_zoho_books_sync`) and streaming resources (`ctms://fleet/live-status`, `ctms://compliance/overdue-test`).
  - **Verification Evidence:** `backend/src/mcp/server.py` verified with unit tests in `test_api_keys_and_mcp.py` asserting tool calls and live resources.

---

### Epic 6: Hardware Peripherals & Operational Exception Playbooks
- [ ] **TASK-601: Bluetooth ESC/POS Thermal Print Engine**
  - **Spec Reference:** `docs/13_HARDWARE_PERIPHERALS_AND_EXCEPTION_PLAYBOOKS.md`
  - **Details:** Implement driver byte layout generator for 58mm (32-col) and 80mm (48-col) portable printers with bold, double-height, 2D QR raster commands, and partial cut `1D 56 42 00`.
  - **Verification:** Execute test asserting raw byte sequence matches ESC/POS specification and validates checksum.

- [ ] **TASK-602: Zebra & Chainway Rugged Scanner Broadcast Receivers**
  - **Spec Reference:** `docs/13_HARDWARE_PERIPHERALS_AND_EXCEPTION_PLAYBOOKS.md`
  - **Details:** Implement Android `BroadcastReceiver` listening to `com.ctms.app.ACTION_DATAWEDGE_SCAN` (`data_string`) and `com.android.server.scannerservice.broadcast` (`scannerdata`) for hardware trigger scanning.
  - **Verification:** Unit test broadcast receiver with mock intents simulating hardware laser gun scans.

- [ ] **TASK-603: Collar Tag Re-Binding & Yard Quarantined Audit Workflow**
  - **Spec Reference:** `docs/13_HARDWARE_PERIPHERALS_AND_EXCEPTION_PLAYBOOKS.md`
  - **Details:** Implement damaged tag re-binding API with manager OTP authorization, concurrent scan collision arbitration (geofence + timestamp check), and `QUARANTINED_AUDIT` state handler.
  - **Verification:** Integration test verifying tag re-bind preserves 5-year event history and arbitration halts conflicting driver trips.

---

### Epic 7: Statutory PESO Compliance & Customer Self-Service Portal
- [ ] **TASK-701: PESO Rule 35 Validation & Form III / IV Exporters**
  - **Spec Reference:** `docs/14_STATUTORY_PESO_REPORTING_AND_CUSTOMER_PORTAL.md`
  - **Details:** Implement hydrostatic stretch test validation ($\le 10\%$ permanent/total expansion ratio, $\le 5\%$ tare loss rejection) and automated Form III PDF & Form IV Excel logbook generators.
  - **Verification:** Unit test asserting plastic deformation $>10\%$ triggers permanent condemnation and Form III PDF renders with valid SHA-256 HMAC signature.

- [ ] **TASK-702: B2B Customer Portal (Holding Balance, Refill Dispatch & NABH Vault)**
  - **Spec Reference:** `docs/14_STATUTORY_PESO_REPORTING_AND_CUSTOMER_PORTAL.md`
  - **Details:** Implement Next.js web portal with passwordless magic link/OTP auth, live cylinder holding matrix (COC vs POC), online refill & pickup orders, and hospital NABH compliance dossier export.
  - **Verification:** End-to-end test verifying customer portal retrieves live holding balances and hospital purity certificates.

---

### Epic 8: Infrastructure Orchestration & Continuous Integration
- [ ] **TASK-801: Docker Compose Local Infrastructure Orchestration**
  - **Spec Reference:** `docs/15_INFRASTRUCTURE_DOCKER_AND_CI_CD_PIPELINE.md`
  - **Details:** Maintain `docker-compose.yml` orchestrating PostgreSQL 16 (TimescaleDB), Redis 7, Dgraph standalone, and hermetic mock Zoho server with automated container healthchecks.
  - **Verification:** Run `docker compose config` to validate syntax and verify container startup.

- [ ] **TASK-802: Automated CI/CD Pipeline & Quality Gate Runner**
  - **Spec Reference:** `docs/15_INFRASTRUCTURE_DOCKER_AND_CI_CD_PIPELINE.md`
  - **Details:** Configure GitHub Actions workflow running static link audits, backend pytest suites, Android Room DAO tests, and proof artifact emission.
  - **Verification:** Execute `bash scripts/verify_all.sh` asserting zero link failures and clean proof artifact generation.


