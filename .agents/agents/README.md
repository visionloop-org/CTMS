# Specialized Agent Swarm Architecture
## Cylinder Tracking Management System (CTMS)

This directory defines the specialized autonomous agent fleet powering the Agent-Driven Development (ADD) of CTMS. Each agent is a domain specialist possessing dedicated responsibilities, invariants, and handoff protocols.

---

## 🏛️ Swarm Topology & Hierarchy

```
                               +-----------------------------+
                               |     Agent Coordinator       |
                               |   (Swarm Orchestrator &     |
                               |    Backlog Gatekeeper)      |
                               +--------------+--------------+
                                              |
                   Dispatches Tasks & Enforces Invariants across Swarm
                                              |
         +-------------------+----------------+-------------------+-------------------+
         |                   |                |                   |                   |
         v                   v                v                   v                   v
+-----------------+ +-----------------+ +-------------+ +-----------------+ +-----------------+
|  Backend API    | |   Android App   | |  Database   | | Zoho Integration| |   Industrial    |
|     Agent       | |      Agent      | |Ledger Agent | |      Agent      | |  Design Agent   |
+--------+--------+ +--------+--------+ +------+------+ +--------+--------+ +--------+--------+
         |                   |                 |                 |                   |
         +-------------------+--------+--------+-----------------+-------------------+
                                      |
                                      v
                      +-------------------------------+
                      | Interaction Protocol Agent    |
                      | (API Gateway, Webhooks, MCP)  |
                      +---------------+---------------+
                                      |
                                      v
                      +-------------------------------+
                      |      Quality Test Agent       |
                      | (TDD, Mocks, Verification, QA)|
                      +-------------------------------+
```

---

## 📋 Domain Agent Directory

| Agent File | Role / Domain | Core Responsibilities | Key Invariants Enforced |
| :--- | :--- | :--- | :--- |
| **[01_zoho_integration_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/01_zoho_integration_agent.md)** | Zoho Ecosystem Specialist | Books, Inventory, CRM, Analytics & Sign integration; Document Triad (`salesorders` = IN, `invoices` = OUT, `deliverychallans` = Security/Rent). | Mandatory `Idempotency-Key`, 80 req/min leaky bucket, zero rental on POC cylinders. |
| **[02_android_app_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/02_android_app_agent.md)** | Native Android Specialist | Kotlin 2.0+, Jetpack Compose UI, Room SQLite DB, CameraX ML Kit scanning, WorkManager sync, Zebra/Chainway BLE RFID. | Offline-first write precedence, outbox event queueing, non-blocking UI thread. |
| **[03_backend_api_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/03_backend_api_agent.md)** | Core Backend Specialist | FastAPI async REST services, 10-stage lifecycle state machine, Celery background queues, and rental calculation math. | Strict state transition guardrails, PESO pre-fill safety lockout, multi-tenant isolation. |
| **[04_industrial_design_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/04_industrial_design_agent.md)** | UI/UX & Design Specialist | Industrial design guide tokens, WCAG AAA contrast, PESO statutory cylinder gas colors, 56dp glove-friendly CTAs. | Sunlight mode readability, tabular numbers (`tnum`) for zero-jitter, crimson 403 lockout modal. |
| **[05_interaction_protocol_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/05_interaction_protocol_agent.md)** | Integration & AI Gateway | Cryptographic API Key Gateway (`ctms_live_...`, SHA-256), Native Model Context Protocol (MCP) server, external ERPs. | Scope enforcement (`cylinders:read`, `dispatch:write`), MCP tool deterministic safety locks. |
| **[06_database_ledger_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/06_database_ledger_agent.md)** | Database & Graph Specialist | PostgreSQL 16 DDL, TimescaleDB weekly hypertable partitioning, compression policies, and Dgraph DQL graph queries. | Immutable append-only `cylinder_events` ledger, PostGIS geofencing, sub-50ms graph recalls. |
| **[07_agent_coordinator.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/07_agent_coordinator.md)** | Swarm Orchestrator | Task queue dispatching, cross-domain dependency resolution, architecture alignment, and `INDEX.md` maintenance. | The 5 Prime Invariants across all PRs, zero unresolved cross-domain schema breaking changes. |
| **[08_quality_test_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/08_quality_test_agent.md)** | QA & Test Harness Engineer | Test-driven development (TDD), hermetic mocking (`mock_zoho_server.py`), fast link auditing, and proof generation. | 100% green verification runs via `verify_all.sh`, zero regression in `.agents/proofs/`. |

---

## 🤝 Cross-Agent Handoff Protocol

When work spans multiple domains, agents hand off artifacts using this deterministic sequence:
1. **Schema & Contract First:** `Database Ledger Agent` or `Interaction Protocol Agent` defines tables/schemas.
2. **Backend Implementation:** `Backend API Agent` implements the business logic and state machine guardrails.
3. **External Sync & Mobile:** `Zoho Integration Agent` configures financial sync; `Android App Agent` builds the mobile UI/DB.
4. **Design Validation:** `Industrial Design Agent` verifies UI tokens and glove-friendly ergonomic compliance.
5. **Quality Gate:** `Quality Test Agent` runs hermetic test fixtures, verifies link integrity, and stamps `.agents/proofs/latest_verification.json`.
6. **Sign-off:** `Agent Coordinator` closes the task in [`TASK_QUEUE.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/TASK_QUEUE.md) and updates [`INDEX.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/INDEX.md).
