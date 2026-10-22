# Agent-Driven Development (ADD) Guidelines
## Cylinder Tracking Management System (CTMS)

Welcome Agent! You are working on the **Cylinder Tracking Management System (CTMS)**, an enterprise-grade ERP and asset-tracking platform for high-pressure gas cylinders with native **Zoho Ecosystem** synchronization and a **Native Android Mobile App (Kotlin + Jetpack Compose)**.

---

## 1. Prime Invariants & Non-Negotiable Rules

When writing code, refactoring, or generating tests, you MUST uphold these 5 core invariants:

1. **PESO & Safety Zero-Tolerance (Filling Station Interlock):**
   - Under no circumstances may a cylinder overdue for hydrostatic stretch testing (`CurrentDate >= hydro_test_due_date`) be assigned to a filling batch or marked as `PLANT_FILLED`.
   - Any API or UI flow attempting to bypass this rule must return an explicit `403 FORBIDDEN` and log an auditable safety rejection.

2. **Immutable Scan Audit Trail:**
   - Every physical scan or status transition MUST append a row to `cylinder_events` containing `cylinder_id`, `event_type`, `to_status`, `to_location_id`, `actor_user_id`, `timestamp`, and `geo_point`. 
   - Never update or delete existing history rows in `cylinder_events`.

3. **Multi-Ownership Integrity (COC vs POC):**
   - **Party-Owned Cylinders (POC):** Must NEVER be charged rental or holding fees. Must be linked to `owner_customer_id` and strictly returned to the same customer upon refilling.
   - **Company-Owned Cylinders (COC):** Subject to rental slabs past the customer's agreed grace period.

4. **Offline-First Resilience (Android Native):**
   - The Android client must function without internet connectivity. All deliveries, collections, damage photos, and signatures must commit immediately to local Room database entities and enqueue an outbox mutation in `outbox_mutations`.
   - Never block the UI thread on network calls or assume active connectivity.

5. **Financial Idempotency (Zoho Synchronization):**
   - Every transaction pushed to Zoho Books, Inventory, or CRM must pass an explicit `Idempotency-Key` (e.g. `dc_2026_008129_books_v1`).
   - Duplicate delivery submissions must never produce duplicate tax invoices or challans.

6. **Strict Modular File Limit (< 1,000 Lines):**
   - Under no circumstances may any file (source code, configuration, SQL migration, or documentation) exceed **1,000 lines**.
   - Any module approaching this threshold must be proactively decomposed into focused, single-responsibility components and sub-modules.

7. **Strict Dark Theme Only (Industrial & Sunlight Contrast):**
   - The Android mobile application must strictly enforce a high-contrast industrial Dark Theme across all screens and components.
   - Light theme is explicitly prohibited to preserve battery on rugged OLED handhelds and guarantee outdoor legibility for delivery drivers and plant operators.

---

## 2. Agent Workflow & Execution Protocol

When assigned a task or executing a goal:

```
[ 1. Pick Task ] ───> [ 2. Read Relevant Specs ] ───> [ 3. Plan & Test First ]
      │                                                         │
      ▼                                                         ▼
[ 6. Update Queue ] <─── [ 5. Run Verification ] <─── [ 4. Implement Code ]
```

1. **Task Selection:**
   - Inspect [`TASK_QUEUE.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/TASK_QUEUE.md) to locate the active story/task.
2. **Context Intake:**
   - Read the corresponding technical specification in [`docs/`](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/) before writing code:
     - Architecture & Tech Stack: [`docs/01_SYSTEM_REQUIREMENTS_AND_ARCHITECTURE.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/01_SYSTEM_REQUIREMENTS_AND_ARCHITECTURE.md)
     - Business Logic & State Machines: [`docs/02_CORE_FUNCTIONAL_MODULES.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/02_CORE_FUNCTIONAL_MODULES.md)
     - Zoho APIs & Data Mapping: [`docs/03_ZOHO_ECOSYSTEM_INTEGRATION_SPEC.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/03_ZOHO_ECOSYSTEM_INTEGRATION_SPEC.md)
     - Schema & DDL: [`docs/04_DATA_MODELS_AND_SCHEMA_DESIGN.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/04_DATA_MODELS_AND_SCHEMA_DESIGN.md)
     - REST APIs & Mobile Sync: [`docs/05_API_SPECIFICATION_AND_OFFLINE_SYNC.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/05_API_SPECIFICATION_AND_OFFLINE_SYNC.md)
     - Native Android App: [`docs/07_NATIVE_ANDROID_APP_SPECIFICATION.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/07_NATIVE_ANDROID_APP_SPECIFICATION.md)
     - Zoho API Payloads: [`docs/08_ZOHO_API_INTERACTIONS_AND_PAYLOAD_SPECIFICATION.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/08_ZOHO_API_INTERACTIONS_AND_PAYLOAD_SPECIFICATION.md)
     - AI Development Protocols: [`docs/09_AI_DRIVEN_DEVELOPMENT_PROTOCOLS_AND_BEST_PRACTICES.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/09_AI_DRIVEN_DEVELOPMENT_PROTOCOLS_AND_BEST_PRACTICES.md)
3. **Red-Green-Refactor Protocol:**
   - Write unit/integration tests asserting expected behavior *before* implementing functionality.
   - Run tests to observe failure, implement minimal code, and re-run tests to observe green pass.
   - Test against hermetic mocks (e.g. `scripts/mock_zoho_server.py`, Room in-memory DB) to avoid external dependencies.
4. **Implementation Standards:**
   - **Android App:** Kotlin 2.0+, Jetpack Compose, Material 3, Room, Hilt, Coroutines/StateFlow, WorkManager. Follow Clean Architecture (Data -> Domain -> Presentation).
   - **Backend API:** Modular architecture, TypeScript or Go, Strict schema validation, TimescaleDB/PostgreSQL queries with appropriate indexes.
5. **Verification & Proof Artifacts:**
   - Never declare a task complete without executing automated unit tests, lint checks, or dry-run scripts.
   - Capture test execution logs as proof of correctness before updating [`TASK_QUEUE.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/TASK_QUEUE.md).
6. **Task Completion:**
   - Check off the completed item in [`TASK_QUEUE.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/TASK_QUEUE.md) with timestamp and test evidence.

---

## 3. Directory Layout & Project Structure

```text
CylinderTrackingSystem/
├── .agents/                          # Customization root for AI agents
│   ├── rules/                        # Contextual guidelines and constraints
│   │   └── agent_workflow.md         # Workflow and testing rules
│   └── skills/                       # Specialized runbooks and cheatsheets
│       ├── zoho-sync-engine/         # Testing and mocking Zoho APIs
│       └── android-device-testing/   # Testing Android Room, CameraX, and WorkManager
├── android/                          # Native Android App (Kotlin + Compose)
│   ├── app/
│   │   ├── src/main/java/com/ctms/app/
│   │   │   ├── data/                 # Room DB, DAOs, Entities, Retrofit Services
│   │   │   ├── domain/               # Use cases, Business Models, Validators
│   │   │   ├── presentation/         # Jetpack Compose UI Screens, ViewModels
│   │   │   └── worker/               # WorkManager Background Sync Workers
│   │   └── build.gradle.kts
│   └── build.gradle.kts
├── backend/                          # Core API Server & Zoho Integration Gateway
│   ├── src/
│   │   ├── modules/                  # Cylinders, Batches, Trips, Challans, Rental
│   │   ├── integrations/zoho/        # Books, Inventory, CRM, Analytics Clients
│   │   └── database/                 # Migrations & Seeds
│   └── package.json
├── docs/                             # Exhaustive Technical & Architectural Specs
├── scripts/                          # Agent automation helpers, mocks, seeders
├── AGENTS.md                         # This file: Agent guidelines and prime invariants
├── GEMINI.md                         # Gemini CLI & IDE instructions
├── README.md                         # Master repository index
└── TASK_QUEUE.md                     # Agent work tracking board
```

---

## 4. Useful Slash Commands for Pairing with Users

- `/goal`: Run long-running autonomous development sessions.
- `/plan`: Generate structured step-by-step implementation plans before touching code.
- `/grill-me`: Interview the user to clarify edge cases before making irreversible design decisions.
