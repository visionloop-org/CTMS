# Agent Workflow & Testing Guidelines

## Rules for Agents Working on CTMS

1. **Check Prior Art Before Creating:**
   - Always check `docs/` and existing database models in `docs/04_DATA_MODELS_AND_SCHEMA_DESIGN.md` before inventing new entity types, status names, or API contracts.
   
2. **Deterministic State Changes:**
   - All cylinder status changes must strictly adhere to the state transition graph documented in `docs/02_CORE_FUNCTIONAL_MODULES.md`.
   - Never skip intermediate safety inspection states (`UNDER_INSPECTION`, `FILLING`, `QA_CHECK`).

3. **Android Clean Architecture Enforcement:**
   - Presentation layer (Jetpack Compose screens & ViewModels) must NEVER call database DAOs or network APIs directly.
   - Always route through Domain UseCases or Repositories.
   - All business logic that validates hydro-test dates, ownership flags, and serial number formatting must be covered by JUnit 5 unit tests.

4. **Testing & Verification Standard:**
   - For backend APIs: Provide unit tests and integration tests using mocks for external Zoho API responses.
   - For Android: Write unit tests for ViewModels and Room DAOs.
   - Validate any newly generated script or migration by running it with dry-run flags.
