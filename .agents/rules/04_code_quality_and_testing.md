# Rule: Code Quality, Testing & Verification Protocol

## Standards for Code Changes, Refactoring & Pull Requests

1. **Test-First Verification:**
   - No task in `TASK_QUEUE.md` may be marked as complete without executing automated unit tests, lint checks, or dry-run scripts.
   - For Android: ViewModels, Room DAOs, and UseCases must be covered by JUnit / MockK unit tests.
   - For Backend: Domain business logic (e.g., rental slab rate calculators, pre-fill safety validators) must achieve $>90\%$ test branch coverage.

2. **Clean Architecture Separation:**
   - **Data Layer:** Room Entities, Retrofit API Services, DAOs, DTOs, Mappers.
   - **Domain Layer:** Pure Kotlin/TypeScript UseCases, Domain Models, Business Validators (zero framework dependencies).
   - **Presentation Layer:** Jetpack Compose UI Screens, ViewModels, UI State.
   - UI Composables must never query database DAOs or API services directly.

3. **Database Migration Safety:**
   - Never modify existing migration files once committed. Always create forward-only migration scripts.
   - Every migration must include a corresponding rollback script.

4. **Documentation & Clickable Links:**
   - All generated code files, schemas, and specifications must maintain clear markdown cross-links using the standard format (e.g. [README.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/README.md)).

5. **Strict File Length Limit (< 1,000 Lines):**
   - Under no circumstances may any file (source code, configuration, database migration, or markdown document) exceed **1,000 lines**.
   - Any file approaching 800 lines must be proactively refactored and decomposed into smaller, single-responsibility modules or sub-documents.
