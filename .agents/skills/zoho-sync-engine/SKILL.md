---
name: zoho-sync-engine
description: >-
  Use this skill when developing, testing, or debugging integrations between CTMS
  and Zoho applications (Zoho Books, Zoho Inventory, Zoho CRM, Zoho Analytics, and Zoho Sign).
---

# Zoho Sync Engine Skill

This skill guides the agent in implementing, testing, and mocking the bidirectional synchronization between CTMS and the Zoho Cloud Suite.

## 1. Core Document Triad & Mappings

The Zoho Books integration is anchored on three distinct document types:

1. **Sales Orders (`POST /api/v3/salesorders`): CYLINDER IN**
   - Customer refill requests, inward intake of empty cylinders returning to plant, and Party-Owned Cylinders (POC) received for refilling.
   - Includes custom fields: `cf_cylinder_direction: "CYLINDER_IN"`, `cf_serialized_cylinders_inward`.

2. **Tax Invoices (`POST /api/v3/invoices`): CYLINDER OUT**
   - Commercial sale of consumable gas product ($m^3 / kg$) and outward delivery of filled cylinders to customer premises.
   - Includes custom field: `cf_serialized_cylinders_outward`.

3. **Stock Delivery Challans (`POST /api/v3/deliverychallans`): CYLINDER ON SECURITY OR RENT**
   - Non-sale container asset bailment under GST Rule 55.
   - Used for cylinders issued against refundable Security Deposits or under Rental/Holding agreements.
   - Starts and stops the customer holding days timer for rental calculations.

4. **Monthly Rental Invoicing (`POST /api/v3/invoices`):**
   - Billable cylinder-days calculated from `rental_slabs`.
   - Day-by-day itemized audit PDF attached via `POST /api/v3/invoices/{invoice_id}/attachment`.

5. **Security Deposit Liability Ledger:**
   - Posted under liability account `Cylinder Security Deposits Liability`.

### Zoho Inventory
- Plant and mobile trucks mapped as separate warehouses:
  - `Main Bottling Plant (wh_01)`
  - `Truck MH-04-AB-1234 (wh_truck_09)`
- Moving filled cylinders triggers Transfer Order in Zoho Inventory.

## 2. Idempotency & Reliability Pattern
Every outward API call MUST include a unique idempotency key:
```typescript
const idempotencyKey = `zoho_books_dc_${challan.id}_${challan.version}`;
```
If a network timeout occurs, the agent must check the local `zoho_sync_outbox` table before retrying to prevent duplicate invoice generation.

## 3. Mock Testing Strategy
When running offline or automated integration tests without production Zoho credentials, use the mock server in `scripts/mock_zoho_server.py`:
```bash
python3 scripts/mock_zoho_server.py --port 8089
```
This mock verifies request headers, validates payload schemas, and responds with synthetic Zoho IDs (`zoho_dc_992182`, `zoho_inv_109281`).
