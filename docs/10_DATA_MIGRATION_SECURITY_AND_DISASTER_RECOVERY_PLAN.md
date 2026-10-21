# Data Migration, Security Architecture & Disaster Recovery Plan
## Enterprise Transition Strategy, Role-Based Access Control (RBAC) & Business Continuity

---

## 1. Data Migration & Cutover Strategy (Phase 0)

Migrating an established industrial or medical gas operation from paper registers, spreadsheets, or legacy desktop software to CTMS and Zoho without halting 24/7 hospital deliveries or industrial plant operations requires a phased **Three-Stage Inward Migration Pipeline**.

```
+--------------------------------------------------------------------------------------------------+
|                                    STAGE 1: ASSET INGESTION                                      |
|  • Bulk Import of Stamped Metal Serials, Tare Weights, Water Capacities & Test Dates from CSV    |
|  • Cleansing & De-duplication Engine: Flag duplicate collar numbers or missing PESO test dates   |
+--------------------------------------------------------------------------------------------------+
                                                 │
                                                 ▼
+--------------------------------------------------------------------------------------------------+
|                               STAGE 2: LIVE RETROFIT & PAIRING                                   |
|  • Physical Tagging Workflow: Laser-etched SS304 2D QR collar plates & UHF RFID tags riveted     |
|  • Pairing Mobile Station: Scan physical stamped serial -> Scan new 2D QR / RFID -> Pair in DB   |
|  • Zero-Disruption Rule: Cylinders tagged during routine return-to-plant cycle over 30 days       |
+--------------------------------------------------------------------------------------------------+
                                                 │
                                                 ▼
+--------------------------------------------------------------------------------------------------+
|                                  STAGE 3: CUTOVER & OPENING BALANCES                             |
|  • Opening Balance Audit: Match customer holding counts against Zoho Books debtor records        |
|  • Cutover Freeze: 24-hour weekend cutoff window for physical gate reconciliation                 |
|  • Day 1 Live Go-Live: Driver app mandatory for all outward gate passes and POD signatures        |
+--------------------------------------------------------------------------------------------------+
```

### 1.1 Bulk Ingestion Data Schemas
Historical records are prepared in standardized CSV templates:
1. `cylinders_opening_master.csv`: `serial_number`, `gas_type`, `water_capacity`, `stamped_tare_weight`, `manufacturer`, `mfg_date`, `last_hydro_test_date`, `hydro_test_station_id`, `ownership` (`COC`/`POC`).
2. `customer_opening_holdings.csv`: `zoho_contact_id`, `customer_name`, `gas_type`, `quantity_held`, `estimated_holding_days`, `active_deposit_amount`.
3. `poc_customer_registry.csv`: Serial numbers strictly registered as party-owned assets linked to specific customer tax IDs.

### 1.2 "Rolling Fleet Tagging" Protocol (Zero Plant Downtime)
Rather than recalling thousands of cylinders simultaneously, tagging is executed as a **rolling gate retrofit**:
- As empty cylinders return from customer routes, they pass through a dedicated **Tagging Bay**.
- A plant technician uses an Android tablet to look up the stamped serial number, affixes the laser-etched metal collar QR / RFID tag, and scans both to link them permanently in the database.
- Tagged cylinders are spray-coded on the shoulder to signify they are active in the CTMS digital fleet.
- Untagged cylinders returning after Day 30 trigger a mandatory gate stop for immediate tag assignment.

---

## 2. Enterprise Security Architecture & RBAC Matrix

CTMS implements Defense-in-Depth, combining cryptographic transport security, token-based authentication, and a strict **Role-Based Access Control (RBAC)** permission matrix.

```
       +-------------------------------------------------------------+
       |               AUTHENTICATION & ACCESS GATEWAY               |
       |  • TLS 1.3 Transport Encryption    • JWT / OAuth 2.0 Auth    |
       |  • Multi-Factor Authentication     • Argon2 Password Hashing |
       +------------------------------+------------------------------+
                                      │
         +----------------------------+----------------------------+
         │                            │                            │
         v                            v                            v
+------------------+         +------------------+         +------------------+
| Plant Operator   |         | Logistics Driver |         | Finance Officer  |
| • Pre-fill check |         | • Scan assigned  |         | • View unbilled  |
| • Batch QA logs  |         |   truck delivery |           rental accruals  |
| • Tare inspection|         | • Collect empties|         | • Push to Zoho   |
| • NO price view  |         | • Capture POD    |         | • Manage deposits|
+------------------+         +------------------+         +------------------+
```

### 2.1 Role-Based Access Control (RBAC) Matrix

| Functional Capability | Super Admin | Plant Manager | Filling Operator | Dispatch Manager | Driver | Finance Officer | Customer Portal |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Register / Scrap Cylinders** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Pre-Fill Safety Validation** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Sign-Off Filling Batch QA** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Create Outward Gate-Pass** | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Scan Delivery & Capture POD** | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Collect Empty Cylinders (ECR)** | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| **View Gas Prices & Invoices** | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ (Own) |
| **Run Monthly Rental Billing** | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Trigger Zoho Books Sync** | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **View PESO Statutory Compliance** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ (Own Certs)|

---

## 3. High Availability & Disaster Recovery Plan

The platform is designed to guarantee business continuity for critical healthcare oxygen and continuous industrial operations.

```
+--------------------------------------------------------------------------------------------------+
|                             HIGH AVAILABILITY DEPLOYMENT ARCHITECTURE                            |
+--------------------------------------------------------------------------------------------------+
|  Primary Availability Zone (AZ-1)               Secondary Availability Zone (AZ-2)               |
|  +-------------------------------------+        +-------------------------------------+          |
|  | PostgreSQL Primary (Read/Write)     | =====> | PostgreSQL Standby (Read-Only)      |          |
|  | Redis Cluster Master                |  Sync  | Redis Cluster Replica               |          |
|  | CTMS API Gateway Instances (Auto)   |        | CTMS API Gateway Instances (Hot)    |          |
|  +-------------------------------------+        +-------------------------------------+          |
+--------------------------------------------------------------------------------------------------+
                                                 │ Continuous WAL Archival
                                                 ▼
+--------------------------------------------------------------------------------------------------+
|                                DISASTER RECOVERY COLD STORAGE (S3)                               |
|  • Point-in-Time Recovery (PITR) up to 35 days                                                    |
|  • Automated Daily Encrypted Full Snapshots (AES-256)                                             |
|  • Cross-Region Geographic Replication (Mumbai -> Hyderabad / Frankfurt -> Dublin)               |
+--------------------------------------------------------------------------------------------------+
```

### 3.1 Service Level Objectives (SLOs)
- **Recovery Point Objective (RPO):** $\le 1\text{ Minute}$ (Zero transactional data loss; synchronous WAL streaming to standby replica).
- **Recovery Time Objective (RTO):** $\le 15\text{ Minutes}$ (Automated health-check failover promoted via Patroni/DNS rerouting).
- **Application Availability:** $99.95\%$ uptime SLA.

### 3.2 Failure Mode Resilience Table

| Failure Scenario | Impact | Automated Resilience Architecture |
| :--- | :--- | :--- |
| **Complete Cellular Outage in Field** | Drivers cannot reach backend servers. | **Offline-First Room DB:** All drop-offs, signatures, and pickups commit locally to encrypted SQLite; WorkManager syncs automatically upon signal recovery. |
| **Zoho Books API Downtime / Maintenance** | Invoices and challans cannot be pushed to Zoho. | **Asynchronous Outbox:** All transactions queue in PostgreSQL/BullMQ; retries resume automatically with exponential backoff; operations never stall. |
| **Physical Tag Scratched / Illegible** | Scanner cannot read 2D QR code. | **Collar Backup Code:** Driver enters 4-digit engraved collar suffix or metal serial number; app provides 1-tap damaged tag re-pairing workflow. |
| **Primary Cloud Zone Outage** | Main server cluster goes offline. | **Multi-AZ Failover:** Automatic promotion of secondary read-replica to primary; traffic rerouted via cloud load balancer health checks. |
