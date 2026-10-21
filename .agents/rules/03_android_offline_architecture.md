# Rule: Native Android Offline-First Architecture

## Architecture & Performance Standards for Android Client

1. **Local Room Write Precedence (Offline-First):**
   - The Android client must operate flawlessly without an active cellular or Wi-Fi network.
   - Every delivery scan, empty collection, damage photo, customer signature, and OTP verification MUST commit to local Room database entities and append an outbox entry in `outbox_mutations` BEFORE attempting any network transmission.
   - The UI must update immediately using optimistic state (`DELIVERED_OFFLINE_SAVED`).

2. **Main Thread Non-Blocking Invariant:**
   - Database operations (Room DAOs), cryptographic hashing, image compression, and network calls must NEVER run on `Dispatchers.Main`.
   - Always dispatch to `Dispatchers.IO` or `Dispatchers.Default`:
     ```kotlin
     withContext(Dispatchers.IO) {
         outboxDao.insertMutation(mutation)
     }
     ```

3. **High-Speed Scanning Latency ($\le 150\text{ ms}$):**
   - CameraX frame analysis with Google ML Kit Barcode Scanning must process video frames at $\ge 30\text{ fps}$.
   - Continuous scanning debounce: The scanner must prevent duplicate scan triggers of the same cylinder ID within 500ms.
   - Distinct audio and haptic feedback must trigger on every valid scan without UI stutter.

4. **Background Sync via WorkManager:**
   - Background synchronization must be orchestrated exclusively through `androidx.work.WorkManager`.
   - Never run raw background threads or infinite while-loops in Android Services.
   - Enforce network constraints: `NetworkType.CONNECTED`.
   - Handle server errors with `Result.retry()` and exponential backoff.
