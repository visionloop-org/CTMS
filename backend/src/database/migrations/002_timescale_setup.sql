-- TimescaleDB Hypertable Setup & Event Retention Policies
-- Conforms to docs/04_DATA_MODELS_AND_SCHEMA_DESIGN.md and .agents/skills/database-event-ledger/SKILL.md

-- 1. Enable TimescaleDB extension if available in PostgreSQL
DO $$ BEGIN
    CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'TimescaleDB extension not installed or permission denied, skipping hypertable configuration';
END $$;

-- 2. Convert cylinder_events to Hypertable partitioned by week (7 days)
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        PERFORM create_hypertable(
            'cylinder_events',
            'event_timestamp',
            chunk_time_interval => INTERVAL '7 days',
            if_not_exists => TRUE
        );

        -- 3. Enable compression on cylinder_events for chunks older than 30 days
        ALTER TABLE cylinder_events SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'tenant_id, cylinder_id',
            timescaledb.compress_orderby = 'event_timestamp DESC'
        );

        PERFORM add_compression_policy('cylinder_events', INTERVAL '30 days', if_not_exists => TRUE);
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Skipping TimescaleDB hypertable policy: %', SQLERRM;
END $$;
