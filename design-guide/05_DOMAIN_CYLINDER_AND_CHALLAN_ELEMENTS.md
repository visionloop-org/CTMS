# Domain Cylinder & Challan UI Elements
## Serialized Asset Cards, PESO Expiry Countdown, e-DC Layout & Signature Canvas

---

## 1. Serialized Cylinder Asset Card

The **Cylinder Card** is the atomic data unit displayed in inventory lists, manifests, and scan confirmation sheets.

```
+--------------------------------------------------------------------------------------------------+
|  OX-47-009281                                       [ COC ]  [ OXYGEN MEDICAL (47L) ]            |
|  Collar: CL-8812    | Tare: 52.40 kg               Body: Black  | Collar: White                  |
+--------------------------------------------------------------------------------------------------+
|  Location: Truck MH-04-AB-1234 (Driver: Rajesh)    Batch: BAT-20261101-OX01 (Purity: 99.99%)     |
|  PESO Hydro Test: Valid until 30-Apr-2028          [ ● HYDRO VALID: 546 DAYS REMAINING ]         |
+--------------------------------------------------------------------------------------------------+
```

### Visual Specifications
- **Container:** Rounded surface card ($8\text{ dp}$ radius) with $1\text{ dp}$ border (`#E2E8F0`).
- **Header:**
  - Left: Serial Number in `Roboto Mono` ($18\text{ sp}$, Bold).
  - Right: Ownership Chip (`[ COC ]` Purple or `[ POC ]` Blue) and Gas Type Badge styled with statutory PESO colors.
- **Hydro-Test Expiry Countdown Gauge:**
  - $\ge 180\text{ Days Remaining:}$ Solid Green Indicator (`#15803D`)
  - $1\text{ to } 180\text{ Days:}$ Amber Warning Indicator (`#D97706`) with alert: *"Test due within 6 months"*
  - $\le 0\text{ Days (Overdue):}$ Flashing Crimson Indicator (`#DC2626`) with hard safety lock icon.

---

## 2. Digital Proof of Delivery (POD) Signature Canvas

The signature canvas captures the customer store manager's finger or stylus signature with **high-fidelity velocity smoothing**.

```
+--------------------------------------------------------------------------------------------------+
|  CUSTOMER PROOF OF DELIVERY — SIGNATURE                                                          |
|  Receiver: Amit Sharma (Store In-charge)   Phone: +91 98765 43210                                |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|               ~~~~~~~~~~~~~~~~~~~~ (Signature Path in Navy Ink) ~~~~~~~~~~~~~~                   |
|                                                                                                  |
|  X ─────────────────────────────────────────────────────────────────────────────────────────────  |
|  Watermark: 2026-11-01 10:14:22 IST | Lat: 19.076090, Long: 72.877726 | OTP: 4891 Verified       |
+--------------------------------------------------------------------------------------------------+
|  [ CLEAR SIGNATURE ]                                        [ CONFIRM & GENERATE E-CHALLAN ]     |
+--------------------------------------------------------------------------------------------------+
```

### Jetpack Compose Canvas Implementation Details
- **Stroke Width:** $3.5\text{ dp}$ with round caps and joints (`StrokeCap.Round`, `StrokeJoin.Round`).
- **Ink Color:** Deep Navy (`#0F172A`), avoiding generic black for enhanced authenticity.
- **Background:** Crisp White (`#FFFFFF`) with subtle dotted baseline.
- **Embedded Watermark:** Upon signature completion, the canvas embeds non-removable metadata into the exported SVG/PNG: `Timestamp`, `GPS Coordinates`, `Device ID`, and `Receiver Name`.

---

## 3. Electronic Delivery Challan (e-DC) Visual Layout

The generated document rendered on the driver app, printed on thermal paper, and pushed to Zoho Books:

```
+--------------------------------------------------------------------------------------------------+
|                         PREMIER INDUSTRIAL & MEDICAL GASES PVT LTD                               |
|                         Plot 44, TTC Industrial Area, Navi Mumbai                               |
|                         GSTIN: 27AAACP1234A1Z5 | PESO Lic: G/WC/MH/2020                          |
+--------------------------------------------------------------------------------------------------+
|  DELIVERY CHALLAN: DC-2026-008129                           DATE: 01-Nov-2026  10:14 IST         |
|  Customer: Apex Engineering Works                          Vehicle: MH-04-AB-1234                |
|  Delivery Address: Plot 12, Koperkhairane MIDC             Driver: Rajesh Kumar                  |
+--------------------------------------------------------------------------------------------------+
|  ITEM DESCRIPTION                  QTY     HSN CODE    UNIT RATE      TOTAL (INR)                |
|  • Medical Oxygen 7.0 m³ (47L)      10     28044090       350.00         3,500.00                |
|  • Industrial Argon 7.0 m³ (47L)     5     28042100       650.00         3,250.00                |
+--------------------------------------------------------------------------------------------------+
|  DELIVERED CYLINDER SERIALS (15 UNITS):                                                          |
|  OX-47-0912, OX-47-0915, OX-47-0922, OX-47-0931, OX-47-0940, OX-47-0945, OX-47-0951,            |
|  OX-47-0958, OX-47-0962, OX-47-0970, AR-47-0112, AR-47-0115, AR-47-0119, AR-47-0125, AR-47-0130 |
+--------------------------------------------------------------------------------------------------+
|  COLLECTED EMPTY CYLINDERS (12 UNITS):                                                           |
|  OX-47-0401, OX-47-0412, OX-47-0419, OX-47-0422, OX-47-0430, OX-47-0435, OX-47-0441, OX-47-0450 |
+--------------------------------------------------------------------------------------------------+
|  CUSTOMER SIGNATURE: [Attached Digital Sign]                VERIFICATION: OTP #4891 VERIFIED     |
|  GPS GEO-STAMP: 19.076090 N, 72.877726 E                   ZOHO BOOKS REF: INV-2026-009182       |
+--------------------------------------------------------------------------------------------------+
```
