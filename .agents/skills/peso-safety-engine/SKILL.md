---
name: peso-safety-engine
description: Runbook and test protocols for verifying PESO statutory safety interlocks, hydrostatic stretch testing due dates, tare weight loss thresholds, and filling plant lockout mechanisms in CTMS.
---

# PESO Statutory Safety Engine Runbook

## Overview
This skill guides the implementation, validation, and testing of **PESO / SMPV compliance interlocks** in CTMS.

### Invariant: Prime Rule #1
> **Under no circumstances may a cylinder overdue for hydrostatic stretch testing (`CurrentDate >= hydro_test_due_date`) be assigned to a filling batch or marked as `PLANT_FILLED`. Any attempt must return an immediate HTTP `403 FORBIDDEN` and log an auditable safety rejection.**

---

## 1. Safety Validation Rules

### 1.1 Hydrostatic Testing Due Date Interlock
- **Rule:** Seamless steel cylinders (IS 7285) require hydrostatic stretch testing every 5 years; toxic/corrosive gas cylinders require testing every 2 years.
- **Formula:** `days_remaining = hydro_test_due_date - CURRENT_DATE`
- **Actions:**
  - `days_remaining > 30`: **PASS** (Normal green status).
  - `0 <= days_remaining <= 30`: **WARNING** (Amber warning banner; permits filling but schedules immediate re-test upon return).
  - `days_remaining < 0`: **HARD LOCKOUT** (Crimson lockout; HTTP `403 FORBIDDEN`; blocks filling batch entry).

### 1.2 Tare Weight Loss Verification
- **Rule:** Before filling, tare weight is measured. If measured tare weight has decreased by $>5\%$ from original stamped tare weight (`stamped_tare_weight_kg`), the cylinder wall has thinned due to internal/external corrosion.
- **Formula:** `tare_loss_percent = ((stamped_tare - measured_tare) / stamped_tare) * 100`
- **Action:** If `tare_loss_percent > 5.0`, cylinder status transitions to `QUARANTINED` for ultrasonic wall thickness inspection.

### 1.3 Gas Compatibility & Collar Coding
- **Rule:** Cylinders must never be refilled with a gas type differing from their certified service gas (`certified_gas_type`) without formal purging, valve replacement, and statutory recertification.
- **Action:** Attempting to fill an `OXYGEN_MEDICAL` cylinder with `ARGON` or `NITROGEN` raises `IncompatibleGasTypeException`.

---

## 2. Test Verification Scripts

When testing pre-fill safety endpoints:

```bash
# Test 1: Verify expired cylinder rejection
curl -s -X POST http://localhost:8000/api/v1/filling/pre-check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ctms_live_test_key" \
  -d '{"cylinder_id": "test-expired-cyl-uuid", "batch_gas_type": "OXYGEN_INDUSTRIAL"}'
# Expected Output: {"status": "REJECTED", "error_code": "PESO_HYDRO_TEST_OVERDUE", "http_status": 403}
```
