-- CTMS Initial PostgreSQL Relational Schema
-- Conforms to docs/04_DATA_MODELS_AND_SCHEMA_DESIGN.md and docs/12_API_KEYS_AND_MCP_SERVER_SPECIFICATION.md

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enums
DO $$ BEGIN
    CREATE TYPE cylinder_ownership AS ENUM ('COC', 'POC', 'VOC');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
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
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
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
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE location_type AS ENUM ('PLANT', 'DEPOT', 'TRUCK', 'CUSTOMER_SITE', 'TESTING_FACILITY');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE transaction_type AS ENUM ('DELIVERY_FILLED', 'PICKUP_EMPTY', 'TRANSFER_TRUCK', 'INWARD_GATE', 'OUTWARD_GATE');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE sync_status AS ENUM ('PENDING', 'PROCESSING', 'SYNCED', 'FAILED', 'PERMANENTLY_REJECTED');
EXCEPTION WHEN duplicate_object THEN null; END $$;

-- 1. Multi-tenant isolation table
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(64) UNIQUE NOT NULL,
    zoho_organization_id VARCHAR(64),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Plants & Refilling Facilities
CREATE TABLE IF NOT EXISTS plants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    code VARCHAR(32) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    peso_license_number VARCHAR(128) NOT NULL,
    peso_license_expiry DATE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Users & Operators
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    username VARCHAR(128) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(32),
    role VARCHAR(64) NOT NULL, -- SUPER_ADMIN, PLANT_MANAGER, FILLING_OPERATOR, DRIVER, FINANCE
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Authorized Hydro Testing Stations
CREATE TABLE IF NOT EXISTS test_stations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    peso_approval_number VARCHAR(128) NOT NULL,
    location TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 5. Vendors (Suppliers / Third-party fleets)
CREATE TABLE IF NOT EXISTS vendors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    zoho_vendor_id VARCHAR(64) UNIQUE,
    contact_phone VARCHAR(32),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 6. Customers & Commercial Rules
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    zoho_contact_id VARCHAR(64) UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    trade_name VARCHAR(255),
    gstin VARCHAR(32),
    contact_person VARCHAR(128),
    phone VARCHAR(32) NOT NULL,
    email VARCHAR(128),
    billing_address TEXT,
    shipping_address TEXT,
    gps_latitude NUMERIC(10, 7),
    gps_longitude NUMERIC(10, 7),
    cylinder_credit_limit INT NOT NULL DEFAULT 50,
    free_grace_days INT NOT NULL DEFAULT 15,
    rental_billing_cycle VARCHAR(32) DEFAULT 'MONTHLY',
    is_poc_authorized BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Progressive Rental Slabs
CREATE TABLE IF NOT EXISTS rental_slabs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    gas_type gas_type NOT NULL,
    from_day INT NOT NULL,
    to_day INT, -- NULL = Infinity
    daily_rate_inr NUMERIC(10, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_rental_slabs_lookup ON rental_slabs(customer_id, gas_type, from_day);

-- 8. Bundles, Quads & Pallets
CREATE TABLE IF NOT EXISTS bundles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    bundle_code VARCHAR(64) NOT NULL UNIQUE,
    bundle_type VARCHAR(32) NOT NULL,
    qr_code_uid VARCHAR(128) UNIQUE,
    rfid_epc_uid VARCHAR(128) UNIQUE,
    total_cylinder_capacity INT NOT NULL,
    manifold_working_pressure_bar NUMERIC(6, 2),
    current_location_id UUID NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. Cylinder Master
CREATE TABLE IF NOT EXISTS cylinders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    serial_number VARCHAR(64) NOT NULL UNIQUE,
    collar_code VARCHAR(64),
    qr_code_uid VARCHAR(128) UNIQUE,
    rfid_epc_uid VARCHAR(128) UNIQUE,
    bundle_id UUID REFERENCES bundles(id),
    
    ownership cylinder_ownership NOT NULL DEFAULT 'COC',
    owner_customer_id UUID REFERENCES customers(id),
    owner_vendor_id UUID REFERENCES vendors(id),
    
    current_gas_type gas_type NOT NULL,
    water_capacity_litres NUMERIC(6, 2) NOT NULL,
    working_pressure_bar NUMERIC(6, 2) NOT NULL,
    stamped_tare_weight_kg NUMERIC(6, 2) NOT NULL,
    current_tare_weight_kg NUMERIC(6, 2),
    
    status cylinder_status NOT NULL DEFAULT 'PLANT_EMPTY',
    current_location_type location_type NOT NULL DEFAULT 'PLANT',
    current_location_id UUID NOT NULL,
    
    manufacturer_name VARCHAR(128),
    manufacturing_date DATE NOT NULL,
    specification_standard VARCHAR(64) DEFAULT 'IS 7285',
    last_hydro_test_date DATE NOT NULL,
    hydro_test_due_date DATE NOT NULL,
    hydro_test_station_id UUID REFERENCES test_stations(id),
    hydro_test_cert_number VARCHAR(128),
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cylinders_serial ON cylinders(serial_number);
CREATE INDEX IF NOT EXISTS idx_cylinders_qr ON cylinders(qr_code_uid);
CREATE INDEX IF NOT EXISTS idx_cylinders_rfid ON cylinders(rfid_epc_uid);
CREATE INDEX IF NOT EXISTS idx_cylinders_status ON cylinders(status);
CREATE INDEX IF NOT EXISTS idx_cylinders_due_date ON cylinders(hydro_test_due_date);
CREATE INDEX IF NOT EXISTS idx_cylinders_location ON cylinders(current_location_type, current_location_id);

-- 10. Security Deposits Ledger
CREATE TABLE IF NOT EXISTS security_deposits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id),
    zoho_payment_id VARCHAR(64),
    receipt_number VARCHAR(64) UNIQUE NOT NULL,
    cylinder_type gas_type NOT NULL,
    quantity_covered INT NOT NULL,
    unit_deposit_amount NUMERIC(10, 2) NOT NULL,
    total_deposit_amount NUMERIC(12, 2) NOT NULL,
    refunded_amount NUMERIC(12, 2) DEFAULT 0.00,
    adjusted_against_rent NUMERIC(12, 2) DEFAULT 0.00,
    active_balance NUMERIC(12, 2) NOT NULL,
    status VARCHAR(32) DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 11. Filling Batches
CREATE TABLE IF NOT EXISTS filling_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    batch_number VARCHAR(64) NOT NULL UNIQUE,
    plant_id UUID NOT NULL REFERENCES plants(id),
    gas_type gas_type NOT NULL,
    target_pressure_bar NUMERIC(6, 2) NOT NULL,
    actual_pressure_bar NUMERIC(6, 2) NOT NULL,
    purity_percentage NUMERIC(6, 3) NOT NULL,
    purity_test_method VARCHAR(64),
    operator_user_id UUID NOT NULL REFERENCES users(id),
    qa_signoff_user_id UUID REFERENCES users(id),
    lab_report_pdf_url TEXT,
    cylinder_count INT NOT NULL DEFAULT 0,
    status VARCHAR(32) DEFAULT 'COMPLETED',
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ
);

-- 12. Trips, Manifests & Gate-Passes
CREATE TABLE IF NOT EXISTS trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    trip_number VARCHAR(64) NOT NULL UNIQUE,
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
    status VARCHAR(32) DEFAULT 'PLANNED',
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 13. Delivery Challans & Transactions
CREATE TABLE IF NOT EXISTS delivery_challans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    challan_number VARCHAR(64) NOT NULL UNIQUE,
    trip_id UUID REFERENCES trips(id),
    customer_id UUID NOT NULL REFERENCES customers(id),
    challan_type transaction_type NOT NULL,
    
    signature_image_url TEXT,
    receiver_name VARCHAR(128),
    receiver_phone VARCHAR(32),
    otp_verified BOOLEAN DEFAULT FALSE,
    delivery_latitude NUMERIC(10, 7),
    delivery_longitude NUMERIC(10, 7),
    delivery_timestamp TIMESTAMPTZ NOT NULL,
    
    zoho_salesorder_id VARCHAR(64),
    zoho_invoice_id VARCHAR(64),
    zoho_delivery_challan_id VARCHAR(64),
    zoho_sync_status sync_status DEFAULT 'PENDING',
    
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 14. Challan Items
CREATE TABLE IF NOT EXISTS challan_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    challan_id UUID NOT NULL REFERENCES delivery_challans(id) ON DELETE CASCADE,
    cylinder_id UUID NOT NULL REFERENCES cylinders(id),
    batch_id UUID REFERENCES filling_batches(id),
    gas_type gas_type NOT NULL,
    item_condition VARCHAR(32) DEFAULT 'INTACT',
    condition_photo_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_challan_items_lookup ON challan_items(challan_id, cylinder_id);

-- 15. Immutable Cylinder Scan Ledger
CREATE TABLE IF NOT EXISTS cylinder_events (
    id BIGSERIAL,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    cylinder_id UUID NOT NULL REFERENCES cylinders(id),
    event_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_type VARCHAR(64) NOT NULL,
    from_status cylinder_status,
    to_status cylinder_status NOT NULL,
    from_location_id UUID,
    to_location_id UUID NOT NULL,
    
    actor_user_id UUID REFERENCES users(id),
    scan_device_id VARCHAR(64),
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    
    reference_trip_id UUID REFERENCES trips(id),
    reference_challan_id UUID REFERENCES delivery_challans(id),
    reference_batch_id UUID REFERENCES filling_batches(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id, event_timestamp)
);
CREATE INDEX IF NOT EXISTS idx_events_cylinder_time ON cylinder_events(cylinder_id, event_timestamp DESC);

-- 16. Zoho Synchronization Outbox
CREATE TABLE IF NOT EXISTS zoho_sync_outbox (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    aggregate_type VARCHAR(64) NOT NULL,
    aggregate_id UUID NOT NULL,
    zoho_target_app VARCHAR(32) NOT NULL,
    payload JSONB NOT NULL,
    idempotency_key VARCHAR(128) UNIQUE NOT NULL,
    status sync_status DEFAULT 'PENDING',
    retry_count INT DEFAULT 0,
    last_error TEXT,
    next_retry_at TIMESTAMPTZ,
    synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sync_outbox_queue ON zoho_sync_outbox(status, next_retry_at);

-- 17. External API Key Gateway & Tenant Tokens
CREATE TABLE IF NOT EXISTS tenant_api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    key_name VARCHAR(128) NOT NULL,
    key_prefix VARCHAR(16) NOT NULL,
    key_hash VARCHAR(64) NOT NULL UNIQUE,
    allowed_scopes TEXT[] NOT NULL DEFAULT '{"cylinders:read"}',
    cidr_whitelist TEXT[] DEFAULT '{}',
    rate_limit_rpm INT NOT NULL DEFAULT 300,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    expires_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by_user_id UUID REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON tenant_api_keys(key_hash);

-- 18. API Key Audit & Usage Metrics
CREATE TABLE IF NOT EXISTS tenant_api_key_usage (
    id BIGSERIAL PRIMARY KEY,
    api_key_id UUID NOT NULL REFERENCES tenant_api_keys(id) ON DELETE CASCADE,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(16) NOT NULL,
    status_code INT NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    latency_ms NUMERIC(8, 2) NOT NULL,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_api_usage_key_time ON tenant_api_key_usage(api_key_id, requested_at DESC);
