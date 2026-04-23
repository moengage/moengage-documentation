"""Parse every fetched Zendesk article into canonical JSON."""
from __future__ import annotations

import argparse
import json
import sys

from lib.env import ZD_CANONICAL_DIR, ZD_RAW_DIR
from lib.html_parse import parse_zendesk_html
from lib.mapping import load_mapping, select


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--article", help="Only parse this article id")
    args = ap.parse_args()

    entries = select(load_mapping(), args.article)
    ok = fail = 0
    for e in entries:
        raw_path = ZD_RAW_DIR / f"{e.article_id}.json"
        if not raw_path.exists():
            print(f"skip  {e.article_id}: no raw snapshot (run fetch.py first)")
            fail += 1
            continue
        payload = json.loads(raw_path.read_text())
        article = payload.get("article") or {}
        translation = payload.get("translation") or {}
        body = (translation.get("body") if translation else None) or article.get("body") or ""
        if not body:
            print(f"FAIL  {e.article_id}: empty body")
            fail += 1
            continue
        meta = {
            "article_id": e.article_id,
            "article_url": e.article_url,
            "article_title": article.get("title") or translation.get("title") or e.article_title,
            "draft": translation.get("draft", article.get("draft")),
            "updated_at": translation.get("updated_at") or article.get("updated_at"),
        }
        canonical = parse_zendesk_html(body, meta)
        out = ZD_CANONICAL_DIR / f"{e.article_id}.json"
        out.write_text(json.dumps(canonical, indent=2, ensure_ascii=False))
        n_req = len(canonical["request_body"])
        n_resp = len(canonical["response_fields"])
        n_codes = len(canonical["response_codes"])
        print(f"ok    {e.article_id}  endpoint={canonical['endpoint'].get('method','')} {canonical['endpoint'].get('url','')[:60]}  req={n_req} resp={n_resp} codes={n_codes}")
        ok += 1

    print(f"\nparsed {ok}/{ok+fail}")


if __name__ == "__main__":
    sys.exit(main() or 0)
