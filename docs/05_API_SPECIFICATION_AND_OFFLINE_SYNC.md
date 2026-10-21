# API Specification & Offline-First Sync Protocol
## REST API Design, Mobile Sync Protocol & Webhook Endpoints

---

## 1. Offline-First Mobile Sync Architecture

Drivers and delivery agents frequently enter basements, industrial fabrication plants, and rural hospitals without cellular reception. The mobile application operates using an **Offline-First Event-Outbox Pattern**.

```
[ Mobile Device (SQLite / WatermelonDB) ]
   |
   | 1. User performs action (e.g. Scan 20 Cylinders, Sign POD)
   v
[ Local Transactional Outbox Table ]
   - Enqueue Mutation: { client_event_id, event_type, payload, local_timestamp, status='QUEUED' }
   - Immediate UI update (Optimistic UI)
   |
   | 2. Network Connectivity Detected (Network Daemon / Ping)
   v
[ Sync Engine: POST /api/v1/sync/batch-mutations ]
   |
   | 3. Transport with Idempotency Key & Authorization Bearer
   v
[ CTMS API Gateway & Conflict Resolution Engine ]
   - Verify Idempotency-Key
   - Deduplicate scans already accepted
   - Validate State Transitions (e.g. check if cylinder was already returned)
   - Commit to PostgreSQL in single atomic transaction
   - Enqueue downstream Zoho Sync Event
   |
   | 4. Sync Response (200 OK)
   v
[ Mobile Database Updates ]
   - Mark outbox mutations as 'COMMITTED'
   - Pull Server Deltas since 'last_sync_seq' (Updated customer balances, new orders)
```

---

## 2. Core REST Endpoints

### 2.1 Authentication & Device Session
```http
POST /api/v1/auth/login
Content-Type: application/json

Request:
{
  "username": "driver_rajesh",
  "password": "SecurePassword123!",
  "device_id": "MBL-SM-G998B-7721",
  "app_version": "2.4.0"
}

Response (200 OK):
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "def50200...",
  "user": {
    "id": "c1f106d8-...",
    "full_name": "Rajesh Kumar",
    "role": "DRIVER",
    "assigned_vehicle_reg": "MH-04-AB-1234",
    "assigned_plant_id": "p001-..."
  }
}
```

---

### 2.2 Offline Batch Mutation Sync Endpoint
```http
POST /api/v1/sync/batch-mutations
Content-Type: application/json
Authorization: Bearer <JWT>
X-Device-Id: MBL-SM-G998B-7721

Request:
{
  "client_sync_batch_id": "sync-batch-20261101-0941",
  "last_synced_sequence": 14920,
  "mutations": [
    {
      "mutation_id": "mut-a189-98124",
      "event_type": "DELIVERY_COMPLETED",
      "timestamp": "2026-11-01T10:14:22Z",
      "payload": {
        "trip_id": "tr-20261101-01",
        "customer_id": "c-99120-...",
        "challan_type": "DELIVERY_FILLED",
        "scanned_cylinders": [
          { "cylinder_id": "cyl-ox-0012", "condition": "INTACT" },
          { "cylinder_id": "cyl-ox-0014", "condition": "INTACT" }
        ],
        "empties_collected": [
          { "cylinder_id": "cyl-ox-0891", "condition": "INTACT" }
        ],
        "receiver_name": "Amit Sharma (Store Manager)",
        "receiver_phone": "+919876543210",
        "otp_code": "4891",
        "signature_svg_base64": "data:image/svg+xml;base64,...",
        "geo_latitude": 19.0760,
        "geo_longitude": 72.8777
      }
    }
  ]
}

Response (200 OK):
{
  "success": true,
  "processed_mutations": [
    {
      "mutation_id": "mut-a189-98124",
      "status": "COMMITTED",
      "server_document_id": "dc-2026-008129",
      "zoho_sync_enqueued": true
    }
  ],
  "server_deltas": {
    "new_sequence": 14925,
    "customer_updates": [],
    "trip_status": "IN_PROGRESS"
  }
}
```

---

### 2.3 Filling Station Gate & Safety Validation API
Used by plant touchscreen tablets or automated RFID filling manifolds.

```http
POST /api/v1/filling/pre-check
Content-Type: application/json
Authorization: Bearer <JWT>

Request:
{
  "cylinder_scan_code": "CYL-OX-47L-009281", -- Tag barcode or RFID EPC
  "manifold_gas_type": "OXYGEN_MEDICAL",
  "plant_id": "plant-mumbai-01"
}

Response (200 OK - Approved):
{
  "allowed": true,
  "cylinder_id": "908a71b2-...",
  "serial_number": "OX-47-9281",
  "ownership": "COC",
  "tare_weight_stamped": 52.4,
  "hydro_test_valid_until": "2028-04-30",
  "days_until_hydro_due": 546,
  "message": "Cylinder approved for filling. Mount to manifold bay."
}

Response (403 Forbidden - Hard Safety Rejection):
{
  "allowed": false,
  "cylinder_id": "908a71b2-...",
  "serial_number": "OX-47-1044",
  "error_code": "HYDRO_TEST_OVERDUE",
  "hydro_test_due_date": "2026-09-15",
  "message": "PESO HARD LOCK: Hydrostatic testing overdue by 47 days. FILLING FORBIDDEN. Divert to hydro testing yard."
}
```

---

### 2.4 Customer Rental Live Audit & Balance API
Returns customer's real-time holding inventory and projected rental fees.

```http
GET /api/v1/customers/{customer_id}/cylinder-balance
Authorization: Bearer <JWT>

Response (200 OK):
{
  "customer_id": "c-99120-...",
  "company_name": "Apex Engineering Works",
  "zoho_contact_id": "982000000184291",
  "quota_limit": 50,
  "current_holding_count": 34,
  "available_credit": 16,
  "active_deposit_amount": 119000.00,
  "holding_summary": {
    "OXYGEN_INDUSTRIAL": {
      "total_held": 24,
      "within_grace_period": 18,
      "past_grace_billable": 6,
      "current_accrued_rent_inr": 1800.00
    },
    "ARGON": {
      "total_held": 10,
      "within_grace_period": 8,
      "past_grace_billable": 2,
      "current_accrued_rent_inr": 1250.00
    }
  },
  "oldest_held_cylinder": {
    "serial_number": "AR-47-0912",
    "delivery_date": "2026-08-10",
    "days_held": 83,
    "warning_level": "CRITICAL_RECOVERY_REQUIRED"
  }
}
```

---

### 2.5 Inbound Zoho Webhook Receiver
Endpoint receiving events directly from Zoho Books, CRM, or Flow.

```http
POST /api/v1/integrations/zoho/webhook
Content-Type: application/json
X-Zoho-Signature: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

Request:
{
  "event_type": "contact.created",
  "data": {
    "contact_id": "982000000184291",
    "contact_name": "Precision Fabrikators Pvt Ltd",
    "gst_no": "27AAACP1234A1Z5",
    "custom_fields": {
      "cf_cylinder_holding_limit": 100,
      "cf_free_grace_days": 21,
      "cf_rental_slab": "TIER_1_STANDARD"
    }
  }
}

Response (200 OK):
{
  "received": true,
  "action": "CUSTOMER_UPSERTED",
  "internal_customer_id": "c-4491-..."
}
```
