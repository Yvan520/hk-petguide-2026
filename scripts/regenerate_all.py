#!/usr/bin/env python3
"""Regenerate ALL calendar topics with the new natural prompt.
Usage: python3 scripts/regenerate_all.py
Requires env vars: API_KEY, API_BASE_URL, MODEL_NAME
"""

import json, os, sys, subprocess, time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CALENDAR_PATH = BASE_DIR / "scripts" / "content_calendar.json"

def main():
    with open(CALENDAR_PATH, "r", encoding="utf-8") as f:
        topics = json.load(f)

    success = 0
    fail = 0
    for i, topic in enumerate(topics):
        slug = topic["slug"]
        print(f"\n{'='*50}")
        print(f"[{i+1}/{len(topics)}] {slug} — {topic['title']}")

        result = subprocess.run(
            [sys.executable, "scripts/generate_article.py",
             "--force", "--topic-slug", slug],
            cwd=BASE_DIR,
            capture_output=True, text=True, timeout=300
        )
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                print(f"  {line}")
        if result.stderr:
            for line in result.stderr.strip().split('\n')[-3:]:
                if line.strip():
                    print(f"  ! {line}")
        if result.returncode == 0:
            success += 1
        else:
            fail += 1
            print(f"  FAILED (exit {result.returncode})")
        time.sleep(2)

    print(f"\n{'='*50}")
    print(f"Done: {success} success, {fail} failed of {len(topics)} total")
    return 0 if fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
