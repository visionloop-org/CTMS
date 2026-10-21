"""
Fast standalone test runner for CTMS backend.
Runs all unit test suites directly with zero overhead and produces detailed reports.
"""

import os
import sys
import time

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def run():
    print("=" * 60)
    print("  CTMS Core Engine Standalone Verification Runner")
    print("=" * 60)
    
    start_time = time.time()
    passed = 0
    failed = 0

    suites = [
        ("PESO Safety Engine (Prime Invariant #1)", "backend.tests.test_peso_safety", [
            "test_hydro_test_overdue_rejected_with_403",
            "test_hydro_test_valid_passes",
            "test_tare_loss_exceeding_5_percent_quarantined",
            "test_gas_type_mismatch_rejected",
        ]),
        ("10-State Lifecycle Machine (Prime Invariant #2)", "backend.tests.test_state_machine", [
            "test_valid_lifecycle_progression",
            "test_illegal_jump_throws_error",
            "test_scrapped_is_terminal",
        ]),
        ("Rental Engine & POC Exemption (Prime Invariant #3)", "backend.tests.test_rental_engine", [
            "test_poc_cylinder_strictly_zero_rental",
            "test_coc_cylinder_progressive_slabs",
            "test_customer_batch_mixed_fleet",
        ]),
        ("API Key Auth & Native MCP Server", "backend.tests.test_api_keys_and_mcp", [
            "test_api_key_authentication_and_scopes",
            "test_mcp_server_tools_and_resources",
        ]),
        ("Zoho Books Idempotency (Prime Invariant #5)", "backend.tests.test_zoho_integration", [
            "test_missing_idempotency_key_raises_error",
            "test_missing_idempotency_key_invoice_raises_error",
        ]),
    ]

    for suite_name, module_name, test_names in suites:
        print(f"\n[SUITE] {suite_name}")
        try:
            mod = __import__(module_name, fromlist=test_names)
        except Exception as e:
            print(f"  FAILED to import {module_name}: {e}")
            failed += len(test_names)
            continue

        for test_name in test_names:
            test_fn = getattr(mod, test_name, None)
            if not test_fn:
                print(f"  [MISSING] {test_name}")
                failed += 1
                continue
            try:
                test_fn()
                print(f"  PASS: {test_name}", flush=True)
                passed += 1
            except Exception as e:
                print(f"  FAIL: {test_name} -> {e}", flush=True)
                failed += 1

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"  RESULTS: {passed} passed, {failed} failed in {elapsed:.3f}s")
    print("=" * 60)
    
    if failed > 0:
        sys.exit(1)
    else:
        print("ALL PRIME INVARIANTS & CORE TESTS PASSED [STATUS: GREEN]")

if __name__ == "__main__":
    run()
