# AI-Driven Development (AIDD) Protocols & Engineering Best Practices
## Standards for Autonomous AI Pair Programming, Verification & Continuous Evolution

---

## 1. Vision & Core Philosophy

Building enterprise ERP and safety-critical asset tracking systems with AI requires shifting from unstructured code generation to **Deterministic, Spec-Driven Autonomous Development**. 

AI agents operate with maximum speed and zero regression when bounded by strict protocols:
1. **Spec-Driven Precedence (Read Before Write):** Specifications are the single source of truth; agents never guess business rules or hallucinate APIs.
2. **Test-First Red-Green-Refactor (Verify Before Declare):** Agents must write failing tests, implement the minimal solution, and execute tests to observe success.
3. **Hermetic Mocking (Zero-Credential Autonomy):** Development and testing must execute against self-contained mock servers and in-memory databases without requiring live Zoho API keys or physical hardware.
4. **Non-Negotiable Proof Artifacts:** No task is complete without an automated execution log proving code correctness.

```
┌───────────────────────────────────────────────────────────────────────────┐
│                    THE AI-DRIVEN DEVELOPMENT CYCLE                        │
└───────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
        ┌───────────────────────────────────────────────────────────┐
        │ 1. TASK INTAKE & SPEC ANCHORING                           │
        │ • Read TASK_QUEUE.md & corresponding docs/ specification  │
        │ • Identify Prime Invariants & affected modules           │
        └────────────────────────────┬──────────────────────────────┘
                                     │
                                     ▼
        ┌───────────────────────────────────────────────────────────┐
        │ 2. RED PHASE: WRITE FAILING TEST FIRST                    │
        │ • Create unit/integration test capturing acceptance spec  │
        │ • Run test command -> OBSERVE FAILURE (Red)               │
        └────────────────────────────┬──────────────────────────────┘
                                     │
                                     ▼
        ┌───────────────────────────────────────────────────────────┐
        │ 3. GREEN PHASE: MINIMAL IMPLEMENTATION                    │
        │ • Implement minimal clean code adhering to invariants     │
        │ • Run test command -> OBSERVE SUCCESS (Green)             │
        └────────────────────────────┬──────────────────────────────┘
                                     │
                                     ▼
        ┌───────────────────────────────────────────────────────────┐
        │ 4. REFACTOR & REGRESSION AUDIT                            │
        │ • Enforce Clean Architecture (Data -> Domain -> Present)  │
        │ • Run entire suite to ensure zero collateral regressions  │
        └────────────────────────────┬──────────────────────────────┘
                                     │
                                     ▼
        ┌───────────────────────────────────────────────────────────┐
        │ 5. PROOF ARTIFACT & QUEUE UPDATE                          │
        │ • Save test log proof into scratch/test-runs/             │
        │ • Check off task in TASK_QUEUE.md with timestamp          │
        └───────────────────────────────────────────────────────────┘
```

---

## 2. The 7 AIDD Protocols

### Protocol 1: Spec-First Anchoring & Context Ingestion
- **Mandate:** Before writing or altering code, the AI agent must read the specific specification markdown file in `docs/` governing that feature:
  - Financial/Zoho flows $\rightarrow$ [`docs/08_ZOHO_API_INTERACTIONS_AND_PAYLOAD_SPECIFICATION.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/08_ZOHO_API_INTERACTIONS_AND_PAYLOAD_SPECIFICATION.md)
  - Android Kotlin/Compose $\rightarrow$ [`docs/07_NATIVE_ANDROID_APP_SPECIFICATION.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/07_NATIVE_ANDROID_APP_SPECIFICATION.md)
  - Lifecycle state machine $\rightarrow$ [`docs/02_CORE_FUNCTIONAL_MODULES.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/02_CORE_FUNCTIONAL_MODULES.md)
  - Database & Migrations $\rightarrow$ [`docs/04_DATA_MODELS_AND_SCHEMA_DESIGN.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/04_DATA_MODELS_AND_SCHEMA_DESIGN.md)
- **Anti-Pattern Prohibited:** Agents must never invent API endpoints, custom fields, or status names that deviate from the established specs.

---

### Protocol 2: Test-Driven Autonomous Generation (TDD for AI)
AI agents generate higher quality code when guided by concrete test assertions.
1. **Red Stage:** Agent creates a test file (e.g. `RentalEngineTest.kt` or `prefill_validator_test.py`) asserting expected behavior. The agent executes the test command using terminal tools and verifies it fails for the expected reason.
2. **Green Stage:** Agent implements the production code until the test passes cleanly.
3. **Edge Case Fuzzing:** The agent must deliberately test boundary conditions:
   - Leap years and timezone boundaries in hydro-test due dates.
   - Cylinder held for exactly the grace period limit ($Day == 15$) vs one day past grace ($Day == 16$).
   - Empty returned batch with zero cylinders vs full truck bed of 120 cylinders.
   - Network failure occurring mid-way through a multi-cylinder scan batch.

---

### Protocol 3: Hermetic Mocking & Sandbox Isolation
To allow AI agents to develop and test without external dependencies:
- **Zoho API Mock Server:**
  - Standardized mock server in `scripts/mock_zoho_server.py` simulating Zoho Books, Inventory, and CRM REST endpoints with configurable latency, rate-limiting (HTTP 429), and failure injection (HTTP 500).
- **In-Memory SQLite for Android Room:**
  - Android DAO unit tests must execute against `Room.inMemoryDatabaseBuilder()` with `allowMainThreadQueries()` for instant sub-second verification without requiring an emulator.
- **Virtual Scan Feeder:**
  - CameraX and RFID tests utilize synthetic data feeds simulating camera QR frame detections and Bluetooth BLE raw byte streams.

---

### Protocol 4: Proof Artifacts & Verification Mandate
- **Rule:** A task cannot be marked `[x]` in [`TASK_QUEUE.md`](file:///home/server/GoogleDrive/CylinderTrackingSystem/TASK_QUEUE.md) on trust. The agent must provide verifiable evidence.
- **Required Evidence:**
  1. Terminal command executed.
  2. Test pass output (e.g., `BUILD SUCCESSFUL`, `12 passed, 0 failed in 1.42s`).
  3. Linter / Static analysis confirmation with zero errors.

---

### Protocol 5: Small-Batch Iteration & Micro-Commit Hygiene
- **Scope Limit:** Agents must keep changes bounded to a single task unit. Never refactor unrelated files or make sweeping stylistic changes across multiple modules simultaneously.
- **Conventional Commits Standard:**
  Every git commit message generated by an agent must follow:
  ```text
  [TASK-ID] <type>(<scope>): <concise description>

  Examples:
  [TASK-201] feat(safety): enforce PESO hydrostatic test due date filling lockout
  [TASK-302] feat(zoho): implement delivery challan dispatcher with idempotency key
  [TASK-401] test(android): add Room DAO unit tests for offline mutation queue
  ```

---

### Protocol 6: Defensive State Machine & Compile-Time Safety
Gas cylinder operations involve hazardous pressurized assets. AI-generated code must prevent invalid states through type-system enforcement:
- **Exhaustive Sealed Classes / Enums:** In Kotlin and TypeScript, use exhaustive pattern matching. Never use raw strings for statuses or gas types.
  ```kotlin
  sealed class CylinderEvent {
      data class Filled(val batchId: String, val pressureBar: Double) : CylinderEvent()
      data class Delivered(val customerId: String, val challanId: String) : CylinderEvent()
      data class EmptyCollected(val customerId: String) : CylinderEvent()
      data class HydroTestOutward(val testStationId: String) : CylinderEvent()
  }
  ```
- **Runtime Precondition Checks:** Critical operations must assert invariants before writing to DB:
  ```kotlin
  check(cylinder.status == CylinderStatus.PLANT_EMPTY) {
      "Cannot transition to FILLING: Current status is ${cylinder.status}"
  }
  ```

---

### Protocol 7: Continuous Self-Correction & Context Compaction
- **Log Inspection Protocol:** If a command or test fails, the agent must read the exact error trace in the task log, formulate a single hypothesis, and apply a surgical fix rather than blindly guessing.
- **Token Efficiency:** When viewing large logs or bundles, use line ranges (`StartLine`/`EndLine`) or grep filters to preserve context window tokens.

---

## 3. Directory Conventions for AI Workflows

```text
CylinderTrackingSystem/
├── .agents/
│   ├── rules/                        # Always-active AI behavioral constraints
│   │   ├── 01_safety_and_compliance.md
│   │   ├── 02_zoho_financial_integrity.md
│   │   ├── 03_android_offline_architecture.md
│   │   ├── 04_code_quality_and_testing.md
│   │   └── agent_workflow.md
│   └── skills/                       # On-demand specialized agent runbooks
│       ├── zoho-sync-engine/
│       └── android-device-testing/
├── docs/                             # The immutable system specifications
├── scripts/
│   ├── mock_zoho_server.py           # Hermetic local mock server for Zoho APIs
│   ├── seed_cylinders.py             # Synthetic test fleet generator (5,000 units)
│   └── verify_all.sh                 # Unified verification runner (lint + test + build)
├── TASK_QUEUE.md                     # Active agent work board with proof checks
└── AGENTS.md                         # Master operating manual for AI agents
```

---

## 4. Unified Verification Protocol (`verify_all.sh`)

Every autonomous agent session concludes by running the unified test runner:
```bash
bash scripts/verify_all.sh
```
This script executes:
1. **Schema Check:** Validates SQL migrations for syntax and constraint integrity.
2. **Backend Tests:** Executes unit and integration test suites against local mocks.
3. **Android Unit Tests:** Runs `./gradlew testDebugUnitTest` verifying Room DAOs and ViewModels.
4. **Zoho Contract Test:** Validates sample JSON payloads against the schemas defined in `docs/08_ZOHO_API_INTERACTIONS_AND_PAYLOAD_SPECIFICATION.md`.
