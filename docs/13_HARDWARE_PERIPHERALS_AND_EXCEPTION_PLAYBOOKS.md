# Hardware Peripherals & Operational Exception Playbooks
## ESC/POS Printing, Rugged Scanners & Industrial Edge Anomaly Protocols

---

## 1. Bluetooth Thermal Printer ESC/POS Byte Layout Specification

CTMS mobile drivers carry portable 2-inch (58mm / 384 dots) and 3-inch (80mm / 576 dots) battery-powered Bluetooth thermal printers (e.g. TVS, Epson, Rugtek, BluPrints, Bixolon). These printers produce legal **Electronic Delivery Challans (e-DC)** and **Electronic Cylinder Receipts (ECR)** at customer drop-off without cellular reception.

### 1.1 Core ESC/POS Control Sequences (Hexadecimal)

```
+---------------------------------------------------------------------------------------------------+
| Command Name                | ESC/POS Hex Sequence        | Description / Field Behavior          |
+-----------------------------+-----------------------------+---------------------------------------+
| Hardware Reset / Init       | `1B 40`                     | Clear buffer & reset text formatting  |
| Text Alignment (Left)       | `1B 61 00`                  | Left justify text                     |
| Text Alignment (Center)     | `1B 61 01`                  | Center justify text                   |
| Text Alignment (Right)      | `1B 61 02`                  | Right justify text                    |
| Emphasized / Bold ON        | `1B 45 01`                  | Bold font weight enabled              |
| Emphasized / Bold OFF       | `1B 45 00`                  | Standard font weight                  |
| Double-Height ON            | `1D 21 01`                  | Double font height                    |
| Double-Width ON             | `1D 21 10`                  | Double font width                     |
| Double-Height + Width ON    | `1D 21 11`                  | Headline double size                  |
| Normal Size (Reset)         | `1D 21 00`                  | Standard 1x1 font scale               |
| Paper Feed (N lines)        | `1B 64 <n>`                 | Feed paper n lines (e.g. 1B 64 04)    |
| Partial Guillotine Cut      | `1D 56 42 00`               | 80mm only: Cut with feed              |
| Raster Bit-Image (Fallback) | `1D 76 30 00 xL xH yL yH`   | GS v 0 raster bitmap print            |
+---------------------------------------------------------------------------------------------------+
```

---

### 1.2 Two-Dimensional QR Printing: Raster-First with Native Optimization

> [!IMPORTANT]
> **Real-World Hardware Reality:** Many low-cost 58mm mobile belt-clip printers lack firmware support for native ESC/POS 2D barcode commands (`GS ( k`).
> **Engineering Rule:** The Android client generates a **pure monochrome raster bitmap (`GS v 0`) as the universal default**. Native `GS ( k` is treated as an optional optimization toggled via printer capability profiles.

#### 1. Universal Raster Bit-Image Mode (`GS v 0` - Standard for all 58mm/80mm):
```hex
[Raster Bit-Image Header]: 1D 76 30 00 <xL> <xH> <yL> <yH> <BITMAP_BYTES>
Where:
  xL, xH = Number of bytes in horizontal direction (e.g., 250 dots / 8 = 32 bytes -> 20 00)
  yL, yH = Number of dots in vertical direction (e.g., 250 dots -> FA 00)
```

#### 2. Native ESC/POS QR Mode (`GS ( k` - High-End Desktop / 80mm Mobile):
```hex
[1. Set QR Model 2]:             1D 28 6B 04 00 31 41 32 00
[2. Set QR Module Size (1-16)]:  1D 28 6B 03 00 31 43 06
[3. Set Error Correction Level]: 1D 28 6B 03 00 31 45 31   (30=L, 31=M, 32=Q, 33=H)
[4. Store QR Data (pL pH = n+3)]:1D 28 6B <pL> <pH> 31 50 30 <DATA_BYTES>
[5. Print QR Buffer]:            1D 28 6B 03 00 31 51 30
```

---

### 1.3 Belt-Clip Paper Handling, Currency & Devanagari Guidelines

1. **Tear Bar vs. Guillotine Cutters:**
   - 58mm mobile belt-clip printers do not have motorized cutter blades. Sending `1D 56 42 00` can stall the print buffer on generic hardware.
   - For 58mm printers: Always send **Paper Feed 4 Lines** (`1B 64 04`) to push the receipt past the serrated manual tear bar.
   - For 80mm vehicle-mounted or desktop printers with auto-cutters: Issue partial cut `1D 56 42 00`.

2. **Currency Symbols & Devanagari (Hindi) Text:**
   - Most Indian thermal printers lack Unicode code pages for Devanagari script and the Indian Rupee symbol (`₹`).
   - Text using `₹` prints as corrupted garbage characters (such as `?` or `EUR`).
   - **Standard:** Use standard ASCII `Rs.` for plain-text receipts, or render customer names / Hindi text on an Android `Bitmap` canvas and output via `GS v 0` raster stream.

3. **Reprint & Duplicate Audit Invariant:**
   - If an e-DC or ECR receipt is reprinted (due to paper jam or driver error):
   - The receipt header **MUST** print in bold double-height: `*** DUPLICATE COPY ***`.
   - The print event is immutably logged in `cylinder_events` with `event_type = RECEIPT_REPRINTED` along with driver ID, GPS coordinates, and timestamp.

---

### 1.4 58mm (32-Column) Electronic Delivery Challan (e-DC) Layout

```text
       1B 40                           <-- Initialize
       1B 61 01                        <-- Center Align
       1D 21 11                        <-- Double Height & Width
       APEX INDUSTRIAL GASES
       1D 21 00                        <-- Normal Size
       Plot 14, MIDC Industrial Area, Pune
       GSTIN: 27AABCA1234F1Z5
       PESO Ref: G.3(1)2021-EXP
--------------------------------
       1B 61 00                        <-- Left Align
       1B 45 01                        <-- Bold ON
       DELIVERY CHALLAN (e-DC)
       1B 45 00                        <-- Bold OFF
Challan No:  DC-2026-008129
Date & Time: 21-OCT-2026 14:32 IST
Customer:    Sunrise Multispeciality
Cust GSTIN:  27AAACS1421D1ZA
Delivery At: Senapati Bapat Marg, Pune
Vehicle No:  MH-12-RN-8819 (Truck 4)
Driver:      Ramesh Shinde (DRV-04)
--------------------------------
SR. CYLINDER ID    GAS TYPE    ST
--------------------------------
01  OX-47-0912     MED O2 47L  COC
02  OX-47-0913     MED O2 47L  COC
03  OX-47-1002     MED O2 47L  COC
04  N2-88-0192     NITROGEN    POC*
--------------------------------
*POC: Party-Owned (Rental-Exempt)
Delivered Full Cylinders:     04
Collected Empty Cylinders:    04
Net Security Deposits Held:   Rs. 0.00
Current Holding Balance:      84 Cyl
--------------------------------
       1B 61 01                        <-- Center Align
[ RASTER QR BITMAP (GS v 0) ]
Scan to verify statutory e-DC
https://portal.apexgases.com/dc/8129

Customer Signature on File (OTP Verified)
OTP Auth Code: 891-204 (14:31:55 IST)
--------------------------------
       1B 64 04                        <-- Feed 4 Lines past tear bar
```

---

## 2. Dedicated Rugged Barcode Guns & Scanner Intent Architecture

To achieve sub-100ms continuous batch scanning in industrial plants, CTMS interfaces with Android laser terminals (Zebra TC21/TC26, Chainway C66/C72, Honeywell EDA51).

```
                      +------------------------------------------+
                      |         Physical Hardware Trigger        |
                      |   (Laser Engine / 2D Imager Triggered)   |
                      +------------------------------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |        Vendor Hardware Service           |
                      |    (Zebra DataWedge / Chainway Service)  |
                      +------------------------------------------+
                                           |
                     Intent Broadcast with | Action: com.ctms.app.SCAN
                     Extra: com.symbol.datawedge.data_string
                                           v
                      +------------------------------------------+
                      |       ScannerSource Interface Adapter    |
                      |  - CameraXScannerSource                  |
                      |  - DataWedgeScannerSource                |
                      |  - ChainwayScannerSource                 |
                      +------------------------------------------+
                                           |
                                           | Reactive StateFlow<ScanEvent>
                                           v
                      +------------------------------------------+
                      |         CTMS Domain State Machine        |
                      |    (Zero knowledge of hardware source)   |
                      +------------------------------------------+
```

---

### 2.1 The `ScannerSource` Unified Interface

```kotlin
interface ScannerSource {
    val scanEvents: StateFlow<ScanResult?>
    fun enable()
    fun disable()
}

data class ScanResult(
    val rawData: String,
    val symbology: String,
    val sourceHardware: ScannerHardwareType,
    val timestamp: Long = System.currentTimeMillis()
)

enum class ScannerHardwareType {
    CAMERAX_MLKIT,
    ZEBRA_DATAWEDGE,
    CHAINWAY_LASER,
    BLUETOOTH_RFID_SLED
}
```

---

### 2.2 Zebra DataWedge Configuration & Broadcast Receiver

#### 1. Zero-Touch Auto-Provisioning on First Launch (`SET_CONFIG`):
The app automatically creates and configures the DataWedge profile without requiring manual MDM setup:

```kotlin
fun provisionDataWedgeProfile(context: Context) {
    val profileConfig = Bundle().apply {
        putString("PROFILE_NAME", "CTMS_Scanner_Profile")
        putString("PROFILE_ENABLED", "true")
        putString("CONFIG_MODE", "CREATE_IF_NOT_EXIST")
        
        // Associate with CTMS Android Application
        val appConfig = Bundle().apply {
            putString("PACKAGE_NAME", context.packageName)
            putStringArray("ACTIVITY_LIST", arrayOf("*"))
        }
        putParcelableArray("APP_LIST", arrayOf(appConfig))
    }
    
    // Configure Intent Output Plugin
    val intentConfig = Bundle().apply {
        putString("PLUGIN_NAME", "INTENT")
        putString("RESET_CONFIG", "true")
        val intentParams = Bundle().apply {
            putString("intent_output_enabled", "true")
            putString("intent_action", "com.ctms.app.SCAN")
            putString("intent_delivery", "2") // 2 = Broadcast Intent
        }
        putBundle("PARAM_LIST", intentParams)
    }
    profileConfig.putBundle("PLUGIN_CONFIG", intentConfig)

    val setConfigIntent = Intent("com.symbol.datawedge.api.ACTION").apply {
        putExtra("com.symbol.datawedge.api.SET_CONFIG", profileConfig)
    }
    context.sendBroadcast(setConfigIntent)
}
```

#### 2. DataWedge Broadcast Receiver:
```kotlin
class DataWedgeReceiver(
    private val onScanReceived: (ScanResult) -> Unit
) : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == "com.ctms.app.SCAN") {
            val scannedData = intent.getStringExtra("com.symbol.datawedge.data_string") ?: return
            val labelType = intent.getStringExtra("com.symbol.datawedge.label_type") ?: "UNKNOWN"
            
            onScanReceived(
                ScanResult(
                    rawData = scannedData.trim(),
                    symbology = labelType,
                    sourceHardware = ScannerHardwareType.ZEBRA_DATAWEDGE
                )
            )
        }
    }
}
```

---

### 2.3 Chainway C66 / C72 Scanner Receiver

Chainway rugged devices dispatch scans via their internal scanner service:

```kotlin
class ChainwayReceiver(
    private val onScanReceived: (ScanResult) -> Unit
) : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        // Chainway default broadcast action
        if (intent.action == "com.android.server.scannerservice.broadcast") {
            val barcode = intent.getStringExtra("scannerdata") ?: return
            
            onScanReceived(
                ScanResult(
                    rawData = barcode.trim(),
                    symbology = "2D_BARCODE",
                    sourceHardware = ScannerHardwareType.CHAINWAY_LASER
                )
            )
        }
    }
}
```

---

## 3. Industrial Edge Exception Playbooks

Real-world factory floors and delivery routes encounter physical anomalies that break naive software:

---

### 3.1 Playbook 1: Damaged Collar QR & Stamped Metal Serial Re-Tagging

```
[ QR Code Sandblasted / Destroyed ]
                │
                ▼
[ Operator inspects cylinder shoulder ]
                │
                ▼
[ Search hard-stamped metal serial: e.g. "OX-47-0912" ]
                │
                ▼
[ Capture high-resolution photo of stamped shoulder ]
                │
                ▼
[ Scan brand-new, unassigned QR collar tag: "TAG-99412" ]
                │
                ▼
[ Manager OTP Approval: Dual-Control Authorization ]
                │
                ▼
[ Backend: Retire old tag_binding, bind new tag to immutable UUID ]
                │
                ▼
[ Complete 40-year event history preserved on cylinder UUID ]
```

#### Temporal Tag Binding Database Schema (`tag_bindings`):
```sql
CREATE TABLE tag_bindings (
    binding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cylinder_id UUID NOT NULL REFERENCES cylinders(cylinder_id),
    tag_id VARCHAR(64) NOT NULL,                          -- QR code string or RFID EPC
    stamped_serial_no VARCHAR(100) NOT NULL,
    shoulder_photo_uri VARCHAR(512) NOT NULL,             -- Evidence photo of physical stamped steel
    manager_otp_user_id UUID NOT NULL REFERENCES users(user_id),
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to TIMESTAMPTZ,                                 -- NULL = Active Tag
    binding_reason VARCHAR(100) NOT NULL DEFAULT 'DAMAGED_REPLACEMENT',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Constraint: Only one active tag per cylinder at any instant
CREATE UNIQUE INDEX idx_active_tag_per_cylinder 
ON tag_bindings (cylinder_id) WHERE valid_to IS NULL;

-- Constraint: A tag cannot be actively assigned to multiple cylinders
CREATE UNIQUE INDEX idx_active_tag_unique 
ON tag_bindings (tag_id) WHERE valid_to IS NULL;
```

---

### 3.2 Playbook 2: Concurrent Offline Scan Collision Arbitration

> [!CAUTION]
> **Trap to Avoid:** Do NOT arbitrate offline collisions using device GPS and device timestamps alone. System clocks drift across mobile devices, and GPS signals are easily blocked inside steel cylinder warehouses or spoofed.

#### Deterministic Hybrid Logical Clock (HLC) & State Machine Arbitration:

```
[ Truck A (Offline) Scans OX-47-0912 ]         [ Truck B (Offline) Scans OX-47-0912 ]
  - Device HLC: (T1, 0)                          - Device HLC: (T2, 0)
  - Action: DELIVERED to Hospital                - Action: COLLECTED from Factory
                 \                                     /
                  \                                   /
                   ▼                                 ▼
             +---------------------------------------------+
             |         Cloud Ingestion Outbox Queue        |
             +---------------------------------------------+
                                   │
                                   ▼
             +---------------------------------------------+
             |     State Machine Deterministic Replay      |
             |  Current DB Status: LOADED_TRUCK (Truck A)  |
             +---------------------------------------------+
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
[ Event 1 from Truck A: DELIVERED ]           [ Event 2 from Truck B: COLLECTED ]
  • Legal Transition from LOADED_TRUCK          • ILLEGAL Transition! (Truck B never
  • Database commits: CUSTOMER_HELD               had cylinder on its manifest)
  • cylinder_events row appended                • Stored as REJECTED_CONFLICT
                                                • Audit incident created for manager
```

#### Arbitration Rules:
1. Every scan mutation carries `device_id`, monotonic `device_sequence_no`, and **Hybrid Logical Clock (HLC)** timestamp.
2. The server processes events strictly through the **Custody State Machine**:
   - `DELIVERED` is only valid if cylinder is currently `LOADED_TRUCK` on that specific driver's `trip_id`.
   - `COLLECTED_EMPTY` is only valid if cylinder is currently `CUSTOMER_HELD` at that customer location.
3. If an incoming event is mathematically illegal according to the active custody state, it is **never discarded**:
   - It is committed to `cylinder_events` with `to_status = REJECTED_CONFLICT`.
   - The current cylinder custody status remains unchanged.
   - A high-priority **Manager Conflict Task** is enqueued in the web dashboard displaying both drivers' GPS coordinates, photos, and customer challans for manual review.

---

### 3.3 Playbook 3: Ghost / Unaccounted Cylinder Plant Yard Audit

During monthly plant inventory audits, physical cylinders are discovered in the yard whose database record indicates they are still held at a customer site (`CUSTOMER_HELD`).

```
+---------------------------------------------------------------------------------------------------+
| GHOST CYLINDER AUDIT RECONCILIATION WORKFLOW                                                      |
+---------------------------------------------------------------------------------------------------+
| 1. Physical Discovery:                                                                            |
|    Plant auditor scans cylinder OX-47-0912 during yard stocktaking.                              |
|    DB Status: CUSTOMER_HELD (Sunrise Hospital, delivered 120 days ago).                           |
|                                                                                                   |
| 2. Automated State Transition:                                                                    |
|    cylinder_status -> QUARANTINED_AUDIT                                                           |
|    location_id     -> PLANT_YARD_QUARANTINE_BAY                                                   |
|                                                                                                   |
| 3. Commercial Protection (Automated Rent Pause):                                                  |
|    - Daily holding fee accrual is IMMEDIATELY PAUSED for Sunrise Hospital.                        |
|    - Prevents false over-billing and legal disputes during dispute investigation.                 |
|                                                                                                   |
| 4. Reconciliation Decision (Operations Manager):                                                  |
|    Option A [Customer Returned Without Scan]:                                                     |
|      - Confirm customer returned via third-party vehicle.                                         |
|      - Waive rental from discovery date; transition cylinder to PLANT_EMPTY.                      |
|    Option B [Duplicate Stamping / Phantom Cylinder]:                                              |
|      - Cylinder shoulder inspected for cloned serial numbers.                                     |
|      - If confirmed counterfeit, transition to CONDEMNED_PESO and file police FIR.                |
+---------------------------------------------------------------------------------------------------+
```
