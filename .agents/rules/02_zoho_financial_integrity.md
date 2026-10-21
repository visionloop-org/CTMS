# Rule: Zoho Financial & Accounting Integrity

## Invariants for Financial Synchronization with Zoho

1. **Mandatory Idempotency Keys:**
   - Every mutating request to Zoho Books (Delivery Challans, Invoices, Customer Payments, Credit Notes) and Zoho Inventory (Transfer Orders) MUST pass an `Idempotency-Key` HTTP header.
   - Idempotency key format:
     ```text
     ctms_{entity_type}_{entity_id}_{version_or_hash}
     Example: ctms_dc_2026_008129_v1
     ```
   - Before firing an API call, the gateway must check Redis/PostgreSQL to verify if the idempotency key was previously dispatched.

2. **Multi-Ownership Billing Isolation (COC vs POC):**
   - **Company-Owned Cylinders (COC):** Subject to security deposits, contract grace days, and progressive rental slabs.
   - **Party-Owned / Customer-Owned Cylinders (POC):**
     - **NEVER** bill cylinder holding charges or rental fees on POC cylinders.
     - Line items for POC deliveries must only bill for gas volume refilled, never container rent.
     - POC cylinders must be validated to ensure they return strictly to the original customer.

3. **Rate-Limit Preservation (Max 80 req/min):**
   - Zoho Books enforces a 100 requests/minute rate limit per organization.
   - The integration gateway must enforce a token-bucket rate limiter capped at **80 requests/minute**.
   - If an HTTP `429 Rate Limit Exceeded` is received, the worker queue must pause for the duration indicated in the `Retry-After` header before retrying.

4. **Asynchronous Isolation:**
   - User-facing REST APIs and Android sync endpoints must NEVER block waiting on external Zoho HTTP calls.
   - All events must commit to the local PostgreSQL database, then enqueue into BullMQ / Redis for background dispatch.

5. **Zoho Document Semantic Mapping (The Triad Invariant):**
   - **Sales Orders (`salesorders`):** Map strictly to **CYLINDER IN** (customer refill demand, inward intake of empties, and POC cylinders arriving at the plant for refilling).
   - **Tax Invoices (`invoices`):** Map strictly to **CYLINDER OUT** (commercial sale of filled gas consumables and outward cylinder deliveries to customer premises).
   - **Stock Delivery Challans (`deliverychallans`):** Map strictly to **CYLINDER ON SECURITY OR RENT** (returnable container asset custody under GST Rule 55 / refundable security deposits / rental loan agreements).

