# Statutory PESO Regulatory Reporting Engine & B2B Customer Portal
## Gas Cylinders Rules (Rule 35) Compliance, Template Exporter & Enterprise Customer Experience

---

## 1. Statutory PESO Regulatory Reporting Engine

High-pressure gas cylinder testing stations and filling facilities operating in India must strictly adhere to statutory compliance mandated by the **Petroleum and Explosives Safety Organization (PESO)** under **Rule 35 of the Gas Cylinders Rules, 2016**.

CTMS incorporates an automated compliance engine that records all physical testing measurements, executes deterministic pass/fail safety calculations, and compiles tamper-proof **PESO Form III** and **PESO Form IV** inspection dossiers.

```
                    +--------------------------------------------+
                    |    Hydrostatic Stretch Test Station Data   |
                    |    (Burette water displacement levels)     |
                    +--------------------------------------------+
                                          |
                                          v
                    +--------------------------------------------+
                    |        PESO Rule 35 Math Validation        |
                    |  - Perm Expansion / Total Exp <= 10.0%     |
                    |  - Tare Weight Loss <= 5.0% (Wall Thinning)|
                    +--------------------------------------------+
                           /                             \
                PASS     /                                 \ FAIL
                        v                                   v
        +-------------------------------+       +-------------------------------+
        |  Update cylinder record:      |       |  Permanently CONDEMN cylinder:|
        |  - hydro_test_due_date + 5 yrs|       |  - to_status: CONDEMNED_PESO  |
        |  - Stamp approval cert #      |       |  - Append to scrap ledger     |
        +-------------------------------+       +-------------------------------+
                        |                                   |
                        +-----------------+-----------------+
                                          v
                    +--------------------------------------------+
                    |       Template-Driven Report Exporter      |
                    |  - Maps structured data to PESO layouts    |
                    |  - Cryptographically signed PDF for PESO   |
                    |  - Excel register for statutory inspections|
                    +--------------------------------------------+
```

---

### 1.1 PESO Rule 35 Mathematical Validation Invariants

Every cylinder subjected to periodic hydraulic stretch testing must pass two mandatory physical tests before re-qualification:

#### 1. Permanent Volumetric Expansion Limit:
$$\text{Expansion Ratio} = \left( \frac{\text{Permanent Expansion (cc)}}{\text{Total Volumetric Expansion (cc)}} \right) \times 100$$
- **Statutory Threshold:** The permanent expansion must **never exceed 10.0%** of the total expansion under the prescribed test pressure (e.g. 250 bar or $1.5\times$ working pressure).
- **If $\text{Expansion Ratio} > 10.0\%$:** The cylinder has undergone irreversible plastic deformation. It must be **immediately condemned** and rendered unserviceable as per IS 5844 / Gas Cylinders Rules 2016.

#### 2. Tare Weight Loss Threshold (Internal & External Wall Thinning):
$$\text{Tare Loss Percentage} = \left( \frac{\text{Original Tare Weight (kg)} - \text{Current Clean Tare Weight (kg)}}{\text{Original Tare Weight (kg)}} \right) \times 100$$
- **Statutory Threshold:** The tare weight loss must **not exceed 5.0%** of the original manufacturer tare stamped on the cylinder shoulder.
- **If $\text{Tare Loss} > 5.0\%$:** The cylinder shell has suffered significant corrosion or wall thinning. It fails statutory safety standards and must be **immediately condemned**.

---

### 1.2 Template-Driven Reporting Engine & Schema

> [!TIP]
> **Regulatory Architecture Principle:** Never hardcode statutory government report table coordinates or text layouts into backend business logic. PESO circulars and state inspectors periodically modify form columns.
> CTMS stores raw hydrostatic test metrics in structured relational tables and renders certificates using a **Template-Driven Engine** (JSON schema mapping DB fields to PDF/Excel layout configurations).

```sql
CREATE TABLE hydro_test_records (
    test_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cylinder_id UUID NOT NULL REFERENCES cylinders(cylinder_id),
    station_license_no VARCHAR(64) NOT NULL,              -- e.g. "G.3(1)2021-EXP/TEST-042"
    competent_person_user_id UUID NOT NULL REFERENCES users(user_id),
    test_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Pressure Parameters
    working_pressure_bar NUMERIC(6,2) NOT NULL,          -- e.g. 150.00 bar
    test_pressure_bar NUMERIC(6,2) NOT NULL,             -- e.g. 250.00 bar (1.5x to 1.66x)
    hold_duration_seconds INTEGER NOT NULL DEFAULT 30,   -- Mandatory 30-second dwell under pressure
    
    -- Weight Parameters
    original_tare_weight_kg NUMERIC(6,3) NOT NULL,
    current_tare_weight_kg NUMERIC(6,3) NOT NULL,
    tare_weight_loss_pct NUMERIC(5,2) GENERATED ALWAYS AS (
        ROUND(((original_tare_weight_kg - current_tare_weight_kg) / original_tare_weight_kg) * 100.0, 2)
    ) STORED,
    
    -- Volumetric Water Jacket Burette Readings
    water_temperature_celsius NUMERIC(4,1) NOT NULL DEFAULT 28.0,
    water_capacity_litres NUMERIC(6,2) NOT NULL,          -- e.g. 46.7 L
    total_expansion_cc NUMERIC(6,2) NOT NULL,
    permanent_expansion_cc NUMERIC(6,2) NOT NULL,
    expansion_ratio_pct NUMERIC(5,2) GENERATED ALWAYS AS (
        CASE WHEN total_expansion_cc > 0 THEN
            ROUND((permanent_expansion_cc / total_expansion_cc) * 100.0, 2)
        ELSE 0.0 END
    ) STORED,
    
    -- Visual & Ultrasonic Inspections
    internal_inspection_passed BOOLEAN NOT NULL DEFAULT true,
    external_inspection_passed BOOLEAN NOT NULL DEFAULT true,
    neck_threads_ok BOOLEAN NOT NULL DEFAULT true,
    
    -- Deterministic Statutory Outcome
    test_passed BOOLEAN NOT NULL,
    rejection_reason VARCHAR(255),
    
    -- Post-Test Certification & Immutability
    next_test_due_date DATE,
    hydro_cert_number VARCHAR(100) UNIQUE,
    is_locked_immutable BOOLEAN NOT NULL DEFAULT false,   -- Locks record once signed
    approved_by_user_id UUID REFERENCES users(user_id),
    digital_signature_hash VARCHAR(256),                  -- SHA-256 HMAC of test row signed by inspector
    signed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Audit index for statutory inspection queries
CREATE INDEX idx_hydro_test_cyl_date ON hydro_test_records (cylinder_id, test_date DESC);
CREATE INDEX idx_hydro_test_cert ON hydro_test_records (hydro_cert_number);
```

---

### 1.3 PESO Form III Specification (Certificate of Hydrostatic Testing)

**Form III** is the official statutory test certificate issued to cylinder owners, industrial customers, and PESO circle offices.

```text
========================================================================================================
                                     GOVERNMENT OF INDIA
                        PETROLEUM AND EXPLOSIVES SAFETY ORGANIZATION (PESO)
                                            FORM III
                                    [See Rule 35, Sub-rule (1)]
            CERTIFICATE OF PERIODICAL EXAMINATION AND TESTING OF HIGH PRESSURE GAS CYLINDERS
========================================================================================================
Test Station: Apex Industrial Gas Testing Lab, Plot 14 MIDC, Pune - 411028
PESO License No: G.3(1)2021-EXP/TEST-042                     License Validity: 31-DEC-2028
Certificate No:  PESO-TEST-2026-004812                       Test Date:        21-OCT-2026
--------------------------------------------------------------------------------------------------------
1. Name & Address of Owner:       Sunrise Multispeciality Hospital, Senapati Bapat Marg, Pune - 411016
2. Type of Gas / Service:         Medical Oxygen (O2)
3. Manufacturing Standard / Spec: IS 7285 (Part 2) / ISO 9809-1
4. Cylinder Serial / Stamped No:  OX-47-0912                 CTMS Tag ID:     TAG-99412
5. Manufacturer Name:             Bharat Petroleum Equipment Ltd (2018)
6. Water Capacity (Litres):       46.7 Litres                Working Pressure: 150.0 kg/cm2 (bar)
--------------------------------------------------------------------------------------------------------
                                   RECORD OF HYDROSTATIC STRETCH TEST
--------------------------------------------------------------------------------------------------------
(a) Original Tare Weight (kg):    52.500 kg
(b) Current Clean Tare Weight:    51.800 kg
(c) Tare Weight Loss Percentage:  1.33 %                     [Statutory Limit: Max 5.00%]  -> PASSED
(d) Hydraulic Test Pressure:      250.0 kg/cm2 (bar)         [Dwell Time: 30 seconds]
(e) Total Volumetric Expansion:   310.0 cc
(f) Permanent Expansion:          12.0 cc
(g) Perm / Total Expansion Ratio: 3.87 %                     [Statutory Limit: Max 10.0%] -> PASSED
(h) Internal & External Condition: Free from pitting, denting, or lamellar defects. Threads sound.
--------------------------------------------------------------------------------------------------------
                                          FINAL DETERMINATION
--------------------------------------------------------------------------------------------------------
RESULT: PASSED STATUTORY HYDROSTATIC STRETCH TEST AS PER PESO RULE 35.
The shoulder has been hard-stamped with the Inspection Mark "[APEX]" and testing date "10/26".
NEXT MANDATORY RE-TESTING DUE DATE: 20-OCT-2031 (Valid for 5 Years).

Certified By:
Competent Person: Er. R. S. Deshmukh (PESO Approved Inspector ID: PESO/EXP/MH/8841)
Digital Signature Hash: 7b89d4e5f2a18c991e...3df84c20e10
Verification QR Code: https://portal.apexgases.com/verify-cert/PESO-TEST-2026-004812
========================================================================================================
```

---

## 2. B2B Customer Self-Service Portal

Large institutional consumers (hospitals, engineering fabrication yards, semiconductor plants, and pharmaceutical laboratories) require live visibility into their cylinder balances, automated statutory document retrieval, and instant refill ordering.

```
       +-------------------------------------------------------------+
       |             CTMS B2B Customer Portal (Next.js)             |
       |             https://portal.apexgases.com                    |
       +-------------------------------------------------------------+
                                      |
         +----------------------------+----------------------------+
         |                            |                            |
         v                            v                            v
+------------------+         +------------------+         +------------------+
| Holding & Rental |         | Instant Orders & |         | Statutory NABH & |
| Dashboard        |         | Empty Dispatch   |         | Compliance Vault |
+------------------+         +------------------+         +------------------+
| - Live balances  |         | - Emergency O2   |         | - Form III Certs |
| - POC vs COC     |         | - Empty pickup   |         | - Gas Purity IP  |
| - Days before fee|         | - SLA Timer      |         | - Expiring URLs  |
| - CSV Export     |         | - WhatsApp alert |         | - QR Verify Hash |
+------------------+         +------------------+         +------------------+
```

---

### 2.1 Multi-Tenant Isolation: PostgreSQL Row-Level Security (RLS)

To guarantee that competitive manufacturing plants or neighboring hospitals cannot inspect each other's cylinder fleets, CTMS enforces database-level tenant isolation via **PostgreSQL Row-Level Security**:

```sql
-- Enable Row Level Security on Customer Facing Tables
ALTER TABLE delivery_challans ENABLE ROW LEVEL SECURITY;
ALTER TABLE hydro_test_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE gas_purity_certificates ENABLE ROW LEVEL SECURITY;

-- Policy: Customers can only query rows belonging to their authenticated session
CREATE POLICY customer_portal_dc_isolation ON delivery_challans
    FOR SELECT
    USING (customer_id = NULLIF(current_setting('app.current_customer_id', true), '')::UUID);

CREATE POLICY customer_portal_purity_isolation ON gas_purity_certificates
    FOR SELECT
    USING (customer_id = NULLIF(current_setting('app.current_customer_id', true), '')::UUID);
```

#### Granular Portal RBAC Roles:
1. `PURCHASE_MANAGER`: Full order placement, invoice viewing, rental waiver dispute submission.
2. `STORE_KEEPER`: Empty pickup dispatch, driver delivery acknowledgment, receiving inspections.
3. `CLINICAL_AUDITOR` (Hospital): Read-only access to statutory certificates, batch purity reports, and NABH dossiers.

---

### 2.2 Security, MFA & Signed Expiring URLs

1. **Authentication Flow:**
   - Passwordless magic link + mandatory **SMS/WhatsApp Time-based OTP** (MFA).
   - Session tokens (JWT) carry claim `tenant_customer_id` and have an idle TTL of 30 minutes.
2. **Document Retrieval via Signed Expiring URLs:**
   - Certificate PDFs are stored in S3/MinIO private buckets.
   - The portal never exposes raw storage buckets; it generates HMAC-signed **Presigned URLs valid for 15 minutes**:
     `https://storage.apexgases.com/certs/PESO-TEST-2026-004812.pdf?Expires=1761148800&Signature=...`
3. **Immutable Download Audit Log:**
   - Every document download and order submission appends to `portal_audit_log` recording `customer_user_id`, `ip_address`, `document_type`, and `timestamp`.

---

### 2.3 Live Cylinder Holding & Rental Ledger

The portal displays an interactive, real-time matrix of cylinders held at the customer's physical premises, with individual countdowns to rent commencement:

```json
{
  "customer_id": "cust_sun_99182",
  "customer_name": "Sunrise Multispeciality Hospital",
  "holding_summary": {
    "total_cylinders_on_site": 84,
    "company_owned_coc": 60,
    "party_owned_poc": 24,
    "rental_accruing_count": 8,
    "estimated_monthly_rental_inr": 2400.00
  },
  "cylinder_holdings": [
    {
      "cylinder_serial": "OX-47-0912",
      "gas_type": "MEDICAL_OXYGEN_IP",
      "ownership": "COC",
      "delivered_date": "2026-10-01",
      "days_on_site": 20,
      "grace_period_days": 15,
      "days_until_rent_starts": 0,
      "billable_days_accrued": 5,
      "current_slab_rate_per_day": 10.00
    },
    {
      "cylinder_serial": "OX-47-1044",
      "gas_type": "MEDICAL_OXYGEN_IP",
      "ownership": "COC",
      "delivered_date": "2026-10-15",
      "days_on_site": 6,
      "grace_period_days": 15,
      "days_until_rent_starts": 9,
      "billable_days_accrued": 0,
      "current_slab_rate_per_day": 0.00
    },
    {
      "cylinder_serial": "N2O-11-209",
      "gas_type": "NITROUS_OXIDE",
      "ownership": "POC",
      "delivered_date": "2026-09-01",
      "days_on_site": 50,
      "grace_period_days": 0,
      "days_until_rent_starts": 999,
      "billable_days_accrued": 0,
      "current_slab_rate_per_day": 0.00,
      "notes": "Party-Owned Cylinder: Rental Exempt"
    }
  ]
}
```

---

### 2.4 Emergency Refill Dispatching with SLA Tracking

When a hospital purchase manager submits an emergency ICU oxygen order:
1. An active **SLA Timer (2 Hours)** starts in the CTMS dispatch queue.
2. An instant **WhatsApp + SMS notification** is dispatched to the plant logistics manager and the on-duty cluster driver.
3. A high-priority **Zoho Sales Order** is created via webhook with priority tag `URGENT_MEDICAL_SLA`.

---

### 2.5 Hospital NABH Compliance Document Vault

Hospital accreditation auditors (NABH / JCI) require immediate verification of medical gas purity. Every certificate generated includes a verification QR code linking to the cylinder UUID and filling batch:

```text
+---------------------------------------------------------------------------------------------------+
| HOSPITAL NABH STATUTORY DOCUMENT VAULT                                                           |
+---------------------------------------------------------------------------------------------------+
| Cylinder Tag ID | Stamped S/N | Gas Spec           | Batch #    | Purity Cert     | Form III Cert |
+-----------------+-------------+--------------------+------------+-----------------+---------------+
| TAG-99412       | OX-47-0912  | Med O2 IP (99.6%)  | B-2610-09  | [ Signed PDF ]  | [ Signed PDF ]|
| TAG-99413       | OX-47-0913  | Med O2 IP (99.7%)  | B-2610-09  | [ Signed PDF ]  | [ Signed PDF ]|
| TAG-88102       | N2O-11-209  | Nitrous Oxide USP  | B-2609-41  | [ Signed PDF ]  | [ Signed PDF ]|
+-----------------+-------------+--------------------+------------+-----------------+---------------+
| [ DOWNLOAD ALL ACTIVE AUDIT CERTIFICATES (ZIP) ] - Instant 1-Click NABH Compliance Pack          |
+---------------------------------------------------------------------------------------------------+
```
