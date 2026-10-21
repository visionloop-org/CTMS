# Master Design Guide & Element System
## Cylinder Tracking Management System (CTMS)

---

## 1. Design System Vision

The **Cylinder Tracking Management System (CTMS)** design system is engineered specifically for **industrial, field, and logistics conditions**. 

Unlike standard consumer apps, gas cylinder operations occur in challenging physical environments:
- **Direct Sunlight & Glare:** Drivers operating on flatbed trucks and open loading bays need high-contrast, non-reflective visual hierarchy.
- **Gloves & Grease:** Plant yard workers wearing industrial protective gloves require large touch targets (minimum $48\times 48\text{ dp}$, recommended $56\text{ dp}$).
- **High-Velocity Operations:** Field workers scan 100+ cylinders in minutes, requiring instant tactile, acoustic, and visual feedback without UI latency.
- **Safety Criticality:** PESO statutory testing dates and gas type identification must never be ambiguous or misread.

```
       +-------------------------------------------------------------+
       |               CTMS ELEMENT DESIGN SYSTEM                    |
       +-------------------------------------------------------------+
                                      │
         +----------------------------+----------------------------+
         │                            │                            │
         v                            v                            v
+------------------+         +------------------+         +------------------+
| Visual Tokens    |         | Core UI Elements |         | Domain Elements  |
| • Sunlight Mode  |         | • 56dp Touch CTA |         | • Cylinder Cards |
| • PESO Gas Colors|         | • Number Pads    |         | • QR Reticle     |
| • Mono Serials   |         | • Status Badges  |         | • e-Sign Canvas  |
+------------------+         +------------------+         +------------------+
```

---

## 2. Directory Structure of the Design Guide

This design guide is organized element-by-element across modular specification files:

| Document | Element Category & Scope |
| :--- | :--- |
| **[`01_COLOR_SYSTEM_AND_THEMING.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/01_COLOR_SYSTEM_AND_THEMING.md)** | Semantic Color Tokens, High-Contrast Outdoor Sunlight Mode, Dark Mode, and Statutory PESO Cylinder Gas Color Standards (Oxygen, Argon, Nitrogen, CO2, Acetylene). |
| **[`02_TYPOGRAPHY_AND_ICONS.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/02_TYPOGRAPHY_AND_ICONS.md)** | Typography scale, Monospaced serial number fonts (`Roboto Mono` / `JetBrains Mono`), high-legibility tabular figures, and standard Material Symbol iconography. |
| **[`03_FOUNDATIONAL_UI_ELEMENTS.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/03_FOUNDATIONAL_UI_ELEMENTS.md)** | Buttons, Primary CTAs ($56\text{ dp}$), Input Fields, Numerical Steppers, Modal Sheets, Status Badges, and Offline Floating Indicators. |
| **[`04_SPECIALIZED_SCANNER_AND_HARDWARE_ELEMENTS.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/04_SPECIALIZED_SCANNER_AND_HARDWARE_ELEMENTS.md)** | CameraX Reticle, Target Guides, Continuous Batch Counter, ToneGenerator acoustic frequencies, and Android Haptic vibration patterns. |
| **[`05_DOMAIN_CYLINDER_AND_CHALLAN_ELEMENTS.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/05_DOMAIN_CYLINDER_AND_CHALLAN_ELEMENTS.md)** | Serialized Cylinder Cards, Ownership Chips (`COC` vs `POC`), Hydro-Test Expiry Gauges, Electronic Delivery Challans (e-DC), and e-Signature Canvas. |
| **[`06_STATE_AND_INTERACTION_PATTERNS.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/06_STATE_AND_INTERACTION_PATTERNS.md)** | Micro-interactions, Full-Screen PESO Safety Hard Locks (`403 FORBIDDEN`), Trip Reconciliation Delta Tables, and Network Sync State Progression. |

---

## 3. Schema & Model Consistency Mandate

All visual badges, filters, chips, and color codings in this design guide **strictly match** the database schema enums defined in [`docs/04_DATA_MODELS_AND_SCHEMA_DESIGN.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/04_DATA_MODELS_AND_SCHEMA_DESIGN.md):
- **Cylinder Statuses:** `PLANT_EMPTY`, `UNDER_INSPECTION`, `QUARANTINED_DAMAGED`, `FILLING`, `PLANT_FILLED`, `IN_TRANSIT_OUTWARD`, `CUSTOMER_HELD`, `IN_TRANSIT_INWARD`, `MAINTENANCE_TESTING`, `SCRAPPED`.
- **Ownership:** `COC` (Company Owned), `POC` (Party / Customer Owned), `VOC` (Vendor Owned).
- **Gas Types:** `OXYGEN_MEDICAL`, `OXYGEN_INDUSTRIAL`, `NITROGEN_COMMERCIAL`, `NITROGEN_UHP`, `ARGON`, `CO2`, `DISSOLVED_ACETYLENE`, `HELIUM`, `HYDROGEN`, `LPG_COMMERCIAL`.
