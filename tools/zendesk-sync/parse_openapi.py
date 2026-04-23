"""Parse the mapped OpenAPI operation for every article into canonical JSON.

For single-operation articles we write `<article_id>.json`.
For multi-operation articles (`operation_overrides: [...]`) we write one file
per op as `<article_id>__<slug>.json` and an index `<article_id>.json` that
lists them so `diff.py` can iterate.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

from lib.canonical import empty_canonical
from lib.env import OA_CANONICAL_DIR
from lib.mapping import load_mapping, select
from lib.openapi_parse import parse_openapi_operation


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-") or "op"


def _write_stub(article_id: str, yaml_path: str, title: str, reason: str, slug: str | None = None):
    stub = empty_canonical()
    stub["source"] = {
        "kind": "openapi",
        "article_id": article_id,
        "yaml_path": yaml_path,
        "operation_title": title,
        "missing": True,
        "missing_reason": reason,
    }
    name = f"{article_id}__{slug}.json" if slug else f"{article_id}.json"
    (OA_CANONICAL_DIR / name).write_text(json.dumps(stub, indent=2, ensure_ascii=False))


def _parse_one(e, title: str, slug: str | None = None):
    canonical = parse_openapi_operation(
        e.abs_yaml_path,
        title,
        {
            "article_id": e.article_id,
            "article_url": e.article_url,
            "yaml_path": e.yaml_path,
        },
    )
    if canonical is None:
        _write_stub(e.article_id, e.yaml_path, title, f"no op match for '{title}'", slug)
        return False, title
    name = f"{e.article_id}__{slug}.json" if slug else f"{e.article_id}.json"
    (OA_CANONICAL_DIR / name).write_text(json.dumps(canonical, indent=2, ensure_ascii=False))
    return True, canonical


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--article", help="Only parse this article id")
    args = ap.parse_args()

    entries = select(load_mapping(), args.article)
    ok = miss = skipped = 0
    for e in entries:
        if e.skip_diff:
            print(f"skip  {e.article_id}  {e.article_title}  ({e.skip_reason})")
            skipped += 1
            # Write a stub so diff.py can emit a one-liner report.
            _write_stub(e.article_id, e.yaml_path, e.operation_title, f"skip_diff: {e.skip_reason}")
            continue

        yaml_path = e.abs_yaml_path
        if not yaml_path.exists():
            print(f"FAIL  {e.article_id}: yaml missing at {yaml_path}")
            miss += 1
            continue

        # Handle unparseable YAMLs (e.g. stray tab chars) gracefully.
        try:
            from lib.openapi_parse import load_yaml
            load_yaml(yaml_path)
        except Exception as ex:
            print(f"FAIL  {e.article_id}: cannot parse {e.yaml_path} ({ex.__class__.__name__})")
            _write_stub(e.article_id, e.yaml_path, e.operation_title, f"yaml parse error: {ex}")
            miss += 1
            continue

        # Multi-op article
        if e.operation_overrides:
            ops_written = []
            for op_title in e.operation_overrides:
                slug = _slug(op_title)
                got, val = _parse_one(e, op_title, slug)
                ops_written.append({
                    "slug": slug,
                    "title": op_title,
                    "matched": got,
                    "method": val["endpoint"].get("method") if got else "",
                    "path": val["source"].get("path") if got else "",
                })
                if got:
                    ok += 1
                else:
                    miss += 1
            index = empty_canonical()
            index["source"] = {
                "kind": "openapi-multi",
                "article_id": e.article_id,
                "yaml_path": e.yaml_path,
                "operation_title": e.operation_title,
                "operations": ops_written,
            }
            (OA_CANONICAL_DIR / f"{e.article_id}.json").write_text(
                json.dumps(index, indent=2, ensure_ascii=False)
            )
            print(f"multi {e.article_id}  {len(ops_written)} ops")
            continue

        title = e.operation_override or e.operation_title
        got, val = _parse_one(e, title)
        if got:
            print(f"ok    {e.article_id}  {val['endpoint'].get('method','')} {val['endpoint'].get('url','')[:60]}  req={len(val['request_body'])} resp={len(val['response_fields'])} codes={len(val['response_codes'])}")
            ok += 1
        else:
            print(f"MISS  {e.article_id}  no op match in {e.yaml_path} for '{title}'")
            miss += 1

    total = ok + miss + skipped
    print(f"\nparsed {ok}/{total}  miss={miss}  skipped={skipped}")


if __name__ == "__main__":
    sys.exit(main() or 0)
