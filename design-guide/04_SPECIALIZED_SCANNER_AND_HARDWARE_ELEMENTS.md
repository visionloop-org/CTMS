# Specialized Scanner & Hardware UI Elements
## CameraX Reticle, Acoustic Cues, Haptic Patterns & RFID Radar Elements

---

## 1. CameraX Scanning Viewfinder & Reticle

The camera scanner is the primary interface used hundreds of times daily. It is designed for **continuous multi-code recognition** without user button pressing.

```
+--------------------------------------------------------------------------------------------------+
|  [< Back]               DELIVERY SCAN: APEX ENGINEERING                [Torch: ON]  [Batch: 18]  |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|                                        ┌───              ───┐                                    |
|                                                                                                  |
|                                        │     [  SCAN  ]     │  <-- Targeting Reticle             |
|                                              [  ZONE  ]            (250dp x 250dp)               |
|                                        │                    │                                    |
|                                                                                                  |
|                                        └───              ───┘                                    |
|                                                                                                  |
|                                                                                                  |
|  [!] Continuous Mode: Point camera along cylinder collars to batch-scan.                        |
+--------------------------------------------------------------------------------------------------+
|  LAST SCANNED: OX-47-0945 (OXYGEN 47L - COC)                             TOTAL DELIVERED: 18/20  |
+--------------------------------------------------------------------------------------------------+
```

### 1.1 Reticle Visual Specifications
- **Dimensions:** $250\times 250\text{ dp}$ centered in viewport.
- **Corner Brackets:** $4\text{ dp}$ thick, rounded corner radius $8\text{ dp}$, bracket arm length $32\text{ dp}$.
- **Targeting State Colors:**
  - **Searching:** Crisp White (`#FFFFFF`).
  - **Code Detected (Pass):** Flash Green (`#22C55E`) for 200ms.
  - **Invalid / Overdue Rejection:** Flash Crimson Red (`#EF4444`) with screen border glow.
  - **Duplicate Rescan:** Flash Amber (`#F59E0B`).

---

## 2. Acoustic (Audio) & Tactile (Haptic) Feedback Specifications

Field operators rely on ears and hands while physically moving heavy steel cylinders. Distinct audio-tactile cues prevent the operator from needing to look at the screen on every scan.

```
+---------------------------------------------------------------------------------------------------+
| Scan Event                   | Audio Cue (ToneGenerator)    | Haptic Vibration Pattern            |
+------------------------------+------------------------------+-------------------------------------+
| Valid Cylinder Scan          | 2,500 Hz Crisp Beep (70ms)   | Sharp Short Click (40ms @ 100% amp) |
|                              | `TONE_PROP_BEEP`             | `VibrationEffect.createOneShot(40)` |
+------------------------------+------------------------------+-------------------------------------+
| Duplicate Cylinder Rescan    | Dual Mid Beep (1,200 Hz)     | Double Tap (30ms on, 50ms off, 30ms)|
|                              | `TONE_PROP_ACK`              | `createWaveform([30, 50, 30], ...)` |
+------------------------------+------------------------------+-------------------------------------+
| Safety Rejection / Overdue   | Low Siren Warble (350 Hz)    | Long Heavy Buzz (350ms @ 100% amp)  |
| Hydrostatic Test             | `TONE_CDMA_HIGH_L`           | `VibrationEffect.createOneShot(350)`|
+------------------------------+------------------------------+-------------------------------------+
| Batch Target Complete        | Ascending Chime (3 tones)    | Triple Pulse Celebration            |
| (e.g. 20/20 Delivered)       | 1000Hz -> 1500Hz -> 2000Hz   |                                     |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. High-Velocity Batch Scan Counter Overlay

During continuous scanning, a semi-transparent HUD overlay displays real-time progress:
- **Left Column:** Live count: `Delivered: 18 / 20` (Green odometer).
- **Right Column:** Empties collected: `Collected: 15 / 15` (Blue odometer).
- **Recent Tag Carousel:** Horizontal scrolling chips below the viewfinder displaying the last 5 scanned serial numbers, with newest entering from the right with a slide-in spring animation.

---

## 4. Bluetooth UHF RFID Bulk Radar Interface

When paired with a Bluetooth UHF RFID reader gun (e.g., Zebra RFD8500), the app switches to **Radar Audio-Visual Mode**:

```
+--------------------------------------------------------------------------------------------------+
|  RFID BULK READ ACTIVE                     TAGS IN RANGE: 114 / 120         READ RATE: 420/SEC   |
|  [=============================================================================       ] 95%      |
+--------------------------------------------------------------------------------------------------+
```
- **Read-Rate Gauge:** Displays tags per second to verify antenna orientation.
- **Geiger Audio Clicker:** Beep frequency accelerates as undetected cylinders enter the RF field, guiding the driver to the rear corners of the truck bed.
