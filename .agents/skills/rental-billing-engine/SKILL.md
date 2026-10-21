---
name: rental-billing-engine
description: Guides development, mathematical verification, and billing simulation for the CTMS automated holding charge engine, progressive rental slabs, POC exemption, and Zoho Books invoice generation.
---

# Rental & Holding Calculation Engine Runbook

## Overview
This skill provides developer runbooks and testing fixtures for the **CTMS Automated Rental Engine**.

### Invariant: Prime Rule #3
> **Party-Owned Cylinders (POC) must NEVER be charged rental or holding fees. Company-Owned Cylinders (COC) are subject to rental slabs only after the customer's agreed grace period expires.**

---

## 1. Rental Math & Progressive Slabs

### 1.1 Holding Days Calculation
- **Clock Start:** Timestamp of confirmed customer delivery (recorded on `delivery_challans`).
- **Clock Stop:** Timestamp of empty cylinder pickup scan (recorded on `electronic_cylinder_receipts`).
- **Formula:** `holding_days = CEIL((pickup_time - delivery_time) / 86400)`

### 1.2 Multi-Tier Slab Logic
Customers are assigned a contract slab tier (e.g., Standard Tier 1):

| Tier Days Range | Rate (INR / Cylinder / Day) | Description |
| :--- | :--- | :--- |
| Days 1 to 15 | ₹0.00 | **Contract Grace Period** |
| Days 16 to 30 | ₹10.00 | Base holding fee |
| Days 31 to 60 | ₹25.00 | Penalty holding fee |
| Days 61+ | ₹50.00 | High-shrinkage deterrent fee |

### 1.3 Example Calculation
A customer holds 10 COC cylinders for 40 days:
- Days 1 to 15 (15 days): $10 \times 15 \times ₹0 = ₹0$
- Days 16 to 30 (15 days): $10 \times 15 \times ₹10 = ₹1,500$
- Days 31 to 40 (10 days): $10 \times 10 \times ₹25 = ₹2,500$
- **Total Holding Fee:** $₹1,500 + ₹2,500 = ₹4,000$ (+ 18% GST = ₹4,720).

---

## 2. In-App Finance Approval & Zoho Books Sync

1. **Midnight Cron Run (Celery Beat):** Iterates through active `CUSTOMER_HELD` cylinders and updates daily holding accruals.
2. **Monthly Billing Cycle:** On the 1st of each month, compiles unbilled holding charges into a draft rental batch.
3. **Finance Dashboard Review:** Finance controller inspects the batch, applies dispute waivers if needed, and clicks **"Approve & Push to Zoho Books"**.
4. **Zoho Books Invoice Generation:** An itemized Tax Invoice is pushed to Zoho Books with line-item cylinder serial lists and an `Idempotency-Key` (e.g. `rent_inv_2026_10_cust9912_v1`).
