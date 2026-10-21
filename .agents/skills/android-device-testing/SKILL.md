---
name: android-device-testing
description: >-
  Use this skill when developing, testing, or building the Native Android application
  (Room database, CameraX scanning, Jetpack Compose UI, WorkManager sync, or hardware peripherals).
---

# Android Device Testing Skill

This skill guides the agent in building, testing, and verifying the Native Android application.

## 1. Core Modules to Test

### Room Database & Migrations
- Test entity insertions and queries in `com.ctms.app.data.local.dao.*`.
- Ensure `OutboxDao.getPendingMutations()` retrieves queued deliveries in strict FIFO order by `createdAt`.
- Verify database migrations preserve offline un-synced data.

### CameraX & ML Kit Scanning
- Ensure camera preview frame rate maintains $\ge 30\text{ fps}$.
- Test barcode detection throttle to prevent duplicate triggers within 500ms for the same cylinder ID:
  ```kotlin
  if (lastScannedId == newId && currentTime - lastScannedTime < 500) {
      // Ignore duplicate bounce scan
      return
  }
  ```

### Background Sync (WorkManager)
- Test `SyncWorker` under simulated network failures using `WorkManagerTestInitHelper`.
- Ensure failed mutations with HTTP 500 trigger `Result.retry()` with exponential backoff.
- Ensure 4xx validation errors are marked as `FAILED` to avoid poison pill loops.

## 2. Command Reference
```bash
# Run Room database and ViewModel unit tests
./gradlew testDebugUnitTest

# Run Android Lint checks
./gradlew lintDebug

# Build release APK for testing
./gradlew assembleRelease
```
