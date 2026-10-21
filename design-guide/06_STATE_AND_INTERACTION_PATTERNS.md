# State & Interaction Patterns
## Safety Interlock Modals, Trip Reconciliation Delta Tables & Micro-Interactions

---

## 1. Full-Screen PESO Safety Hard Lockout Pattern

When an operator scans a cylinder overdue for hydrostatic stretch testing or flagged for wall thickness failure during pre-fill inspection, the application triggers a **Full-Screen Hard Lockout Modal**.

```
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|                                        /!\ SAFETY INTERLOCK                                      |
|                                                                                                  |
|                                    FILLING & DISPATCH FORBIDDEN                                  |
|                                                                                                  |
|   Cylinder: OX-47-1044                                               Status: REJECTED            |
|   Statutory Test Due Date: 15-Sep-2026                               Overdue By: 47 Days         |
|                                                                                                  |
|   PESO REGULATION VIOLATION: Under Gas Cylinders Rules, filling an overdue vessel is illegal     |
|   and poses catastrophic rupture risk.                                                           |
|                                                                                                  |
|   ACTION REQUIRED: Divert cylinder immediately to Hydro Testing Yard (Bay 4).                    |
|                                                                                                  |
|   [  PRINT QUARANTINE ROUTING SLIP  ]             [  SCAN NEXT CYLINDER (DISMISS LOCK)  ]        |
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
```

### Visual & Behavioral Invariants:
1. **Background:** Stark Solid Crimson (`#991B1B`) with high-contrast white and amber typography.
2. **Non-Dismissible:** Tapping outside the dialog or pressing the Android hardware Back button is blocked (`onDismissRequest = {}`).
3. **Audio Alarm:** Continuous 3-pulse CDMA emergency alert tone (`ToneGenerator.TONE_CDMA_EMERGENCY_RINGBACK`).
4. **Permanent Audit Log:** Dismissing or routing the cylinder appends an auditable safety rejection record to `cylinder_events`.

---

## 2. Trip Reconciliation Variance Delta Table

Upon return of a delivery vehicle to the plant gate, the dispatcher reviews the physical truck balance against digital manifests:

```
+---------------------------------------------------------------------------------------------------+
| METRIC CATEGORY                          | EXPECTED COUNT | VERIFIED SCANNED | VARIANCE / DELTA   |
+------------------------------------------+----------------+------------------+--------------------+
| 1. Dispatched Outward (Filled)           |      120       |       120        |  0 (Matched)       |
| 2. Delivered at Customers (e-DCs)        |       90       |        90        |  0 (Matched)       |
| 3. Retained Undelivered (Filled on Truck)|       30       |        30        |  0 (Matched)       |
| 4. Empties Collected from Clients (ECRs) |       80       |        80        |  0 (Matched)       |
+------------------------------------------+----------------+------------------+--------------------+
| 5. PHYSICAL TRUCK BED COUNT (Retained + E) |     110      |       106        | -4 MISSING CYLINDERS|
+------------------------------------------+----------------+------------------+--------------------+
| [!] DISCREPANCY DETECTED: 4 Cylinders missing from vehicle. Supervisor clearance required.        |
| Missing Serials: OX-47-0940, OX-47-0945, AR-47-0112, AR-47-0115                                  |
+---------------------------------------------------------------------------------------------------+
```

### Visual Specifications
- **Balanced State (Delta = 0):** Row highlighted in Soft Green (`#DCFCE7`), text in Forest Green (`#15803D`) with `check_circle` icon. Driver cleared for exit.
- **Unaccounted Loss (Delta < 0):** Row highlighted in Stark Crimson (`#FEE2E2`), text in Dark Red (`#991B1B`). Gate release button disabled until driver/supervisor notes are submitted.

---

## 3. Micro-Interactions & Animated Transitions

To ensure the application feels tactile and responsive under field conditions:
1. **Button Tap Response:** Instant spring-based scale depression down to $96\%$ with haptic vibration upon finger down, rebounding to $100\%$ on release (`spring(dampingRatio = 0.6f)`).
2. **Carousel Chip Insertion:** As codes are scanned continuously, newly added chips slide in from the right edge with a $150\text{ ms}$ slide-and-fade animation.
3. **Batch Target Completion:** When the last cylinder of a delivery batch is scanned (e.g., reaching $20 / 20$), the progress bar changes from Deep Cobalt (`#1E40AF`) to Emerald Green (`#16A34A`), triggering an ascending 3-tone chime.
