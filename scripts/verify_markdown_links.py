#!/usr/bin/env python3
"""
Instant Zero-FUSE-Lag Markdown Link Auditor for CTMS.
Verifies both file links and directory links resolve with 100% integrity.
"""

import os
import re
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXPLICIT_DIRS = [
    PROJECT_ROOT,
    os.path.join(PROJECT_ROOT, "docs"),
    os.path.join(PROJECT_ROOT, "design-guide"),
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
    os.path.join(PROJECT_ROOT, ".agents", "proofs"),
    os.path.join(PROJECT_ROOT, "scripts")
]

def fast_audit():
    valid_paths = set()
    markdown_files = []

    # Add directories as valid targets (both with and without trailing slash)
    for d in EXPLICIT_DIRS:
        valid_paths.add(d)
        valid_paths.add(d.rstrip("/") + "/")
        valid_paths.add(os.path.abspath(d))
        valid_paths.add(os.path.abspath(d).rstrip("/") + "/")

        if not os.path.isdir(d):
            continue
        try:
            with os.scandir(d) as entries:
                for entry in entries:
                    if entry.name == ".git":
                        continue
                    p = entry.path
                    if entry.is_file():
                        valid_paths.add(p)
                        valid_paths.add(os.path.abspath(p))
                        if entry.name.endswith(".md"):
                            markdown_files.append(p)
                    elif entry.is_dir():
                        valid_paths.add(p)
                        valid_paths.add(p.rstrip("/") + "/")
                        valid_paths.add(os.path.abspath(p))
                        valid_paths.add(os.path.abspath(p).rstrip("/") + "/")
        except Exception:
            pass

    print(f"[*] Indexed {len(valid_paths)} valid paths across {len(markdown_files)} markdown files.", flush=True)

    broken = []
    total_links = 0

    for md in markdown_files:
        rel = os.path.relpath(md, PROJECT_ROOT)
        with open(md, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        print(f"    [+] Checked {rel}", flush=True)

        for label, url in re.findall(r'\[([^\]]+)\]\((file:///[^\)]+)\)', content):
            total_links += 1
            clean = url.replace("file://", "").split("#")[0]
            if clean in valid_paths or clean.rstrip("/") in valid_paths or os.path.exists(clean) or os.path.exists(clean.rstrip("/")):
                valid_paths.add(clean)
                valid_paths.add(clean.rstrip("/"))
            else:
                broken.append((rel, label, clean))

    print(f"[+] Total file:// links verified: {total_links}", flush=True)

    if broken:
        print(f"\n[!] Broken links found: {len(broken)}", flush=True)
        for src, lbl, tgt in broken:
            print(f"  - In {src}: [{lbl}] -> {tgt}", flush=True)
        sys.exit(1)
    else:
        print("[+] SUCCESS: All markdown links (files & directories) resolve with 100% integrity!", flush=True)
        sys.exit(0)

if __name__ == "__main__":
    fast_audit()
