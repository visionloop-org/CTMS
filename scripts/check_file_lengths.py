#!/usr/bin/env python3
"""
File Length Linter for CTMS.
Enforces the non-negotiable rule: No file may exceed 1000 lines of code/text.
Uses targeted directory scanning for instant zero-FUSE-latency execution.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_ALLOWED_LINES = 1000

CHECK_DIRS = [
    PROJECT_ROOT,
    os.path.join(PROJECT_ROOT, "docs"),
    os.path.join(PROJECT_ROOT, "design-guide"),
    os.path.join(PROJECT_ROOT, "scripts"),
    os.path.join(PROJECT_ROOT, ".agents"),
    os.path.join(PROJECT_ROOT, ".agents", "agents"),
    os.path.join(PROJECT_ROOT, ".agents", "rules"),
    os.path.join(PROJECT_ROOT, ".agents", "skills"),
    os.path.join(PROJECT_ROOT, ".agents", "skills", "zoho-sync-engine"),
    os.path.join(PROJECT_ROOT, ".agents", "skills", "android-device-testing"),
    os.path.join(PROJECT_ROOT, ".agents", "skills", "peso-safety-engine"),
    os.path.join(PROJECT_ROOT, ".agents", "skills", "rental-billing-engine"),
    os.path.join(PROJECT_ROOT, ".agents", "skills", "mcp-gateway-engine"),
    os.path.join(PROJECT_ROOT, ".agents", "skills", "database-event-ledger"),
    os.path.join(PROJECT_ROOT, "backend"),
    os.path.join(PROJECT_ROOT, "backend", "src"),
    os.path.join(PROJECT_ROOT, "backend", "src", "api"),
    os.path.join(PROJECT_ROOT, "backend", "src", "database"),
    os.path.join(PROJECT_ROOT, "backend", "src", "database", "migrations"),
    os.path.join(PROJECT_ROOT, "backend", "src", "modules"),
    os.path.join(PROJECT_ROOT, "backend", "src", "modules", "safety"),
    os.path.join(PROJECT_ROOT, "backend", "src", "modules", "lifecycle"),
    os.path.join(PROJECT_ROOT, "backend", "src", "modules", "rental"),
    os.path.join(PROJECT_ROOT, "backend", "src", "integrations"),
    os.path.join(PROJECT_ROOT, "backend", "src", "integrations", "zoho"),
    os.path.join(PROJECT_ROOT, "backend", "src", "mcp"),
    os.path.join(PROJECT_ROOT, "backend", "tests"),
    os.path.join(PROJECT_ROOT, "android"),
    os.path.join(PROJECT_ROOT, "android", "app"),
    os.path.join(PROJECT_ROOT, "android", "app", "src", "main"),
    os.path.join(PROJECT_ROOT, "android", "app", "src", "main", "java", "com", "ctms", "app"),
    os.path.join(PROJECT_ROOT, "android", "app", "src", "main", "java", "com", "ctms", "app", "presentation"),
    os.path.join(PROJECT_ROOT, "android", "app", "src", "main", "java", "com", "ctms", "app", "data", "local"),
    os.path.join(PROJECT_ROOT, "android", "app", "src", "main", "java", "com", "ctms", "app", "data", "local", "entity"),
    os.path.join(PROJECT_ROOT, "android", "app", "src", "main", "java", "com", "ctms", "app", "data", "local", "dao"),
]

def check_lengths():
    violations = []
    total_files_checked = 0
    longest_file = (0, "")
    seen_files = set()

    for d in CHECK_DIRS:
        if not os.path.isdir(d):
            continue
        try:
            with os.scandir(d) as entries:
                for entry in entries:
                    if not entry.is_file():
                        continue
                    name = entry.name
                    # Skip hidden, binary, or compiled files
                    if name.startswith(".") or name.endswith((".pyc", ".png", ".jpg", ".webp", ".jar", ".zip", ".json")):
                        continue

                    file_path = entry.path
                    if file_path in seen_files:
                        continue
                    seen_files.add(file_path)

                    rel_path = os.path.relpath(file_path, PROJECT_ROOT)
                    total_files_checked += 1

                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            line_count = sum(1 for _ in f)

                        if line_count > longest_file[0]:
                            longest_file = (line_count, rel_path)

                        if line_count > MAX_ALLOWED_LINES:
                            violations.append((rel_path, line_count))
                    except Exception:
                        pass
        except Exception:
            pass

    print(f"[*] Audited {total_files_checked} project files for line-count compliance.", flush=True)
    print(f"[*] Longest file: {longest_file[1]} ({longest_file[0]} lines). Limit: {MAX_ALLOWED_LINES} lines.", flush=True)

    if violations:
        print(f"\n[!] VIOLATION: {len(violations)} files exceed {MAX_ALLOWED_LINES} lines:", flush=True)
        for rel_path, line_count in sorted(violations, key=lambda x: x[1], reverse=True):
            print(f"  - {rel_path}: {line_count} lines (> {MAX_ALLOWED_LINES})", flush=True)
        sys.exit(1)
    else:
        print(f"[+] SUCCESS: All {total_files_checked} files are strictly within the {MAX_ALLOWED_LINES}-line limit!", flush=True)
        sys.exit(0)

if __name__ == "__main__":
    check_lengths()
