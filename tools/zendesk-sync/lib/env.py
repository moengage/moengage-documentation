"""Environment loading and shared paths."""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]

ENV_FILE = ROOT / ".env.local"
if load_dotenv is not None and ENV_FILE.exists():
    load_dotenv(ENV_FILE)


def require(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise SystemExit(
            f"Missing required env var {name}. "
            f"Copy {ROOT}/.env.local.example to .env.local and fill it in."
        )
    return val


SNAPSHOT_DIR = ROOT / "snapshots"
ZD_RAW_DIR = SNAPSHOT_DIR / "zendesk" / "raw"
ZD_CANONICAL_DIR = SNAPSHOT_DIR / "zendesk" / "canonical"
OA_CANONICAL_DIR = SNAPSHOT_DIR / "openapi" / "canonical"
REPORTS_DIR = ROOT / "reports"
MAPPING_FILE = ROOT / "mapping.yaml"

for d in (ZD_RAW_DIR, ZD_CANONICAL_DIR, OA_CANONICAL_DIR, REPORTS_DIR):
    d.mkdir(parents=True, exist_ok=True)
