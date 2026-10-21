#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "  CTMS Unified Verification & Proof Runner (AIDD Protocol)"
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

echo "[1/5] Verifying System Specifications & Markdown Integrity..."
test -f "$PROJECT_ROOT/README.md"
test -f "$PROJECT_ROOT/PROJECT_OVERVIEW.md"
test -f "$PROJECT_ROOT/INDEX.md"
test -f "$PROJECT_ROOT/AGENTS.md"
test -f "$PROJECT_ROOT/TASK_QUEUE.md"
test -f "$PROJECT_ROOT/docker-compose.yml"
test -f "$PROJECT_ROOT/.env.example"
test -f "$PROJECT_ROOT/docs/01_SYSTEM_REQUIREMENTS_AND_ARCHITECTURE.md"
test -f "$PROJECT_ROOT/docs/02_CORE_FUNCTIONAL_MODULES.md"
test -f "$PROJECT_ROOT/docs/03_ZOHO_ECOSYSTEM_INTEGRATION_SPEC.md"
test -f "$PROJECT_ROOT/docs/04_DATA_MODELS_AND_SCHEMA_DESIGN.md"
test -f "$PROJECT_ROOT/docs/05_API_SPECIFICATION_AND_OFFLINE_SYNC.md"
test -f "$PROJECT_ROOT/docs/06_IMPLEMENTATION_ROADMAP_AND_MILESTONES.md"
test -f "$PROJECT_ROOT/docs/07_NATIVE_ANDROID_APP_SPECIFICATION.md"
test -f "$PROJECT_ROOT/docs/08_ZOHO_API_INTERACTIONS_AND_PAYLOAD_SPECIFICATION.md"
test -f "$PROJECT_ROOT/docs/09_AI_DRIVEN_DEVELOPMENT_PROTOCOLS_AND_BEST_PRACTICES.md"
test -f "$PROJECT_ROOT/docs/10_DATA_MIGRATION_SECURITY_AND_DISASTER_RECOVERY_PLAN.md"
test -f "$PROJECT_ROOT/docs/11_SYSTEM_UNDERSTANDING_AND_KNOWLEDGE_GRAPH.md"
test -f "$PROJECT_ROOT/docs/12_API_KEYS_AND_MCP_SERVER_SPECIFICATION.md"
test -f "$PROJECT_ROOT/docs/13_HARDWARE_PERIPHERALS_AND_EXCEPTION_PLAYBOOKS.md"
test -f "$PROJECT_ROOT/docs/14_STATUTORY_PESO_REPORTING_AND_CUSTOMER_PORTAL.md"
test -f "$PROJECT_ROOT/docs/15_INFRASTRUCTURE_DOCKER_AND_CI_CD_PIPELINE.md"
test -f "$PROJECT_ROOT/design-guide/README.md"
test -f "$PROJECT_ROOT/design-guide/01_COLOR_SYSTEM_AND_THEMING.md"
test -f "$PROJECT_ROOT/design-guide/02_TYPOGRAPHY_AND_ICONS.md"
test -f "$PROJECT_ROOT/design-guide/03_FOUNDATIONAL_UI_ELEMENTS.md"
test -f "$PROJECT_ROOT/design-guide/04_SPECIALIZED_SCANNER_AND_HARDWARE_ELEMENTS.md"
test -f "$PROJECT_ROOT/design-guide/05_DOMAIN_CYLINDER_AND_CHALLAN_ELEMENTS.md"
test -f "$PROJECT_ROOT/design-guide/06_STATE_AND_INTERACTION_PATTERNS.md"
echo "  -> OK: All 15 specs, docker-compose.yml and 7 design guide modules exist."

echo "[2/5] Running Fast Zero-IO Markdown Link Integrity Audit..."
python3 "$PROJECT_ROOT/scripts/verify_markdown_links.py"

echo "[3/5] Verifying Agent Swarm, Rules & Customizations..."
test -f "$PROJECT_ROOT/.agents/agents/README.md"
test -f "$PROJECT_ROOT/.agents/agents/01_zoho_integration_agent.md"
test -f "$PROJECT_ROOT/.agents/agents/02_android_app_agent.md"
test -f "$PROJECT_ROOT/.agents/agents/03_backend_api_agent.md"
test -f "$PROJECT_ROOT/.agents/agents/04_industrial_design_agent.md"
test -f "$PROJECT_ROOT/.agents/agents/05_interaction_protocol_agent.md"
test -f "$PROJECT_ROOT/.agents/agents/06_database_ledger_agent.md"
test -f "$PROJECT_ROOT/.agents/agents/07_agent_coordinator.md"
test -f "$PROJECT_ROOT/.agents/agents/08_quality_test_agent.md"
test -f "$PROJECT_ROOT/.agents/rules/01_safety_and_compliance.md"
test -f "$PROJECT_ROOT/.agents/rules/02_zoho_financial_integrity.md"
test -f "$PROJECT_ROOT/.agents/rules/03_android_offline_architecture.md"
test -f "$PROJECT_ROOT/.agents/rules/04_code_quality_and_testing.md"
test -f "$PROJECT_ROOT/.agents/rules/05_api_keys_and_ai_mcp.md"
test -f "$PROJECT_ROOT/.agents/rules/agent_workflow.md"
test -f "$PROJECT_ROOT/.agents/skills/zoho-sync-engine/SKILL.md"
test -f "$PROJECT_ROOT/.agents/skills/android-device-testing/SKILL.md"
test -f "$PROJECT_ROOT/.agents/skills/peso-safety-engine/SKILL.md"
test -f "$PROJECT_ROOT/.agents/skills/rental-billing-engine/SKILL.md"
test -f "$PROJECT_ROOT/.agents/skills/mcp-gateway-engine/SKILL.md"
test -f "$PROJECT_ROOT/.agents/skills/database-event-ledger/SKILL.md"
echo "  -> OK: All 8 specialized agents, 6 rules and 6 skills verified."

echo "[4/5] Enforcing Strict File Length Limit (< 1000 lines)..."
python3 "$PROJECT_ROOT/scripts/check_file_lengths.py"

echo "[5/5] Verifying Python Syntax & Generating Proof Artifact..."
python3 -m py_compile "$PROJECT_ROOT/scripts/mock_zoho_server.py"
python3 -m py_compile "$PROJECT_ROOT/scripts/verify_markdown_links.py"
python3 -m py_compile "$PROJECT_ROOT/scripts/check_file_lengths.py"

PROOF_DIR="$PROJECT_ROOT/.agents/proofs"
mkdir -p "$PROOF_DIR"
cat <<EOF > "$PROOF_DIR/latest_verification.json"
{
  "timestamp": "$TIMESTAMP",
  "status": "PASS",
  "verified_specs_count": 15,
  "verified_design_guides_count": 7,
  "verified_agents_count": 8,
  "verified_rules_count": 6,
  "verified_skills_count": 6,
  "markdown_link_integrity": "100%",
  "max_file_length_compliance": "PASS (< 1000 lines)",
  "mock_server_syntax": "VALID"
}
EOF

echo "=========================================================="
echo "  VERIFICATION COMPLETE: ALL GATES PASSED [STATUS: GREEN]"
echo "=========================================================="
