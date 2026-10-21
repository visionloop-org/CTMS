---
name: database-event-ledger
description: Runbook for managing TimescaleDB hypertable partitioning, PostgreSQL schema migrations, immutable scan audit queries, and Dgraph knowledge graph traversals in CTMS.
---

# Database, Event Ledger & Knowledge Graph Runbook

## Overview
This skill guides database engineering, TimescaleDB performance tuning, and Dgraph knowledge graph query execution.

### Invariant: Prime Rule #2
> **Every physical scan or status transition MUST append a row to `cylinder_events` containing `cylinder_id`, `event_type`, `to_status`, `to_location_id`, `actor_user_id`, `timestamp`, and `geo_point`. Never update or delete existing history rows in `cylinder_events`.**

---

## 1. TimescaleDB Event Ledger

### 1.1 Hypertable Configuration
```sql
-- Convert standard table to TimescaleDB hypertable partitioned by week
SELECT create_hypertable('cylinder_events', 'timestamp', chunk_time_interval => INTERVAL '7 days');

-- Enable native compression for data older than 30 days
ALTER TABLE cylinder_events SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'tenant_id, cylinder_id',
    timescaledb.compress_orderby = 'timestamp DESC'
);

SELECT add_compression_policy('cylinder_events', INTERVAL '30 days');
```

---

## 2. Knowledge Graph Traversals (Dgraph DQL)

### 2.1 Medical Gas Batch Recall Query
Locates all active customer locations holding cylinders from a contaminated filling batch:

```dql
{
  find_contaminated_cylinders(func: eq(batch_number, "MED-OX-20261021-01")) {
    batch_number
    gas_type
    purity_percentage
    contains_cylinders {
      serial_number
      status
      held_by_customer {
        customer_name
        contact_phone
        gps_coordinates
      }
    }
  }
}
```
