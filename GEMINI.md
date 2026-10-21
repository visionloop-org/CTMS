# Gemini Agent Instructions
## Cylinder Tracking Management System (CTMS)

Refer to [AGENTS.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/AGENTS.md) for complete instructions, project invariants, and development guidelines.

### Quick Invariants:
1. **Safety Interlock:** Never permit filling cylinders past their PESO hydrostatic testing due date (`hydro_test_due_date`).
2. **Offline-First Android App:** Native Kotlin + Jetpack Compose + Room SQLite. All mutations must write locally first to `outbox_mutations`.
3. **Multi-Ownership:** Never bill rental on Party-Owned Cylinders (POC).
4. **Zoho Financial Sync:** Always use idempotency keys on Zoho Books / CRM / Inventory API calls.
5. **Immutable Event Log:** Every cylinder movement appends to `cylinder_events`.
6. **Strict Modular Limit:** No file may exceed 1,000 lines. Proactively decompose and refactor modules.
