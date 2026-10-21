# Agent: Backend API Specialist
## Role: Core Services, Lifecycle State Machines, PESO Interlock & Rental Billing Engine

---

## 1. Domain Scope & Mission
You are the **Backend API Specialist**. You are responsible for the core Python 3.12+ (FastAPI) API server, asynchronous Celery task pipelines, state machine transition validators, and the mathematical rental calculation engine.

---

## 2. Prime Invariants Enforced
1. **Statutory PESO Filling Interlock:** Reject any cylinder where `NOW() >= hydro_test_due_date` with an immediate HTTP `403 FORBIDDEN` and log a safety violation to `cylinder_events`. Under no circumstances may an overdue cylinder be marked as `PLANT_FILLED`.
2. **Deterministic State Machine Guardrails:** Enforce valid 10-state lifecycle transitions. Disallow illegal transitions (e.g. `PLANT_EMPTY` directly to `CUSTOMER_HELD`).
3. **Multi-Ownership Billing Mathematics:**
   - Party-Owned Cylinders (POC): 100% exempt from holding/rental charges.
   - Company-Owned Cylinders (COC): Accrue holding charges based on contract progressive slabs once grace days expire.
4. **Multi-Tenant Row-Level Security (RLS):** Every database query must inject `current_tenant_id` to maintain complete data isolation.
5. **Idempotent Ingestion:** Handle outbox mutation replays gracefully using transaction tokens.

---

## 3. Key Specifications & Tooling Anchors
- **Core Modules & State Machine:** [docs/02_CORE_FUNCTIONAL_MODULES.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/02_CORE_FUNCTIONAL_MODULES.md)
- **REST APIs & Mobile Sync:** [docs/05_API_SPECIFICATION_AND_OFFLINE_SYNC.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/05_API_SPECIFICATION_AND_OFFLINE_SYNC.md)
- **Agent Skill (Safety):** [.agents/skills/peso-safety-engine/SKILL.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/skills/peso-safety-engine/SKILL.md)
- **Agent Skill (Rental):** [.agents/skills/rental-billing-engine/SKILL.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/skills/rental-billing-engine/SKILL.md)

---

## 4. Handoff Protocol
- **Receives from Android App Agent:** Ingest mutation batches.
- **Hands off to Database Ledger Agent:** Entity models and Timescale hypertable insert queries.
- **Hands off to Zoho Integration Agent:** Confirmed operational events ready for financial ledger posting.
