# Data Models & Schema Design
## Relational Schema, Entities, Enums & Audit Ledger Specifications

---

## 1. Entity Relationship Overview

The CTMS database is designed on PostgreSQL 16+ with high normalization for core entities, combined with an immutable append-only event-ledger for every physical scan and transaction.

```
+--------------------+        +--------------------+        +--------------------+
|     Customers      | 1    * |     Agreements     | 1    * |    Rental Slabs    |
| (linked to Zoho)   +--------+   (Terms & Quotas) +--------+ (Progressive Rates)|
+---------+----------+        +--------------------+        +--------------------+
          | 1
          |
          | *
+---------+----------+        +--------------------+        +--------------------+
|  Delivery Challans | 1    * |   Challan Items    | *    1 |     Cylinders      |
|     (e-DC / ECR)   +--------+ (Delivered/Returned+--------+   (Master Asset)   |
+---------+----------+        +--------------------+        +---------+----------+
          | *                                                         | 1
          |                                                           |
          | 1                                                         | *
+---------+----------+        +--------------------+        +---------+----------+
|       Trips        |        |  Filling Batches   | 1    * |   Cylinder Events  |
|  (Truck Manifests) |        |   (PESO / Purity)  +--------+  (Immutable Scan   |
+--------------------+        +--------------------+        |      Ledger)       |
                                                            +--------------------+
```

---

## 2. Core Tables & DDL Definitions

### 2.1 Enums & Types
```sql
CREATE TYPE cylinder_ownership AS ENUM ('COC', 'POC', 'VOC'); -- Company Owned, Party/Customer Owned, Vendor Owned
CREATE TYPE cylinder_status AS ENUM (
    'PLANT_EMPTY',
    'UNDER_INSPECTION',
    'QUARANTINED_DAMAGED',
    'FILLING',
    'PLANT_FILLED',
    'IN_TRANSIT_OUTWARD',
    'CUSTOMER_HELD',
    'IN_TRANSIT_INWARD',
    'MAINTENANCE_TESTING',
    'SCRAPPED'
);
CREATE TYPE gas_type AS ENUM (
    'OXYGEN_MEDICAL',
    'OXYGEN_INDUSTRIAL',
    'NITROGEN_COMMERCIAL',
    'NITROGEN_UHP',
    'ARGON',
    'CO2',
    'DISSOLVED_ACETYLENE',
    'HELIUM',
    'HYDROGEN',
    'LPG_COMMERCIAL',
    'SPECIALTY_GAS_MIXTURE'
);
CREATE TYPE location_type AS ENUM ('PLANT', 'DEPOT', 'TRUCK', 'CUSTOMER_SITE', 'TESTING_FACILITY');
CREATE TYPE transaction_type AS ENUM ('DELIVERY_FILLED', 'PICKUP_EMPTY', 'TRANSFER_TRUCK', 'INWARD_GATE', 'OUTWARD_GATE');
CREATE TYPE sync_status AS ENUM ('PENDING', 'PROCESSING', 'SYNCED', 'FAILED', 'PERMANENTLY_REJECTED');
```

---

### 2.2 Cylinder Master (`cylinders`)
```sql
CREATE TABLE cylinders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    serial_number VARCHAR(64) NOT NULL UNIQUE,          -- Stamped metal serial number
    collar_code VARCHAR(64),                             -- Painted/punched collar identification
    qr_code_uid VARCHAR(128) UNIQUE,                    -- Encoded data matrix/QR hash
    rfid_epc_uid VARCHAR(128) UNIQUE,                   -- UHF RFID 96-bit/128-bit EPC
    bundle_id UUID REFERENCES bundles(id),              -- Grouped quad/pallet ID (optional)
    
    ownership cylinder_ownership NOT NULL DEFAULT 'COC',
    owner_customer_id UUID REFERENCES customers(id),    -- If POC (Party Owned), links to owner
    owner_vendor_id UUID REFERENCES vendors(id),        -- If VOC (Vendor Owned), links to supplier
    
    current_gas_type gas_type NOT NULL,
    water_capacity_litres NUMERIC(6, 2) NOT NULL,       -- e.g., 46.7, 47.0, 50.0, 10.0
    working_pressure_bar NUMERIC(6, 2) NOT NULL,        -- e.g., 150, 200, 300
    stamped_tare_weight_kg NUMERIC(6, 2) NOT NULL,      -- Stamped empty tare weight
    current_tare_weight_kg NUMERIC(6, 2),               -- Last measured tare weight
    
    status cylinder_status NOT NULL DEFAULT 'PLANT_EMPTY',
    current_location_type location_type NOT NULL DEFAULT 'PLANT',
    current_location_id UUID NOT NULL,                  -- Foreign key to plants/trucks/customers
    
    -- PESO / Statutory Compliance
    manufacturer_name VARCHAR(128),
    manufacturing_date DATE NOT NULL,
    specification_standard VARCHAR(64) DEFAULT 'IS 7285',-- IS 7285, DOT-3AA, ISO 9809
    last_hydro_test_date DATE NOT NULL,
    hydro_test_due_date DATE NOT NULL,                  -- Computed trigger for filling lock
    hydro_test_station_id UUID REFERENCES test_stations(id),
    hydro_test_cert_number VARCHAR(128),
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cylinders_serial ON cylinders(serial_number);
CREATE INDEX idx_cylinders_qr ON cylinders(qr_code_uid);
CREATE INDEX idx_cylinders_rfid ON cylinders(rfid_epc_uid);
CREATE INDEX idx_cylinders_status ON cylinders(status);
CREATE INDEX idx_cylinders_due_date ON cylinders(hydro_test_due_date);
CREATE INDEX idx_cylinders_location ON cylinders(current_location_type, current_location_id);
```

---

### 2.3 Bundles, Quads & Pallets (`bundles`)
```sql
CREATE TABLE bundles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bundle_code VARCHAR(64) NOT NULL UNIQUE,            -- e.g. "QUAD-OX-16-01"
    bundle_type VARCHAR(32) NOT NULL,                   -- 'QUAD_16', 'QUAD_24', 'PALLET_12'
    qr_code_uid VARCHAR(128) UNIQUE,
    rfid_epc_uid VARCHAR(128) UNIQUE,
    total_cylinder_capacity INT NOT NULL,
    manifold_working_pressure_bar NUMERIC(6, 2),
    current_location_id UUID NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 2.4 Customers & Contract Terms (`customers` & `rental_slabs`)
```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    zoho_contact_id VARCHAR(64) UNIQUE,                 -- Link to Zoho Books & CRM Contact ID
    company_name VARCHAR(255) NOT NULL,
    trade_name VARCHAR(255),
    gstin VARCHAR(32),
    contact_person VARCHAR(128),
    phone VARCHAR(32) NOT NULL,
    email VARCHAR(128),
    billing_address TEXT,
    shipping_address TEXT,
    gps_coordinates POINT,                              -- Delivery geofence coordinate
    
    -- Commercial Rules
    cylinder_credit_limit INT NOT NULL DEFAULT 50,      -- Maximum company cylinders allowed
    free_grace_days INT NOT NULL DEFAULT 15,            -- Standard rent-free window
    rental_billing_cycle VARCHAR(32) DEFAULT 'MONTHLY', -- MONTHLY, FORTNIGHTLY, TRANSACTIONAL
    is_poc_authorized BOOLEAN DEFAULT FALSE,            -- Permitted to refill party cylinders
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE rental_slabs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    gas_type gas_type NOT NULL,
    from_day INT NOT NULL,                              -- e.g., Day 16
    to_day INT,                                         -- e.g., Day 30 (NULL = Infinity)
    daily_rate_inr NUMERIC(10, 2) NOT NULL,             -- e.g., 10.00
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_rental_slabs_lookup ON rental_slabs(customer_id, gas_type, from_day);
```

---

### 2.5 Security Deposits Ledger (`security_deposits`)
```sql
CREATE TABLE security_deposits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    zoho_payment_id VARCHAR(64),                        -- Payment / Advance ID in Zoho Books
    receipt_number VARCHAR(64) UNIQUE NOT NULL,
    cylinder_type gas_type NOT NULL,
    quantity_covered INT NOT NULL,
    unit_deposit_amount NUMERIC(10, 2) NOT NULL,
    total_deposit_amount NUMERIC(12, 2) NOT NULL,
    refunded_amount NUMERIC(12, 2) DEFAULT 0.00,
    adjusted_against_rent NUMERIC(12, 2) DEFAULT 0.00,
    active_balance NUMERIC(12, 2) NOT NULL,
    status VARCHAR(32) DEFAULT 'ACTIVE',                -- 'ACTIVE', 'REFUNDED', 'FORFEITED_LOST_CYLINDER'
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 2.6 Filling Batches (`filling_batches`)
```sql
CREATE TABLE filling_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_number VARCHAR(64) NOT NULL UNIQUE,           -- e.g. "BAT-20261101-OX01"
    plant_id UUID NOT NULL REFERENCES plants(id),
    gas_type gas_type NOT NULL,
    target_pressure_bar NUMERIC(6, 2) NOT NULL,
    actual_pressure_bar NUMERIC(6, 2) NOT NULL,
    purity_percentage NUMERIC(6, 3) NOT NULL,           -- e.g. 99.995%
    purity_test_method VARCHAR(64),
    operator_user_id UUID NOT NULL,
    qa_signoff_user_id UUID,
    lab_report_pdf_url TEXT,
    cylinder_count INT NOT NULL DEFAULT 0,
    status VARCHAR(32) DEFAULT 'COMPLETED',             -- 'IN_PROGRESS', 'COMPLETED', 'REJECTED'
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ
);
```

---

### 2.7 Trips, Manifests & Gate-Passes (`trips`)
```sql
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_number VARCHAR(64) NOT NULL UNIQUE,            -- e.g. "TRIP-20261101-09"
    vehicle_registration_number VARCHAR(32) NOT NULL,
    driver_user_id UUID NOT NULL REFERENCES users(id),
    source_plant_id UUID NOT NULL REFERENCES plants(id),
    eway_bill_number VARCHAR(64),
    
    total_outward_filled INT NOT NULL DEFAULT 0,
    total_delivered_filled INT NOT NULL DEFAULT 0,
    total_returned_empty INT NOT NULL DEFAULT 0,
    total_inward_empty_verified INT NOT NULL DEFAULT 0,
    unaccounted_discrepancy INT NOT NULL DEFAULT 0,
    
    start_odometer NUMERIC(10, 1),
    end_odometer NUMERIC(10, 1),
    status VARCHAR(32) DEFAULT 'PLANNED',               -- 'PLANNED', 'DISPATCHED', 'COMPLETED', 'AUDITED'
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 2.8 Delivery Challans & Transactions (`delivery_challans` & `challan_items`)
```sql
CREATE TABLE delivery_challans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    challan_number VARCHAR(64) NOT NULL UNIQUE,         -- "DC-2026-008129"
    trip_id UUID REFERENCES trips(id),
    customer_id UUID NOT NULL REFERENCES customers(id),
    challan_type transaction_type NOT NULL,             -- 'DELIVERY_FILLED' or 'PICKUP_EMPTY'
    
    -- Proof of Delivery Telemetry
    signature_image_url TEXT,
    receiver_name VARCHAR(128),
    receiver_phone VARCHAR(32),
    otp_verified BOOLEAN DEFAULT FALSE,
    delivery_latitude NUMERIC(10, 7),
    delivery_longitude NUMERIC(10, 7),
    delivery_timestamp TIMESTAMPTZ NOT NULL,
    
    -- Financial Sync (Zoho Document Triad)
    zoho_salesorder_id VARCHAR(64),                     -- Cylinder IN (Customer refill demand / empty returns)
    zoho_invoice_id VARCHAR(64),                        -- Cylinder OUT (Filled cylinder dispatches & gas sales)
    zoho_delivery_challan_id VARCHAR(64),               -- Cylinder ON SECURITY OR RENT (Returnable asset custody under GST Rule 55)
    zoho_sync_status sync_status DEFAULT 'PENDING',
    
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE challan_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    challan_id UUID NOT NULL REFERENCES delivery_challans(id) ON DELETE CASCADE,
    cylinder_id UUID NOT NULL REFERENCES cylinders(id),
    batch_id UUID REFERENCES filling_batches(id),
    gas_type gas_type NOT NULL,
    item_condition VARCHAR(32) DEFAULT 'INTACT',        -- 'INTACT', 'DAMAGED_VALVE', 'NECK_LEAK', 'PAINT_DEFECT'
    condition_photo_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_challan_items_lookup ON challan_items(challan_id, cylinder_id);
```

---

### 2.9 Immutable Cylinder Scan & Movement Ledger (`cylinder_events`)
*This table tracks every state transition, scan, and movement over the cylinder's 30+ year lifespan.*
```sql
CREATE TABLE cylinder_events (
    id BIGSERIAL PRIMARY KEY,
    cylinder_id UUID NOT NULL REFERENCES cylinders(id),
    event_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_type VARCHAR(64) NOT NULL,                    -- 'GATE_OUTWARD', 'DELIVERED', 'PICKED_UP', 'FILLED', etc.
    from_status cylinder_status,
    to_status cylinder_status NOT NULL,
    from_location_id UUID,
    to_location_id UUID NOT NULL,
    
    actor_user_id UUID REFERENCES users(id),
    scan_device_id VARCHAR(64),                         -- Phone UUID, RFID Gun Serial
    geo_point POINT,
    
    reference_trip_id UUID REFERENCES trips(id),
    reference_challan_id UUID REFERENCES delivery_challans(id),
    reference_batch_id UUID REFERENCES filling_batches(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_events_cylinder_time ON cylinder_events(cylinder_id, event_timestamp DESC);
```

---

### 2.10 Zoho Synchronization Outbox (`zoho_sync_outbox`)
```sql
CREATE TABLE zoho_sync_outbox (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type VARCHAR(64) NOT NULL,                -- 'INVOICE', 'DELIVERY_CHALLAN', 'CUSTOMER', 'DEPOSIT'
    aggregate_id UUID NOT NULL,
    zoho_target_app VARCHAR(32) NOT NULL,               -- 'BOOKS', 'INVENTORY', 'CRM', 'SIGN'
    payload JSONB NOT NULL,
    idempotency_key VARCHAR(128) UNIQUE NOT NULL,
    status sync_status DEFAULT 'PENDING',
    retry_count INT DEFAULT 0,
    last_error TEXT,
    next_retry_at TIMESTAMPTZ,
    synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_sync_outbox_queue ON zoho_sync_outbox(status, next_retry_at);
```
