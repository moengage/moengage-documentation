"""Fetch Zendesk article translations for every mapped article.

Uses the translations endpoint so draft (saved-but-unpublished) edits are
captured. Raw JSON is saved to snapshots/zendesk/raw/<article_id>.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

import requests

from lib.env import ZD_RAW_DIR, require
from lib.mapping import load_mapping, select


def build_session() -> requests.Session:
    subdomain = require("ZENDESK_SUBDOMAIN").strip().rstrip("/")
    user = require("ZENDESK_USERNAME").strip()
    token = require("ZENDESK_API_TOKEN").strip()
    s = requests.Session()
    s.auth = (f"{user}/token", token)
    s.headers.update({"Accept": "application/json"})
    s.base = f"https://{subdomain}/api/v2/help_center"
    return s


def _get_with_retry(s: requests.Session, url: str, attempts: int = 6) -> requests.Response:
    for i in range(attempts):
        r = s.get(url, timeout=30, allow_redirects=True)
        if r.status_code == 429:
            retry_after = int(r.headers.get("Retry-After", "10"))
            wait = max(retry_after, 2 ** i)
            print(f"  rate-limited on {url.rsplit('/', 1)[-1]}, sleeping {wait}s (attempt {i+1}/{attempts})")
            time.sleep(wait)
            continue
        if r.status_code >= 500:
            time.sleep(2 ** i)
            continue
        return r
    return r


def fetch_article(s: requests.Session, article_id: str) -> dict[str, Any]:
    article_resp = _get_with_retry(s, f"{s.base}/articles/{article_id}.json")
    article_resp.raise_for_status()
    article = article_resp.json().get("article", {})

    translation = None
    for locale in ("en-us", "en"):
        r = _get_with_retry(s, f"{s.base}/articles/{article_id}/translations/{locale}.json")
        if r.status_code == 200:
            translation = r.json().get("translation")
            break
    if translation is None:
        tr_list = _get_with_retry(s, f"{s.base}/articles/{article_id}/translations.json").json()
        translation = (tr_list.get("translations") or [None])[0]

    return {"article": article, "translation": translation}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--article", help="Only fetch this article id")
    ap.add_argument("--force", action="store_true", help="Refetch even if snapshot exists")
    args = ap.parse_args()

    s = build_session()
    entries = select(load_mapping(), args.article)
    if not entries:
        print(f"No mapping entries selected.")
        return 2

    ok = 0
    for e in entries:
        out = ZD_RAW_DIR / f"{e.article_id}.json"
        if out.exists() and not args.force:
            print(f"skip  {e.article_id} (snapshot exists)")
            ok += 1
            continue
        try:
            payload = fetch_article(s, e.article_id)
        except requests.HTTPError as ex:
            print(f"FAIL  {e.article_id} {e.article_title}: {ex}")
            continue
        tr = payload.get("translation") or {}
        draft = tr.get("draft", payload.get("article", {}).get("draft"))
        updated = tr.get("updated_at") or payload.get("article", {}).get("updated_at")
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
        print(f"ok    {e.article_id} {e.article_title}  draft={draft}  updated={updated}")
        ok += 1
        time.sleep(0.6)

    print(f"\nfetched {ok}/{len(entries)}")


if __name__ == "__main__":
    sys.exit(main() or 0)
