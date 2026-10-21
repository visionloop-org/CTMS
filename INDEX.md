# Cylinder Tracking Management System (CTMS)
## Master Repository Index, File Catalog & Architecture Directory

This document serves as the **authoritative directory and index** of all files within the CTMS repository. Whenever a new file is added, refactored, or deprecated, this index must be updated to reflect the file's path, contents, description, and operational purpose.

---

## 🧭 Repository Structure Overview

```
CylinderTrackingSystem/
├── .agents/                          # Agent-Driven Development (ADD) guidelines, skills & rules
│   ├── proofs/                       # Automated test & link verification proof artifacts
│   ├── rules/                        # Contextual guidelines & non-negotiable invariants
│   └── skills/                       # Specialized runbooks, mocks & procedures
├── android/                          # Native Android Mobile App (Kotlin + Compose + Room)
│   ├── app/                          # App module, Room entities, DAOs, and UI
│   └── build.gradle.kts              # Root Android Gradle build configuration
├── backend/                          # Core Backend API & Integration Server (FastAPI + TimescaleDB)
│   ├── src/                          # Safety engines, state machine, rental, Zoho, and MCP
│   └── tests/                        # Comprehensive automated unit & integration test suites
├── design-guide/                     # Element-by-element UI/UX and hardware interaction specs
├── docs/                             # Exhaustive engineering, domain & integration specifications
├── scripts/                          # Automation, mock servers & fast verification runners
├── AGENTS.md                         # Master ADD guidelines and prime invariants
├── GEMINI.md                         # Gemini CLI & IDE instructions
├── INDEX.md                          # This file: Central repository index & file catalog
├── README.md                         # Master repository landing page & architecture overview
└── TASK_QUEUE.md                     # Engineering backlog & acceptance criteria board
```

---

## 1. Root & Governance Documents

| File | Category | Description | Operational Purpose |
| :--- | :--- | :--- | :--- |
| **[README.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/README.md)** | Root | Executive system summary, business problem statements, high-level architecture diagram, and documentation index. | Serves as the public-facing entry point and high-level architectural map for stakeholders and developers. |
| **[PROJECT_OVERVIEW.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/PROJECT_OVERVIEW.md)** | Root | Comprehensive project overview, architecture blueprint, domain model, operational exception playbooks, and master directory. | Deep-dive guide providing complete end-to-end understanding of business goals, invariants, and technical architecture. |
| **[INDEX.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/INDEX.md)** | Root | Master file directory and catalog detailing every file in the repository, its description, and its purpose. | Provides instant navigation, context anchoring for AI pair programming, and maintenance tracking. |
| **[AGENTS.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/AGENTS.md)** | Governance | Master Agent-Driven Development (ADD) guidelines, 5 Prime Invariants, and Red-Green-Refactor execution protocols. | Guides autonomous AI agents and pair-programmers to enforce safety, offline-first, and financial invariants. |
| **[GEMINI.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/GEMINI.md)** | Governance | Compact instructions and quick-reference invariants for Gemini CLI and IDE pair sessions. | Quick reference for AI pair programming sessions within the Gemini ecosystem. |
| **[TASK_QUEUE.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/TASK_QUEUE.md)** | Backlog | Active engineering backlog broken into epics, stories, acceptance criteria, and verification commands. | Drives autonomous sprint execution; tracks progress from schema migrations to mobile UI. |
| **[docker-compose.yml](file:///home/server/GoogleDrive/CylinderTrackingSystem/docker-compose.yml)** | Infrastructure | Containerized local environment orchestrating PostgreSQL 16 (TimescaleDB), Redis 7, Dgraph standalone, and hermetic mock Zoho server. | Provides reproducible local developer infrastructure and hermetic CI testing environment. |
| **[.env.example](file:///home/server/GoogleDrive/CylinderTrackingSystem/.env.example)** | Config | Template environment variables for local Docker services, database credentials, secrets, and ports. | Documents required configuration and prevents committing production credentials to Git. |
| **[.gitignore](file:///home/server/GoogleDrive/CylinderTrackingSystem/.gitignore)** | Config | Git ignore patterns for Python, Node, Android, Gradle, and OS temporary files. | Prevents build artifacts, virtual environments, and temporary files from being tracked in version control. |

---

## 2. Technical Engineering Specifications (`docs/`)

| File | Spec # | Description | Operational Purpose |
| :--- | :--- | :--- | :--- |
| **[01_SYSTEM_REQUIREMENTS_AND_ARCHITECTURE.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/01_SYSTEM_REQUIREMENTS_AND_ARCHITECTURE.md)** | Spec 01 | Cloud & edge system architecture, technology stack (Python/FastAPI, Kotlin Compose, TimescaleDB), hardware identification (2D QR vs UHF RFID), and security governance. | Defines high-level system boundaries, technology decisions, and multi-tenant SaaS foundation. |
| **[02_CORE_FUNCTIONAL_MODULES.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/02_CORE_FUNCTIONAL_MODULES.md)** | Spec 02 | 10-stage cylinder lifecycle state machine, Company-Owned (COC) vs Party-Owned (POC) rules, filling plant safety interlocks, logistics reconciliation, and progressive rental calculation math. | Defines core domain rules, state machine transitions, and statutory safety interlocks. |
| **[03_ZOHO_ECOSYSTEM_INTEGRATION_SPEC.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/03_ZOHO_ECOSYSTEM_INTEGRATION_SPEC.md)** | Spec 03 | Deep integration blueprint for Zoho Books, Inventory, CRM, Analytics, and Sign; defines the Core Document Triad (`salesorders` = IN, `invoices` = OUT, `deliverychallans` = Security/Rent). | Anchors financial synchronization, inventory transfers, and customer account data flow. |
| **[04_DATA_MODELS_AND_SCHEMA_DESIGN.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/04_DATA_MODELS_AND_SCHEMA_DESIGN.md)** | Spec 04 | Complete PostgreSQL DDL, ENUM definitions, relational tables (`cylinders`, `trips`, `delivery_challans`), and immutable scan ledger (`cylinder_events`). | Provides executable schema definitions, indexes, and database relationship structures. |
| **[05_API_SPECIFICATION_AND_OFFLINE_SYNC.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/05_API_SPECIFICATION_AND_OFFLINE_SYNC.md)** | Spec 05 | REST API contracts, offline-first client SQLite outbox mutation protocol, conflict resolution mechanics, and inbound Zoho webhook handlers. | Governs communication contracts between mobile clients, web portals, and backend services. |
| **[06_IMPLEMENTATION_ROADMAP_AND_MILESTONES.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/06_IMPLEMENTATION_ROADMAP_AND_MILESTONES.md)** | Spec 06 | 24-week phased delivery plan across 5 phases, QA benchmarks (offline sync, scan speed, rate limits), and risk mitigation matrix. | Guides project timeline, sprint planning, milestone verification, and risk management. |
| **[07_NATIVE_ANDROID_APP_SPECIFICATION.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/07_NATIVE_ANDROID_APP_SPECIFICATION.md)** | Spec 07 | Native Android (Kotlin + Jetpack Compose) architecture, CameraX ML Kit scanning, Room DB entities, WorkManager sync, and hardware peripherals (Zebra, Chainway, ESC/POS). | Technical blueprint for building the driver and plant mobile/kiosk applications. |
| **[08_ZOHO_API_INTERACTIONS_AND_PAYLOAD_SPECIFICATION.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/08_ZOHO_API_INTERACTIONS_AND_PAYLOAD_SPECIFICATION.md)** | Spec 08 | Exhaustive JSON request/response payloads, field-by-field mappings, rate limiting (80 req/min), HMAC webhook verification, and idempotency key mechanics. | Implementation reference for building the Zoho integration gateway and message handlers. |
| **[09_AI_DRIVEN_DEVELOPMENT_PROTOCOLS_AND_BEST_PRACTICES.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/09_AI_DRIVEN_DEVELOPMENT_PROTOCOLS_AND_BEST_PRACTICES.md)** | Spec 09 | The 7 AIDD protocols (Spec-First Anchoring, TDD for AI, Hermetic Mocking, Proof Artifacts, Micro-Commit Hygiene, Defensive State Machines, Self-Correction Loops). | Enforces engineering rigor and automated verification for AI agent pair programming. |
| **[10_DATA_MIGRATION_SECURITY_AND_DISASTER_RECOVERY_PLAN.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/10_DATA_MIGRATION_SECURITY_AND_DISASTER_RECOVERY_PLAN.md)** | Spec 10 | Phase 0 rolling fleet retrofit strategy (15k cylinders), 7-role enterprise RBAC permission matrix, and multi-AZ disaster recovery ($\le 1\text{ min}$ RPO, $\le 15\text{ min}$ RTO). | Directs initial operational rollout, user security permissions, and operational continuity. |
| **[11_SYSTEM_UNDERSTANDING_AND_KNOWLEDGE_GRAPH.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/11_SYSTEM_UNDERSTANDING_AND_KNOWLEDGE_GRAPH.md)** | Spec 11 | Domain conceptual model (Container Asset vs Product Gas vs Custodian Agreement triad), Dgraph DQL graph schema, and critical graph query patterns (batch recall, route loss). | Maps complex interconnected domain relationships for operational intelligence and graph querying. |
| **[12_API_KEYS_AND_MCP_SERVER_SPECIFICATION.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/12_API_KEYS_AND_MCP_SERVER_SPECIFICATION.md)** | Spec 12 | Cryptographic API Key Gateway (`X-API-Key`, SHA-256, scopes) for third-party apps and Native Model Context Protocol (MCP) Server (SSE/stdio) for autonomous AI agents. | Enables external software and AI assistants to securely interact with CTMS operations. |
| **[13_HARDWARE_PERIPHERALS_AND_EXCEPTION_PLAYBOOKS.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/13_HARDWARE_PERIPHERALS_AND_EXCEPTION_PLAYBOOKS.md)** | Spec 13 | ESC/POS byte layouts (58mm/80mm e-DC, QR raster), Zebra/Chainway Android broadcast intent handlers, damaged tag re-binding, offline scan collision arbitration, and ghost cylinder yard audit. | Establishes exact byte-level printer/scanner hardware drivers and operational edge playbooks. |
| **[14_STATUTORY_PESO_REPORTING_AND_CUSTOMER_PORTAL.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/14_STATUTORY_PESO_REPORTING_AND_CUSTOMER_PORTAL.md)** | Spec 14 | PESO Rule 35 hydrostatic stretch testing compliance engine, Form III & IV statutory inspection dossiers, and B2B hospital/factory self-service portal (NABH vault, refill/pickup dispatch). | Automates government regulatory reporting and empowers B2B customers with live self-service access. |
| **[15_INFRASTRUCTURE_DOCKER_AND_CI_CD_PIPELINE.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/docs/15_INFRASTRUCTURE_DOCKER_AND_CI_CD_PIPELINE.md)** | Spec 15 | Containerized Docker Compose local topology (PostgreSQL 16, TimescaleDB, PostGIS, Redis 7, Dgraph) and GitHub Actions CI/CD pipeline automation. | Guarantees local reproducible developer environments and automated pull-request verification. |

---

## 3. Element-Wise Design System & UI Guide (`design-guide/`)

| File | Module | Description | Operational Purpose |
| :--- | :--- | :--- | :--- |
| **[design-guide/README.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/README.md)** | Design Overview | Master design guide summary, industrial UX design principles, and component categorization. | Sets design standards for rugged, sunlight-readable, glove-friendly mobile and kiosk UIs. |
| **[01_COLOR_SYSTEM_AND_THEMING.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/01_COLOR_SYSTEM_AND_THEMING.md)** | Design 01 | WCAG AAA contrast tokens, PESO statutory cylinder body/shoulder colors (O2, Ar, N2, CO2), ownership chips (COC/POC/VOC), and high-contrast sunlight mode. | Enforces statutory color accuracy and maximum readability in direct outdoor sunlight. |
| **[02_TYPOGRAPHY_AND_ICONS.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/02_TYPOGRAPHY_AND_ICONS.md)** | Design 02 | Inter & Roboto Mono typography, tabular numbers (`tnum`) for jitter-free scanning counters, dynamic font scaling, and industrial icon tokens. | Ensures serial numbers, pressure readings, and counters remain readable under motion and vibration. |
| **[03_FOUNDATIONAL_UI_ELEMENTS.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/03_FOUNDATIONAL_UI_ELEMENTS.md)** | Design 03 | 56dp oversized primary CTAs (glove-friendly), numeric keypad components, 10-state lifecycle status chips, and persistent offline sync badges. | Provides standardized touch targets and state indicators suitable for industrial warehouse workers. |
| **[04_SPECIALIZED_SCANNER_AND_HARDWARE_ELEMENTS.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/04_SPECIALIZED_SCANNER_AND_HARDWARE_ELEMENTS.md)** | Design 04 | CameraX $250\times 250\text{ dp}$ reticle with corner brackets, continuous scan HUD, ToneGenerator audio (2,500Hz vs 350Hz), and tactile haptics. | Specifies high-speed, sub-100ms multi-cylinder scanning ergonomics and multi-sensory feedback. |
| **[05_DOMAIN_CYLINDER_AND_CHALLAN_ELEMENTS.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/05_DOMAIN_CYLINDER_AND_CHALLAN_ELEMENTS.md)** | Design 05 | Serialized cylinder asset cards, PESO hydro-test countdown gauges (Green $\rightarrow$ Amber $\rightarrow$ Crimson), digital e-signature canvas, and e-DC print layouts. | Standardizes asset passports, safety gauges, digital proof of delivery, and thermal receipt layouts. |
| **[06_STATE_AND_INTERACTION_PATTERNS.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/design-guide/06_STATE_AND_INTERACTION_PATTERNS.md)** | Design 06 | Full-screen crimson PESO safety hard lockout modal (non-dismissible 403), trip reconciliation truck balance delta tables, and spring micro-interactions. | Guarantees critical safety rejections cannot be dismissed and truck load balance deltas are visually obvious. |

---

## 4. Agent Customization System (`.agents/`)

### 4.1 Specialized Domain Agents (`.agents/agents/`)
| File | Domain Specialist | Core Responsibilities | Operational Purpose |
| :--- | :--- | :--- | :--- |
| **[.agents/agents/README.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/README.md)** | Swarm Overview | Master agent fleet architecture, topology diagram, domain directory, and cross-agent handoff protocols. | Coordinates swarm collaboration and defines handoff contracts across all 8 specialists. |
| **[01_zoho_integration_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/01_zoho_integration_agent.md)** | Zoho Ecosystem | Books, Inventory, CRM, Analytics & Sign synchronization; Document Triad (`salesorders` = IN, `invoices` = OUT, `deliverychallans` = Security/Rent). | Enforces financial idempotency, 80 req/min rate limit, and multi-ownership POC rental exemption. |
| **[02_android_app_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/02_android_app_agent.md)** | Native Android App | Pure Kotlin 2.0+ & Jetpack Compose, Room SQLite DB, CameraX ML Kit scanning, WorkManager sync, and BLE RFID sleds. | Delivers offline-first field resilience, sub-100ms camera scans, and glove-friendly 56dp ergonomics. |
| **[03_backend_api_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/03_backend_api_agent.md)** | Core Backend & API | Python 3.12+ (FastAPI), Celery worker queues, 10-stage lifecycle state machine, and rental billing engine. | Enforces statutory PESO filling lockouts, deterministic state transitions, and progressive holding slab math. |
| **[04_industrial_design_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/04_industrial_design_agent.md)** | Industrial Design & UI/UX | Design tokens, WCAG AAA sunlight theme, PESO gas colors (O2, Ar, N2, CO2), tabular numbers (`tnum`), and 56dp CTAs. | Guarantees visual excellence, high-contrast sunlight readability, and multi-sensory feedback. |
| **[05_interaction_protocol_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/05_interaction_protocol_agent.md)** | Integration & AI Gateway | Cryptographic API Key Gateway (`X-API-Key`, SHA-256), Model Context Protocol (MCP) server, external ERPs (SAP/Oracle). | Exposes secure REST endpoints for third-party apps and native MCP tools/resources for external AI agents. |
| **[06_database_ledger_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/06_database_ledger_agent.md)** | Database & Ledger | PostgreSQL 16 DDL, TimescaleDB weekly hypertable partitioning, compression policies, and Dgraph DQL graph schemas. | Maintains the immutable lifetime `cylinder_events` ledger and sub-50ms batch contamination graph recalls. |
| **[07_agent_coordinator.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/07_agent_coordinator.md)** | Swarm Coordinator | Backlog task dispatching, Scrum Master oversight, cross-domain conflict resolution, and `INDEX.md` maintenance. | Upholds the 5 Prime Invariants across the swarm and prevents breaking architectural regressions. |
| **[08_quality_test_agent.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/agents/08_quality_test_agent.md)** | QA & Test Harness | TDD Red-Green-Refactor enforcement, hermetic mock servers (`mock_zoho_server.py`), link auditing, and proof artifacts. | Acts as the single automated gatekeeper ensuring zero-defect releases via `verify_all.sh`. |

### 4.2 Operational Rules (`.agents/rules/`)
| File | Scope | Invariant / Policy Enforced | Operational Purpose |
| :--- | :--- | :--- | :--- |
| **[01_safety_and_compliance.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/rules/01_safety_and_compliance.md)** | Safety | Hard filling interlock: Reject any cylinder where `NOW() >= hydro_test_due_date` with HTTP 403. | Protects plant life safety and statutory PESO compliance. |
| **[02_zoho_financial_integrity.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/rules/02_zoho_financial_integrity.md)** | Finance | Mandatory idempotency keys, 80 req/min rate limit, POC rental exemption, and Zoho Document Triad semantics. | Prevents double-billing and preserves financial reconciliation integrity. |
| **[03_android_offline_architecture.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/rules/03_android_offline_architecture.md)** | Mobile | Offline-first Room DB write precedence, outbox event queueing, non-blocking UI threads. | Guarantees zero field transaction loss during cellular network blackouts. |
| **[04_code_quality_and_testing.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/rules/04_code_quality_and_testing.md)** | Quality | Red-Green-Refactor testing protocol, hermetic mocking, zero external network dependencies. | Enforces software testability and prevents regression bugs. |
| **[05_api_keys_and_ai_mcp.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/rules/05_api_keys_and_ai_mcp.md)** | API & AI | SHA-256 API key hash storage, granular RBAC scopes, MCP PESO safety interlocks, human-in-the-loop locks. | Governs third-party developer access and external autonomous AI agent interactions. |
| **[agent_workflow.md](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/rules/agent_workflow.md)** | Workflow | Step-by-step TDD lifecycle, task queue state tracking, proof artifact generation. | Standardizes AI pair programming procedure from backlog task selection to verification. |

### 4.3 Specialized Agent Skills (`.agents/skills/`)
| File | Skill Name | Description | Operational Purpose |
| :--- | :--- | :--- | :--- |
| **[SKILL.md (zoho-sync-engine)](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/skills/zoho-sync-engine/SKILL.md)** | `zoho-sync-engine` | Runbook for bidirectional Zoho Books, Inventory, CRM, and Analytics synchronization. | Guides implementation, mocking, and debugging of Zoho Cloud Suite integration. |
| **[SKILL.md (android-device-testing)](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/skills/android-device-testing/SKILL.md)** | `android-device-testing` | Runbook for testing Kotlin Compose UI, Room SQLite outbox, CameraX scanning, and BLE RFID readers. | Guides Android client development, hardware simulation, and offline outbox testing. |
| **[SKILL.md (peso-safety-engine)](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/skills/peso-safety-engine/SKILL.md)** | `peso-safety-engine` | Runbook and test scripts for hydrostatic test due dates, tare weight loss ($>5\%$), and filling lockout. | Directs pre-fill safety interlock validation and compliance testing. |
| **[SKILL.md (rental-billing-engine)](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/skills/rental-billing-engine/SKILL.md)** | `rental-billing-engine` | Runbook for daily holding fee calculations, progressive rental slabs, POC exemption, and Zoho Books invoices. | Ensures mathematical accuracy of holding fee accruals and monthly billing runs. |
| **[SKILL.md (mcp-gateway-engine)](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/skills/mcp-gateway-engine/SKILL.md)** | `mcp-gateway-engine` | Runbook for testing the native Model Context Protocol (MCP) server, tools, SSE endpoints, and API key rate limiting. | Facilitates running, testing, and debugging AI agent interfaces and third-party developer APIs. |
| **[SKILL.md (database-event-ledger)](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/skills/database-event-ledger/SKILL.md)** | `database-event-ledger` | Runbook for TimescaleDB hypertable partitioning, compression policies, and Dgraph knowledge graph recall queries. | Manages high-throughput scan event series storage and complex graph relationship queries. |

### 4.4 Proof Artifacts (`.agents/proofs/`)
| File | Category | Description | Operational Purpose |
| :--- | :--- | :--- | :--- |
| **[latest_verification.json](file:///home/server/GoogleDrive/CylinderTrackingSystem/.agents/proofs/latest_verification.json)** | Proof Artifact | JSON verification proof capturing the timestamp, status, spec counts, rule counts, link integrity, and mock server syntax. | Auditable proof artifact generated by `scripts/verify_all.sh` asserting all quality gates pass [GREEN]. |

---

## 5. Automation, Testing & Mocking Scripts (`scripts/`)

| File | Language | Description | Operational Purpose |
| :--- | :--- | :--- | :--- |
| **[scripts/mock_zoho_server.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/scripts/mock_zoho_server.py)** | Python 3 | Lightweight, hermetic HTTP mock server simulating Zoho Books (`/salesorders`, `/deliverychallans`, `/invoices`), Inventory (`/transferorders`), and CRM APIs. | Enables offline, isolated integration testing with idempotency key validation without live Zoho credentials. |
| **[scripts/verify_markdown_links.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/scripts/verify_markdown_links.py)** | Python 3 | High-speed, zero-FUSE-lag link auditor that parses all markdown files in the repository and verifies that every `file://` link resolves with 100% integrity. | Prevents broken links and documentation drift across the entire project repository. |
| **[scripts/check_file_lengths.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/scripts/check_file_lengths.py)** | Python 3 | Fast file length linter asserting that no source code, configuration, or documentation file exceeds 1,000 lines. | Enforces Prime Invariant #6 (Strict Modular File Limit < 1,000 lines) across the codebase. |
| **[scripts/verify_all.sh](file:///home/server/GoogleDrive/CylinderTrackingSystem/scripts/verify_all.sh)** | Bash | Master CI/verification runner; executes specification checks, markdown link audits, rule/skill assertions, file length limits, and Python syntax compilation. | Single-command gatekeeper validating that all specifications, design guides, rules, and skills pass before marking tasks done. |

---

## 6. Core Backend Services & API Gateway (`backend/`)

| File | Subsystem | Description | Operational Purpose |
| :--- | :--- | :--- | :--- |
| **[backend/requirements.txt](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/requirements.txt)** | Config | Python backend dependencies (FastAPI, Uvicorn, Pydantic, HTTPX, Pytest, Redis, AsyncPG). | Defines runtime and testing packages for the CTMS API server. |
| **[backend/src/config.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/config.py)** | Core | Environment settings, database connection URLs, Zoho credentials, and safety threshold configs. | Centralized typed configuration loaded from environment variables with safe defaults. |
| **[backend/src/main.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/main.py)** | Application | FastAPI application entry point, CORS middleware, and API router attachment. | Initializes and launches the REST API server and MCP endpoints. |
| **[backend/src/api/routes.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/api/routes.py)** | REST API | Endpoints for `/health`, `/api/v1/filling/pre-check`, `/api/v1/cylinders/transition`, `/api/v1/rental/calculate-single`, and `/mcp/*`. | Exposes REST interfaces for mobile clients, web consoles, and external integrations. |
| **[backend/src/database/migrations/001_initial_schema.sql](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/database/migrations/001_initial_schema.sql)** | Database | Initial PostgreSQL DDL script creating all 18 tables, enums, indexes, and constraints. | Deploys relational schema for multi-tenant assets, trips, customers, challans, and outboxes. |
| **[backend/src/database/migrations/002_timescale_setup.sql](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/database/migrations/002_timescale_setup.sql)** | Database | TimescaleDB hypertable setup for `cylinder_events` partitioned by 7 days with 30-day compression. | Enables high-throughput scan event ingestion and cost-effective long-term storage. |
| **[backend/src/modules/safety/peso_engine.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/modules/safety/peso_engine.py)** | Safety Engine | Pre-fill check service validating hydro-test due date, gas compatibility, and $\le 5\%$ tare loss. | Enforces Prime Rule #1 (PESO zero-tolerance interlock; 403 Forbidden on expired test). |
| **[backend/src/modules/lifecycle/state_machine.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/modules/lifecycle/state_machine.py)** | State Machine | 10-state deterministic cylinder lifecycle validator generating immutable scan events. | Enforces Prime Rule #2 (Immutable scan audit trail; prevents illegal state skips). |
| **[backend/src/modules/rental/calculator.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/modules/rental/calculator.py)** | Rental Engine | Automated progressive holding calculation engine across contract tiers with POC zero-rent exemption. | Enforces Prime Rule #3 (Party-Owned Cylinders strictly exempt from rental charges). |
| **[backend/src/integrations/zoho/oauth.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/integrations/zoho/oauth.py)** | Zoho Integration | Zoho OAuth 2.0 token manager maintaining active access tokens with auto-refresh. | Provides uninterrupted authenticated API connectivity to Zoho Cloud services. |
| **[backend/src/integrations/zoho/books_client.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/integrations/zoho/books_client.py)** | Zoho Integration | Zoho Books API client for creating Delivery Challans and Tax Invoices with mandatory idempotency keys. | Enforces Prime Rule #5 (Financial idempotency; prevents duplicate invoices and challans). |
| **[backend/src/mcp/auth.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/mcp/auth.py)** | Gateway & Auth | SHA-256 API key authenticator with RBAC scopes (`cylinders:read`, `safety:verify`) and leaky-bucket rate limiting. | Secures third-party developer access and external AI agent queries. |
| **[backend/src/mcp/server.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/src/mcp/server.py)** | MCP Server | Native Model Context Protocol server exposing operational tools and live streaming resources. | Enables external autonomous AI agents to query cylinder passports and verify safety. |
| **[backend/tests/run_tests.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/tests/run_tests.py)** | Testing | Standalone verification test runner executing all backend unit test suites with zero overhead. | Verifies all 5 Prime Invariants in a single command with green pass assertion. |
| **[backend/tests/test_peso_safety.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/tests/test_peso_safety.py)** | Testing | Unit test suite for PESO safety engine (overdue 403 lockout, tare loss, gas mismatch). | Asserts Prime Rule #1 behavior under diverse compliance edge cases. |
| **[backend/tests/test_state_machine.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/tests/test_state_machine.py)** | Testing | Unit test suite for 10-state cylinder transition validator and terminal scrapped state. | Asserts Prime Rule #2 behavior and illegal transition rejections. |
| **[backend/tests/test_rental_engine.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/tests/test_rental_engine.py)** | Testing | Unit test suite for progressive rental slabs, mixed customer fleets, and POC zero-rent. | Asserts Prime Rule #3 mathematical correctness. |
| **[backend/tests/test_api_keys_and_mcp.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/tests/test_api_keys_and_mcp.py)** | Testing | Unit test suite for API key authentication, permission scopes, and MCP tool dispatch. | Asserts security and MCP protocol conformance. |
| **[backend/tests/test_zoho_integration.py](file:///home/server/GoogleDrive/CylinderTrackingSystem/backend/tests/test_zoho_integration.py)** | Testing | Unit test suite asserting mandatory Idempotency-Key validation on Zoho Books transactions. | Asserts Prime Rule #5 financial duplicate protection. |

---

## 7. Native Android Mobile Client (`android/`)

| File | Subsystem | Description | Operational Purpose |
| :--- | :--- | :--- | :--- |
| **[android/settings.gradle.kts](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/settings.gradle.kts)** | Build | Root Android Gradle settings configuring plugin management and repository resolution. | Defines project root and module dependencies (`:app`). |
| **[android/build.gradle.kts](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/build.gradle.kts)** | Build | Top-level Gradle build script configuring Android application, Kotlin, KSP, and Hilt plugins. | Manages global plugin versions and build configurations. |
| **[android/gradle.properties](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/gradle.properties)** | Build | JVM heap memory settings, AndroidX flags, and Kotlin official code styling. | Optimizes Gradle build performance and sets Android runtime flags. |
| **[android/app/build.gradle.kts](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/app/build.gradle.kts)** | Build | App-level build script declaring Compose, Room SQLite, WorkManager, CameraX, and Hilt dependencies. | Compiles the Android driver mobile application with Kotlin 2.0. |
| **[android/app/src/main/AndroidManifest.xml](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/app/src/main/AndroidManifest.xml)** | Manifest | Android manifest declaring Camera, Bluetooth, Location, Network, and Vibrate permissions. | Configures application components, hardware permissions, and main activity launcher. |
| **[android/app/src/main/java/com/ctms/app/CTMSApplication.kt](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/app/src/main/java/com/ctms/app/CTMSApplication.kt)** | Application | Android Application class initializing application context and dependency injection. | Application-level initialization and global state container. |
| **[android/app/src/main/java/com/ctms/app/presentation/MainActivity.kt](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/app/src/main/java/com/ctms/app/presentation/MainActivity.kt)** | Presentation | Jetpack Compose entry activity rendering full-screen Material 3 interface. | UI host activity for driver mobile workflows and continuous scanner views. |
| **[android/app/src/main/java/com/ctms/app/data/local/AppDatabase.kt](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/app/src/main/java/com/ctms/app/data/local/AppDatabase.kt)** | Local Storage | Room SQLite database holding cylinder cache, outbox mutations, and delivery challans. | Local persistent storage engine powering offline-first operations. |
| **[android/app/src/main/java/com/ctms/app/data/local/entity/CylinderCacheEntity.kt](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/app/src/main/java/com/ctms/app/data/local/entity/CylinderCacheEntity.kt)** | Local Entity | Room entity caching cylinder assets with unique indexes on Serial, QR UID, and RFID EPC. | Enables instant sub-10ms cylinder identification in offline field environments. |
| **[android/app/src/main/java/com/ctms/app/data/local/entity/OutboxMutationEntity.kt](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/app/src/main/java/com/ctms/app/data/local/entity/OutboxMutationEntity.kt)** | Local Entity | Room entity storing queued mutations with idempotency keys and retry counters. | Enforces Prime Rule #4 (Transactional offline outbox; guarantees zero transaction loss). |
| **[android/app/src/main/java/com/ctms/app/data/local/entity/DeliveryChallanEntity.kt](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/app/src/main/java/com/ctms/app/data/local/entity/DeliveryChallanEntity.kt)** | Local Entity | Room entity for local delivery challans, receiver details, digital signatures, and GPS stamps. | Captures digital proof of delivery (e-POD) locally before server synchronization. |
| **[android/app/src/main/java/com/ctms/app/data/local/dao/CylinderDao.kt](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/app/src/main/java/com/ctms/app/data/local/dao/CylinderDao.kt)** | DAO | Room Data Access Object for fast indexed cylinder lookup by Serial, QR, or RFID EPC. | Powers real-time camera and RFID scanning validation in the mobile UI. |
| **[android/app/src/main/java/com/ctms/app/data/local/dao/OutboxDao.kt](file:///home/server/GoogleDrive/CylinderTrackingSystem/android/app/src/main/java/com/ctms/app/data/local/dao/OutboxDao.kt)** | DAO | Room Data Access Object for enqueueing mutations, querying pending queue, and updating sync states. | Interfaces with Jetpack WorkManager `SyncWorker` for resilient background synchronization. |

---

## 🔄 Index Maintenance Protocol for Agents & Developers

When modifying the codebase or adding new files:
1. **New File Created:** Append a row to the appropriate table above with clickable link, category, description, and operational purpose.
2. **File Modified:** Update the description if the responsibilities or interfaces change.
3. **File Deleted/Moved:** Update or remove the corresponding row; ensure no dangling links remain.
4. **Verification:** Run `bash scripts/verify_all.sh` to ensure `INDEX.md` and all cross-document markdown links pass with 100% integrity.
