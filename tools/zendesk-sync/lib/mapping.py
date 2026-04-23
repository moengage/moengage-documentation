"""Load mapping.yaml."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import yaml

from .env import MAPPING_FILE, REPO_ROOT


@dataclass
class MappingEntry:
    article_id: str
    article_url: str
    article_title: str
    yaml_path: str           # relative to repo root
    operation_title: str     # the expected summary/title in the YAML
    needs_review: bool = False
    # Optional manual override: a YAML operation summary OR operationId that
    # identifies the operation. Use when the article title does not match the
    # YAML summary.
    operation_override: str | None = None
    # Optional list — for Zendesk articles that document multiple endpoints in
    # one page (e.g. "File Segment API" → create/add/remove/replace).
    operation_overrides: list[str] | None = None
    # Set to true for articles that are not an API endpoint reference at all
    # (feature overviews, glossaries, Streams setup). They are kept in the
    # mapping so we have a complete ledger but are not diffed.
    skip_diff: bool = False
    skip_reason: str | None = None
    path: str | None = None
    method: str | None = None
    operation_id: str | None = None

    @property
    def abs_yaml_path(self):
        return REPO_ROOT / self.yaml_path


def load_mapping() -> list[MappingEntry]:
    if not MAPPING_FILE.exists():
        raise SystemExit(f"mapping.yaml not found at {MAPPING_FILE}")
    with open(MAPPING_FILE) as f:
        data = yaml.safe_load(f) or []
    return [MappingEntry(**row) for row in data]


def select(entries: Iterable[MappingEntry], article_id: str | None):
    if article_id is None:
        return list(entries)
    return [e for e in entries if e.article_id == str(article_id)]
