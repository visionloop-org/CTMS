# API Keys & Model Context Protocol (MCP) Governance Rule

## Context
Applies to all external API interactions, authentication middleware, and AI agent integrations via the Model Context Protocol.

---

## 1. Cryptographic Key Invariants
1. **Never Store Raw Keys:** Raw API keys (`ctms_live_...`) must never be saved to the database or written to server logs. Store strictly the SHA-256 hash in `tenant_api_keys.key_hash`.
2. **Explicit Scopes Required:** Every third-party endpoint invocation must verify the API key holds the necessary scope (e.g., `has_scope('dispatch:write')`). Unscoped requests must return HTTP `403 FORBIDDEN`.
3. **Tenant RLS Enforcement:** The API key middleware must extract `tenant_id` and inject it into the active database session to enforce Row-Level Security (RLS). No external request may query across tenant boundaries.

---

## 2. Model Context Protocol (MCP) Invariants
1. **PESO Safety Guardrails:** MCP tools (such as `verify_peso_safety`) must strictly enforce the PESO hydro-testing interlock. AI agents cannot bypass safety rejections.
2. **Immutable Audit Logging:** When an AI agent performs an operational action via MCP (e.g., triggering a Zoho Books sync), the action must log `actor_user_id = 'ai-agent:<agent_id>'` in `cylinder_events` or `audit_logs`.
3. **Structured Error Handling:** All MCP tool errors must return machine-readable JSON error objects containing `error_code`, `message`, and `recovery_action`.
