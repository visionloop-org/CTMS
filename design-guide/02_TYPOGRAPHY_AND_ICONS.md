# Typography, Numerals & Iconography System
## Field Legibility, Monospaced Serials & Industrial Icon Standards

---

## 1. Typeface Strategy & Font Families

The interface uses two complementary Google Fonts:
1. **Primary Interface Font:** **Inter** (or **Roboto**) for clear UI labels, buttons, dialogs, and navigation.
2. **Serial & Gauge Font:** **Roboto Mono** (or **JetBrains Mono**) for all cylinder stamped serial numbers, RFID hex codes, tare weights, and pressure measurements.

```
       +-------------------------------------------------------------+
       |                     TYPOGRAPHY ARCHITECTURE                 |
       +-------------------------------------------------------------+
                                      │
         +----------------------------+----------------------------+
         │                                                         │
         v                                                         v
+-----------------------------+               +-----------------------------+
|    Inter (Proportional)     |               |    Roboto Mono (Monospace)  |
|  • "Apex Engineering Works" |               |  • "OX-47-009281"           |
|  • "15 Cylinders Delivered" |               |  • "52.40 kg  | 150.0 BAR"  |
|  • "Tap to Confirm POD"     |               |  • "EPC: E280116060000201"  |
+-----------------------------+               +-----------------------------+
```

---

## 2. Type Scale & Hierarchy (Jetpack Compose)

| Role | Font Family | Size | Weight | Line Height | Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Display Hero** | Inter | $28\text{ sp}$ | Bold (700) | $34\text{ sp}$ | Scan Counter (`18 / 20 Delivered`) |
| **Headline Large**| Inter | $22\text{ sp}$ | SemiBold (600) | $28\text{ sp}$ | Customer Name, Screen Titles |
| **Title Medium** | Inter | $18\text{ sp}$ | SemiBold (600) | $24\text{ sp}$ | Section Headers, Card Titles |
| **Serial Title** | Roboto Mono | $18\text{ sp}$ | Bold (700) | $22\text{ sp}$ | Cylinder Serial Numbers (`AR-47-0112`) |
| **Body Large** | Inter | $16\text{ sp}$ | Normal (400) | $22\text{ sp}$ | Delivery addresses, route notes |
| **Metric Value** | Roboto Mono | $15\text{ sp}$ | Medium (500) | $20\text{ sp}$ | Tare weight (`52.4 kg`), Pressure (`150 BAR`) |
| **Badge / Tag** | Inter | $12\text{ sp}$ | Bold (700) | $16\text{ sp}$ | Status Chips (`COC`, `FILLED`, `OVERDUE`) |

### Tabular Numbers Enforcement (`tnum`)
When numbers count up or dynamic weights are read, the font feature setting `tnum` (tabular numbers) is enforced to ensure numbers have identical character widths, preventing horizontal jitter:
```kotlin
val SerialNumberTextStyle = TextStyle(
    fontFamily = FontFamily.Monospace,
    fontSize = 18.sp,
    fontWeight = FontWeight.Bold,
    fontFeatureSettings = "tnum"
)
```

---

## 3. Field Readability & Accessibility Scaling

Drivers vary in age, eyesight, and literacy. The UI adheres to **Android Dynamic Type** scaling:
- **Maximum Scale Factor:** Scales cleanly up to $130\%$ font magnification without clipping text or wrapping action buttons off-screen.
- **Minimum Tap Target Height:** All interactive list items containing text have a minimum height of $64\text{ dp}$.

---

## 4. Standard Industrial Iconography (Material Symbols)

Icons use a consistent **$24\text{ dp}$ grid** ($32\text{ dp}$ for primary driver scan buttons) with a $2.0\text{ dp}$ stroke width.

```
+---------------------------------------------------------------------------------------------------+
| Concept / Action             | Material Symbol Name         | Visual Intent                       |
+-------------------------------+------------------------------+-------------------------------------+
| Barcode / QR Scanner          | `qr_code_scanner`            | Launch continuous camera viewfinder |
| RFID Wave Trigger             | `sensors` / `contactless`    | Bluetooth UHF RFID sled active      |
| Hydrostatic Test / Safety     | `verified_user` / `security` | PESO compliance verified            |
| Overdue Test Warning          | `gpp_bad` / `dangerous`      | PESO overdue lock active            |
| Tare Weight Scale             | `scale` / `weight`           | Stamped vs measured tare check      |
| Manifold Filling              | `valve` / `propane_tank`     | Gas filling station & manifold      |
| Truck Trip / Logistics        | `local_shipping`             | Outward dispatch & trip manifest    |
| Digital Signature             | `draw` / `signature`         | POD customer signature canvas       |
| OTP Verification              | `pin` / `password`           | 4-digit customer SMS/WhatsApp OTP   |
| Thermal Receipt Print         | `print` / `receipt_long`     | Bluetooth ESC/POS printer           |
| Offline Outbox Queue          | `cloud_off` / `sync`         | Pending un-synced transactions      |
+---------------------------------------------------------------------------------------------------+
```
