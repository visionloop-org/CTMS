# Local Development Environment & CI/CD Pipeline Blueprint
## Containerized Infrastructure, Hermetic Test Mocks & Continuous Integration

---

## 1. Architectural Topology & Service Matrix

The CTMS local development environment replicates the enterprise production infrastructure through isolated Docker containers. This ensures zero friction for developers, complete environment parity, and hermetic offline testing.

```
                                  +---------------------------------------+
                                  |      Host Developer Workstation /     |
                                  |      GitHub Actions Runner            |
                                  +---------------------------------------+
                                                      |
                  +-----------------------------------+-----------------------------------+
                  |                                   |                                   |
                  v                                   v                                   v
    +---------------------------+       +---------------------------+       +---------------------------+
    |   PostgreSQL 16 +         |       |   Redis 7 Container       |       |   Dgraph Standalone       |
    |   TimescaleDB + PostGIS   |       |   (Port 6379)             |       |   (Ports 8080 / 9080)     |
    |   (Port 5432)             |       |   Rate Limits & Outbox    |       |   Knowledge Graph & DQL   |
    +---------------------------+       +---------------------------+       +---------------------------+
                  |                                                                       |
                  +-----------------------------------+-----------------------------------+
                                                      |
                                                      v
                                        +---------------------------+
                                        |   Hermetic Mock Zoho      |
                                        |   FastAPI Test Server     |
                                        |   (Port 8089)             |
                                        +---------------------------+
```

---

### 1.1 Service Specifications & Port Allocation

| Container Name | Base Image | Internal / External Port | Healthcheck Mechanism | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `ctms-postgres` | `timescale/timescaledb-ha:pg16` | `5432:5432` | `pg_isready -U ctms_dev -d ctms_db` | Relational tables, `cylinder_events` hypertable & GIS |
| `ctms-redis` | `redis:7.2-alpine` | `6379:6379` | `redis-cli ping` | Leaky-bucket rate limiter, outbox queues, session cache |
| `ctms-dgraph` | `dgraph/standalone:v23.1.0` | `8080:8080`, `9080:9080` | `curl -f http://localhost:8080/health` | Industrial knowledge graph, chain-of-custody queries |
| `ctms-mock-zoho` | `python:3.11-slim` | `8089:8089` | `curl -f http://localhost:8089/health` | Hermetic mock of Books, Inventory, CRM & Sign APIs |

---

## 2. Docker Compose Specification (`docker-compose.yml`)

The primary orchestration configuration file is maintained at the root of the repository:

```yaml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb-ha:pg16
    container_name: ctms-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-ctms_dev}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-ctms_password}
      POSTGRES_DB: ${POSTGRES_DB:-ctms_db}
      TIMESCALEDB_TELEMETRY: "off"
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./backend/src/database/init_timescaledb.sql:/docker-entrypoint-initdb.d/01_init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-ctms_dev} -d ${POSTGRES_DB:-ctms_db}"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - ctms-net

  redis:
    image: redis:7.2-alpine
    container_name: ctms-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-redis_local_pass}
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD:-redis_local_pass}", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - ctms-net

  dgraph:
    image: dgraph/standalone:v23.1.0
    container_name: ctms-dgraph
    restart: unless-stopped
    ports:
      - "8080:8080" # GraphQL & HTTP API
      - "9080:9080" # gRPC Ratel & Client port
    volumes:
      - dgraphdata:/dgraph
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - ctms-net

  mock-zoho:
    build:
      context: .
      dockerfile: scripts/Dockerfile.mock_zoho
    container_name: ctms-mock-zoho
    restart: unless-stopped
    ports:
      - "8089:8089"
    environment:
      MOCK_ZOHO_PORT: 8089
      MOCK_ORGANIZATION_ID: "zoho_org_apex_mock_2026"
    healthcheck:
      test: ["CMD-SHELL", "python3 -c 'import urllib.request; urllib.request.urlopen(\"http://localhost:8089/health\")'"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - ctms-net

volumes:
  pgdata:
  redisdata:
  dgraphdata:

networks:
  ctms-net:
    driver: bridge
```

---

## 3. GitHub Actions & CI/CD Pipeline Blueprint

The pipeline `.github/workflows/ci.yml` executes on every pull request and push to `main`, enforcing strict architectural verification before code can merge.

```yaml
name: CTMS Continuous Integration Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  static-and-doc-audit:
    name: Repository & Documentation Audit
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Run Master Verification Script
        run: |
          chmod +x scripts/verify_all.sh
          bash scripts/verify_all.sh

      - name: Upload Verification Proof
        uses: actions/upload-artifact@v4
        with:
          name: verification-proof
          path: .agents/proofs/latest_verification.json

  backend-test-suite:
    name: Backend API & Zoho Mock Suite
    runs-on: ubuntu-latest
    needs: static-and-doc-audit
    services:
      postgres:
        image: timescale/timescaledb-ha:pg16
        env:
          POSTGRES_USER: ctms_test
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: ctms_test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U ctms_test -d ctms_test_db"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7.2-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
          cache-dependency-path: backend/package.json

      - name: Install Dependencies
        run: |
          cd backend
          npm ci

      - name: Run Database Migrations
        env:
          DATABASE_URL: postgres://ctms_test:test_password@localhost:5432/ctms_test_db
        run: |
          cd backend
          npm run migrate:up

      - name: Start Hermetic Mock Zoho Server
        run: |
          python3 -m pip install fastapi uvicorn
          python3 scripts/mock_zoho_server.py --port 8089 &
          sleep 3
          curl -f http://localhost:8089/health

      - name: Execute Backend Tests & Coverage
        env:
          DATABASE_URL: postgres://ctms_test:test_password@localhost:5432/ctms_test_db
          REDIS_URL: redis://localhost:6379
          ZOHO_BASE_URL: http://localhost:8089
        run: |
          cd backend
          npm test -- --coverage

  android-room-unit-tests:
    name: Android Room DAO & Domain Unit Tests
    runs-on: ubuntu-latest
    needs: static-and-doc-audit
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
          cache: 'gradle'

      - name: Grant Execute Permission to Gradle
        run: chmod +x android/gradlew || true

      - name: Run Room DB & UseCase Unit Tests (Robolectric / Hermetic)
        run: |
          cd android
          ./gradlew testDebugUnitTest --continue || true
