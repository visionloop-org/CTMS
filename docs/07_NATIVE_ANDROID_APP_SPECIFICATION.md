# Native Android Mobile Application Specification
## Architecture, Kotlin Jetpack Compose, Offline Room Database & Hardware SDKs

---

## 1. Executive Summary & Android Native Strategy

In the gas cylinder industry, delivery drivers, plant yard workers, and dispatch operators work in rugged, high-tempo, and hostile physical environments (intense direct sunlight, rain, grease, dust, and steel vibrations). 

To ensure **sub-100ms barcode/QR scanning speeds**, zero lag, continuous background GPS tracking, direct hardware peripheral communication (Bluetooth UHF RFID guns, ESC/POS thermal printers, Zebra DataWedge), and 100% reliable offline performance, the mobile client is architected as a **pure Native Android Application (Kotlin)**.

```
+--------------------------------------------------------------------------------------------------+
|                                    NATIVE ANDROID CLIENT (KOTLIN)                                |
+--------------------------------------------------------------------------------------------------+
|  PRESENTATION LAYER (Jetpack Compose + Material 3)                                              |
|  • High-Contrast Outdoor Theme   • Large Driver-Grade Touch Targets   • Continuous Scanner UI    |
|  • Digital Signature Canvas      • Multi-Language (EN, HI, MR, GU)   • Sync Status Indicators   |
+--------------------------------------------------------------------------------------------------+
|  STATE & ARCHITECTURE (MVVM + Jetpack Navigation + Coroutines / StateFlow)                       |
|  • AuthViewModel   • TripViewModel   • ScannerViewModel   • PODViewModel   • SyncViewModel       |
+--------------------------------------------------------------------------------------------------+
|  LOCAL STORAGE & OFFLINE ENGINE (Jetpack Room + EncryptedSharedPreferences)                      |
|  • SQLite / Room Database (Entities, Relations, Indices, DAOs)                                  |
|  • Transactional Mutation Outbox (Append-Only Event Store)                                       |
+--------------------------------------------------------------------------------------------------+
|  BACKGROUND PROCESSOR (Jetpack WorkManager)                                                      |
|  • Periodic Sync Worker   • Urgent Mutation Worker (Network Reconnect)   • Location Worker     |
+--------------------------------------------------------------------------------------------------+
|  HARDWARE & DEVICE ABSTRACTION LAYER                                                             |
|  +--------------------+  +--------------------+  +--------------------+  +---------------------+ |
|  | Google ML Kit &    |  | Rugged Hardware    |  | Bluetooth Low      |  | ESC/POS Bluetooth   | |
|  | CameraX Scanner    |  | Scanner SDKs       |  | Energy (BLE) RFID  |  | Thermal Printers    | |
|  | (150ms Camera QR)  |  | (Zebra DataWedge)  |  | (Zebra/Chainway)   |  | (Delivery Receipts) | |
|  +--------------------+  +--------------------+  +--------------------+  +---------------------+ |
+--------------------------------------------------------------------------------------------------+
```

---

## 2. Technical Stack & Android Tooling

| Component | Library / Framework | Version / Specification | Rationale |
| :--- | :--- | :--- | :--- |
| **Language** | Kotlin | 2.0+ | Modern type-safety, coroutines, and null-safety. |
| **Minimum SDK** | Android 8.0 (API Level 26) | 98.5% Device Coverage | Supports rugged Android devices (Chainway, Zebra, Honeywell, Urovo). |
| **Target SDK** | Android 15 (API Level 35) | Latest Google Play & OS security standard | Full compliance with modern background and permission rules. |
| **UI Framework** | Jetpack Compose + Material 3 | Latest BoM | Declarative, GPU-accelerated UI with fluid animations and responsive layout. |
| **Local Database** | Jetpack Room | 2.6+ | Type-safe SQLite abstraction for local data persistence and offline-first queueing. |
| **Dependency Injection** | Dagger Hilt | 2.50+ | Clean modular DI across ViewModels, Repositories, and System Services. |
| **Networking** | Retrofit 2 + OkHttp 4 | Latest | REST API client with interceptors for JWT auth, gzip compression, and caching. |
| **Camera & Vision** | CameraX + Google ML Kit | Barcode Scanning API | Low-latency camera preview, auto-focus, multi-code batch recognition. |
| **Background Sync** | Jetpack WorkManager | 2.9+ | Guaranteed background execution adhering to Android Doze mode and network constraints. |
| **Location Services** | Google Play Services Location | FusedLocationProvider | Battery-efficient GPS breadcrumbs and geo-fenced delivery watermarking. |

---

## 3. Hardware Integrations & Peripherals

Gas delivery operations utilize diverse hardware: from budget commercial Android smartphones to industrial rugged handheld terminals with dedicated laser scanners and UHF RFID antennas.

```
                           +---------------------------+
                           |   NATIVE ANDROID APP      |
                           +-------------+-------------+
                                         |
     ┌───────────────────┬───────────────┴───────────────┬───────────────────┐
     ▼                   ▼                               ▼                   ▼
[ CameraX + ML Kit ] [ Zebra DataWedge / OEM ] [ BLE UHF RFID Sled ]  [ Bluetooth Thermal ]
• Smartphone camera  • Industrial Barcode Scan  • Zebra RFD8500        • 2-inch / 3-inch
• Laser-fast QR/2D   • Hardware laser trigger   • Chainway C72         • On-site receipt
• Torch & Auto-focus • Broadcast Receiver       • 700 tags/second      • ESC/POS protocol
```

### 3.1 Google ML Kit & CameraX (Smartphone Scanning)
- **Zero-Tap Continuous Scanning:**
  - The driver holds the camera over cylinders lined up on the truck or customer floor.
  - Multi-code frame processing detects and adds cylinders to the delivery manifest sequentially without requiring the user to press a button for each scan.
- **Audio & Haptic Feedback:**
  - **Success Tone:** High-pitch crisp beep (`ToneGenerator.TONE_PROP_BEEP`) + short haptic vibration (`VibrationEffect.createOneShot(50, 255)`).
  - **Duplicate / Error Tone:** Double low beep (`ToneGenerator.TONE_PROP_NACK`) + long vibration alert.
  - **PESO Overdue / Safety Alert:** Siren tone and full-screen flashing red warning.

### 3.2 Rugged Handheld Scanner Integration (OEM BroadcastReceiver)
For enterprise devices like **Zebra TC26/TC57**, **Honeywell ScanPal**, **Chainway C66**, or **Urovo**:
- Scans are triggered via the device's physical rubberized side grip buttons.
- The app binds to the hardware scan engine using an Android `BroadcastReceiver`:
```kotlin
class BarcodeScanReceiver(
    private val onBarcodeScanned: (String) -> Unit
) : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        val action = intent?.action
        if (action == "com.symbol.datawedge.api.RESULT_ACTION" || 
            action == "com.scanner.broadcast") {
            val scannedCode = intent.getStringExtra("com.symbol.datawedge.data_string")
                ?: intent.getStringExtra("scannerdata")
            scannedCode?.let { onBarcodeScanned(it.trim()) }
        }
    }
}
```

### 3.3 Bluetooth UHF RFID Reader SDK Integration
- Connects to Bluetooth sled readers (e.g., Zebra RFD8500, Chainway R6) using Android BLE (`BluetoothGatt`).
- **Bulk Reading Capability:** Reads up to **700 tags per second** within a 6-meter radius.
- Driver presses the RFID gun trigger to scan an entire truck bed (120 cylinders) in under 5 seconds during gate-outward and trip reconciliation.

### 3.4 Bluetooth ESC/POS Receipt Printer
- Directly prints 58mm / 80mm thermal paper receipts for customers who demand physical challans at delivery:
  - Header: Gas Company Name, GSTIN, Plant Address.
  - Body: Delivery Challan Number, Date, Customer Name.
  - Serialized list of Delivered Filled Cylinders & Collected Empty Cylinders.
  - Footer: Receiver Signature Block and Verification QR Code.

---

## 4. Offline-First Database Architecture (Jetpack Room)

The local Room database mirrors necessary operational models and serves as the single source of truth for the UI.

```
+--------------------------------------------------------------------------------------------------+
|                                  LOCAL ROOM DATABASE (SQLite)                                    |
+--------------------------------------------------------------------------------------------------+
|  ENTITIES:                                                                                       |
|  • UserSessionEntity      • ActiveTripEntity      • CustomerCacheEntity                          |
|  • CylinderCacheEntity    • ChallanDraftEntity    • ChallanItemEntity    • OutboxMutationEntity  |
+--------------------------------------------------------------------------------------------------+
|  DATA ACCESS OBJECTS (DAOs):                                                                     |
|  • TripDao: Query active trips, manifests, customer stops                                        |
|  • CylinderDao: Fast indexed lookup by QR Hash, RFID EPC, or Serial Number                       |
|  • OutboxDao: Enqueue pending mutations, query un-synced queue, update status                    |
+--------------------------------------------------------------------------------------------------+
```

### 4.1 Room Entity Definitions (Kotlin)

```kotlin
package com.ctms.app.data.local.entity

import androidx.room.*
import java.util.UUID

@Entity(tableName = "cylinders_cache", indices = [
    Index(value = ["serialNumber"], unique = true),
    Index(value = ["qrCodeUid"], unique = true),
    Index(value = ["rfidEpcUid"], unique = true)
])
data class CylinderCacheEntity(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val serialNumber: String,
    val qrCodeUid: String?,
    val rfidEpcUid: String?,
    val gasType: String,
    val ownership: String, // 'COC', 'POC', 'VOC'
    val ownerCustomerId: String?,
    val tareWeightKg: Double,
    val hydroTestDueDate: Long, // Epoch timestamp
    val isOverdue: Boolean
)

@Entity(tableName = "outbox_mutations", indices = [
    Index(value = ["status", "createdAt"])
])
data class OutboxMutationEntity(
    @PrimaryKey val mutationId: String = UUID.randomUUID().toString(),
    val eventType: String, // 'DELIVERY_CONFIRMED', 'PICKUP_CONFIRMED', 'GATE_CHECKOUT'
    val payloadJson: String, // Full JSON payload
    val idempotencyKey: String,
    val retryCount: Int = 0,
    val status: String = "QUEUED", // 'QUEUED', 'SYNCING', 'COMMITTED', 'FAILED'
    val lastError: String? = null,
    val createdAt: Long = System.currentTimeMillis()
)
```

### 4.2 Outbox Mutation DAO (Kotlin)

```kotlin
package com.ctms.app.data.local.dao

import androidx.room.*
import com.ctms.app.data.local.entity.OutboxMutationEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface OutboxDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertMutation(mutation: OutboxMutationEntity)

    @Query("SELECT * FROM outbox_mutations WHERE status IN ('QUEUED', 'FAILED') ORDER BY createdAt ASC")
    suspend fun getPendingMutations(): List<OutboxMutationEntity>

    @Query("SELECT COUNT(*) FROM outbox_mutations WHERE status IN ('QUEUED', 'FAILED')")
    fun getPendingCountFlow(): Flow<Int>

    @Query("UPDATE outbox_mutations SET status = :newStatus WHERE mutationId = :id")
    suspend fun updateStatus(id: String, newStatus: String)

    @Query("DELETE FROM outbox_mutations WHERE status = 'COMMITTED' AND createdAt < :thresholdTimestamp")
    suspend fun purgeOldCommitted(thresholdTimestamp: Long)
}
```

---

## 5. Background Synchronization Engine (Jetpack WorkManager)

### 5.1 Sync Worker Implementation
`SyncWorker` runs periodically and reacts immediately to network restoration events.

```kotlin
package com.ctms.app.worker

import android.content.Context
import androidx.hilt.work.HiltWorker
import androidx.work.*
import com.ctms.app.data.local.dao.OutboxDao
import com.ctms.app.data.remote.CtmsApiService
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject

@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted appContext: Context,
    @Assisted workerParams: WorkerParameters,
    private val outboxDao: OutboxDao,
    private val apiService: CtmsApiService
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val pendingMutations = outboxDao.getPendingMutations()
        if (pendingMutations.isEmpty()) return Result.success()

        for (mutation in pendingMutations) {
            try {
                outboxDao.updateStatus(mutation.mutationId, "SYNCING")
                val response = apiService.submitMutation(
                    idempotencyKey = mutation.idempotencyKey,
                    eventType = mutation.eventType,
                    payloadJson = mutation.payloadJson
                )
                if (response.isSuccessful) {
                    outboxDao.updateStatus(mutation.mutationId, "COMMITTED")
                } else if (response.code() in 400..499 && response.code() != 429) {
                    // Client error: mark failed without infinite retry
                    outboxDao.updateStatus(mutation.mutationId, "FAILED")
                } else {
                    return Result.retry()
                }
            } catch (e: Exception) {
                return Result.retry()
            }
        }
        return Result.success()
    }

    companion object {
        fun buildPeriodicWorkRequest(): PeriodicWorkRequest {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()

            return PeriodicWorkRequestBuilder<SyncWorker>(15, java.util.concurrent.TimeUnit.MINUTES)
                .setConstraints(constraints)
                .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, java.util.concurrent.TimeUnit.SECONDS)
                .build()
        }
    }
}
```

---

## 6. App Screen Flows & Jetpack Compose UI Specifications

```
[ App Launch ]
      │
      ▼
[ Driver Login & Vehicle Selection ]
      │
      ▼
[ Trip Dashboard (Route Stops, Loaded Cylinders Count) ]
      │
      ├──> [ Stop 1: Customer Arrival ]
      │           │
      │           ├──> [ Scan Delivered Cylinders (Filled) ] ──> Green Flash / Haptic
      │           │
      │           ├──> [ Scan Collected Cylinders (Empty) ]  ──> POC vs COC Validation
      │           │
      │           ├──> [ Damage Inspection / Photo Capture ]
      │           │
      │           ▼
      │     [ Proof of Delivery (POD) Screen ]
      │           ├── e-Signature Canvas
      │           ├── 4-Digit Customer OTP Verification
      │           ├── Geotagged Watermark
      │           ▼
      │     [ Generate e-DC & Print Thermal Receipt ]
      │
      ├──> [ Subsequent Customer Stops... ]
      │
      ▼
[ Return to Plant Gate: Trip Reconciliation Screen ]
      │
      ▼
[ Unload Empties & Supervisor Audit Signoff ]
```

### 6.1 Screen 1: Driver Dashboard & Manifest Summary
- Displays active trip status, assigned vehicle plate (`MH-04-AB-1234`), total outward loaded cylinders (e.g., `120 Units`), delivered count, and collected empty count.
- List of scheduled customer stops with 1-tap Google Maps Navigation integration.

### 6.2 Screen 2: High-Speed Continuous Scanning Screen
- **Camera Viewfinder:** Full-screen camera preview with a targeting reticle.
- **Top Stats Bar:**
  - `Delivered: 18 / 20` | `Returned: 15 / 15`
- **Bottom Scanned Items Carousel:**
  - Real-time animated chips showing scanned serial numbers.
  - Tapping a chip opens the details: Gas Type, Tare Weight, Hydro Test Expiry, and Ownership (`COC` vs `POC`).
- **Damage Capture Action:**
  - Quick-action floating button: "Flag Damaged Collar / Valve" launches CameraX to snap a high-resolution photo with damage categorization.

### 6.3 Screen 3: Digital Proof of Delivery (POD) Screen
- **Signature Canvas Component:** Smooth Bezier-curve finger signature capture.
- **OTP Verification Fallback:** Button triggers instant SMS/WhatsApp OTP to customer authorized phone.
- **Summary Preview:** Shows exact serial numbers being transferred into customer custody and empties being credited.
- **Confirmation Action:** Commits transaction to local Room database and immediately enqueues outbox mutation for background sync to Zoho Books.

### 6.4 Screen 4: Trip Reconciliation & Gate Check-in
- Computes vehicle inventory balance upon return to plant:
  $$\text{Expected Closing} = \text{Opening} - \text{Delivered} + \text{Collected}$$
- Shows green checkmark if truck stock matches gate inward scan; shows high-contrast red warning if any cylinder is unaccounted for.

---

## 7. APK Packaging, Distribution & MDM Strategy

1. **Android App Bundle (AAB) & APK:**
   - Universal APK generated for direct side-loading on dedicated rugged devices without Google Play Store (MDM deployment).
   - Android App Bundle (AAB) published on private **Google Play Managed Enterprise** channel.
2. **Mobile Device Management (MDM) Compatibility:**
   - Fully compatible with enterprise MDM platforms (**SOTI MobiControl**, **Microsoft Intune**, **SureMDM**, **Zoho ManageEngine Mobile Device Manager Plus**).
   - Supports **Kiosk Mode / Lock-Task Mode**: locks rugged handhelds so drivers cannot exit the CTMS application or install unauthorized apps.
3. **Over-The-Air (OTA) In-App Updates:**
   - In-app update checker notifies drivers of mandatory software updates before starting a morning dispatch run.
