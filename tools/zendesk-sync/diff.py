"""Compare Zendesk vs OpenAPI canonical snapshots and write Markdown reports."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from lib.diff import diff_canonicals
from lib.env import OA_CANONICAL_DIR, REPORTS_DIR, ZD_CANONICAL_DIR
from lib.mapping import load_mapping, select


SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _truncate(v, n=400):
    s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
    if s is None:
        return ""
    if len(s) > n:
        return s[:n] + " …(truncated)"
    return s


def _render_value(v):
    if v is None:
        return "_(none)_"
    if isinstance(v, str):
        s = v.strip()
        if "\n" in s or len(s) > 80:
            return "\n```\n" + _truncate(s, 1200) + "\n```\n"
        return f"`{s}`"
    if isinstance(v, (dict, list)):
        return "\n```json\n" + _truncate(json.dumps(v, indent=2, ensure_ascii=False), 1600) + "\n```\n"
    return f"`{v}`"


def render_report(entry, zd_canonical, oa_canonical, diffs) -> str:
    lines: list[str] = []
    lines.append(f"# Sync report: {entry.article_title}")
    lines.append("")
    lines.append(f"- **Article**: [{entry.article_id}]({entry.article_url})")
    lines.append(f"- **YAML**: `{entry.yaml_path}`")
    if entry.needs_review:
        lines.append(f"- **needs_review**: placement of this article in the YAML was guessed; please confirm.")
    src = zd_canonical.get("source", {})
    lines.append(f"- **Zendesk last updated**: {src.get('updated_at', '?')}  (draft={src.get('draft')})")
    op_src = oa_canonical.get("source", {})
    if op_src.get("missing"):
        lines.append(f"- **OpenAPI match**: NOT FOUND in {entry.yaml_path} for title '{entry.operation_title}'. Every Zendesk field is listed below as missing.")
    else:
        lines.append(f"- **OpenAPI operation**: `{op_src.get('method')} {op_src.get('path')}`  (operationId: `{op_src.get('operation_id')}`)")
    lines.append("")

    if not diffs:
        lines.append("## No differences detected.")
        lines.append("")
        lines.append("Canonical Zendesk and OpenAPI representations match on structure, descriptions, response codes, rate limit, and samples.")
        return "\n".join(lines)

    counts = Counter((d["kind"], d["severity"]) for d in diffs)
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total diffs: **{len(diffs)}**")
    for kind in ("structural", "textual", "sample"):
        for sev in ("high", "medium", "low"):
            n = counts.get((kind, sev), 0)
            if n:
                lines.append(f"  - {kind} / {sev}: {n}")
    lines.append("")

    diffs_sorted = sorted(diffs, key=lambda d: (
        {"structural": 0, "textual": 1, "sample": 2}[d["kind"]],
        SEVERITY_ORDER.get(d["severity"], 9),
        d["path"],
    ))

    for kind in ("structural", "textual", "sample"):
        kind_diffs = [d for d in diffs_sorted if d["kind"] == kind]
        if not kind_diffs:
            continue
        lines.append(f"## {kind.capitalize()} diffs")
        lines.append("")
        for d in kind_diffs:
            lines.append(f"### `{d['path']}` — {d['severity']}")
            lines.append("")
            lines.append(f"_{d['note']}_")
            lines.append("")
            lines.append(f"**Zendesk**: {_render_value(d['zendesk'])}")
            lines.append("")
            lines.append(f"**OpenAPI**: {_render_value(d['openapi'])}")
            lines.append("")

    return "\n".join(lines) + "\n"


def write_index(rows: list[dict]):
    rows.sort(key=lambda r: (r["yaml_path"], r["article_title"]))
    # Group by yaml_path for PR planning.
    lines = [
        "# Zendesk → OpenAPI sync — index",
        "",
        "One PR will be opened per YAML. The counts below summarise the diff reports.",
        "",
        "| YAML | Article | Status | Diffs | High | Draft |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| `{r['yaml_path']}` | [{r['article_title']}](./{r['article_id']}.md) | {r.get('status','ok')} | {r['total']} | {r['high']} | {r['draft']} |"
        )
    # Per-YAML totals
    from collections import defaultdict
    totals: dict[str, dict] = defaultdict(lambda: {"articles": 0, "diffs": 0, "high": 0, "skip": 0, "multi": 0})
    for r in rows:
        t = totals[r["yaml_path"]]
        t["articles"] += 1
        t["diffs"] += r["total"]
        t["high"] += r["high"]
        if str(r.get("status", "")).startswith("skip"):
            t["skip"] += 1
        if r.get("status") == "multi-op":
            t["multi"] += 1
    lines.append("")
    lines.append("## Per-YAML roll-up (one PR each)")
    lines.append("")
    lines.append("| YAML | Articles | Multi-op | Skipped | Total diffs | High |")
    lines.append("|---|---|---|---|---|---|")
    for yaml_path in sorted(totals.keys()):
        t = totals[yaml_path]
        lines.append(f"| `{yaml_path}` | {t['articles']} | {t['multi']} | {t['skip']} | {t['diffs']} | {t['high']} |")
    (REPORTS_DIR / "INDEX.md").write_text("\n".join(lines) + "\n")


def _render_multi_report(entry, zd, oa_index) -> str:
    """For articles with multiple operations, generate per-op diffs and stitch."""
    lines: list[str] = [f"# Sync report: {entry.article_title} (multi-operation)"]
    lines.append("")
    lines.append(f"- **Article**: [{entry.article_id}]({entry.article_url})")
    lines.append(f"- **YAML**: `{entry.yaml_path}`")
    src = zd.get("source", {})
    lines.append(f"- **Zendesk last updated**: {src.get('updated_at', '?')}  (draft={src.get('draft')})")
    ops = oa_index["source"].get("operations", [])
    lines.append(f"- **Operations matched**: {len([o for o in ops if o['matched']])}/{len(ops)}")
    lines.append("")
    total_diffs = 0
    total_high = 0
    for op in ops:
        slug = op["slug"]
        title = op["title"]
        oa_path = OA_CANONICAL_DIR / f"{entry.article_id}__{slug}.json"
        if not oa_path.exists():
            lines.append(f"## {title}")
            lines.append("")
            lines.append(f"_No canonical snapshot for this op._")
            continue
        oa = json.loads(oa_path.read_text())
        lines.append(f"## Operation: {title}")
        lines.append("")
        if oa.get("source", {}).get("missing"):
            lines.append(f"**No OpenAPI match found** — {oa['source'].get('missing_reason', '')}")
            lines.append("")
            total_diffs += 1
            total_high += 1
            continue
        lines.append(f"- OpenAPI: `{oa['source'].get('method')} {oa['source'].get('path')}` (operationId: `{oa['source'].get('operation_id')}`)")
        lines.append("")
        # The Zendesk side is shared across all ops in the article; flag this so
        # reviewers know we're comparing the whole article body to each op.
        lines.append(f"> Note: the Zendesk article documents multiple operations; the fields below are compared against the full article. Cross-referenced context may cause some extra diffs — focus on structural gaps.")
        lines.append("")
        diffs = diff_canonicals(zd, oa)
        total_diffs += len(diffs)
        total_high += sum(1 for d in diffs if d["severity"] == "high")
        if not diffs:
            lines.append("_No differences detected for this op._")
            lines.append("")
            continue
        for d in sorted(diffs, key=lambda x: (SEVERITY_ORDER.get(x["severity"], 9), x["path"])):
            lines.append(f"- `{d['path']}` ({d['severity']}, {d['kind']}) — {d['note']}")
        lines.append("")
    return "\n".join(lines) + "\n", total_diffs, total_high


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--article", help="Only diff this article id")
    args = ap.parse_args()

    entries = select(load_mapping(), args.article)
    summary: list[dict] = []
    for e in entries:
        zd_path = ZD_CANONICAL_DIR / f"{e.article_id}.json"
        oa_path = OA_CANONICAL_DIR / f"{e.article_id}.json"
        if not zd_path.exists() or not oa_path.exists():
            print(f"skip  {e.article_id}: missing canonical snapshots")
            continue
        zd = json.loads(zd_path.read_text())
        oa = json.loads(oa_path.read_text())

        if e.skip_diff:
            report = (
                f"# Sync report: {e.article_title}\n\n"
                f"- **Article**: [{e.article_id}]({e.article_url})\n"
                f"- **YAML**: `{e.yaml_path}`\n"
                f"- **Status**: SKIPPED — {e.skip_reason}\n\n"
                f"This article is not processed by the automated diff because it is not a 1:1 API operation.\n"
                f"Zendesk canonical snapshot is available at `snapshots/zendesk/canonical/{e.article_id}.json` "
                f"for manual review.\n"
            )
            (REPORTS_DIR / f"{e.article_id}.md").write_text(report)
            summary.append({
                "article_id": e.article_id,
                "article_title": e.article_title,
                "yaml_path": e.yaml_path,
                "total": 0, "high": 0,
                "draft": zd.get("source", {}).get("draft"),
                "status": f"skip: {e.skip_reason}",
            })
            print(f"skip  {e.article_id}  ({e.skip_reason})")
            continue

        if oa.get("source", {}).get("kind") == "openapi-multi":
            report, n_diffs, n_high = _render_multi_report(e, zd, oa)
            (REPORTS_DIR / f"{e.article_id}.md").write_text(report)
            summary.append({
                "article_id": e.article_id,
                "article_title": e.article_title,
                "yaml_path": e.yaml_path,
                "total": n_diffs, "high": n_high,
                "draft": zd.get("source", {}).get("draft"),
                "status": "multi-op",
            })
            print(f"multi {e.article_id}  diffs={n_diffs}")
            continue

        if oa.get("source", {}).get("missing"):
            diffs = [{
                "kind": "structural", "severity": "high",
                "path": "operation",
                "zendesk": {"title": zd.get("title"), "endpoint": zd.get("endpoint")},
                "openapi": None,
                "note": f"No matching operation in {e.yaml_path} for '{e.operation_override or e.operation_title}'. "
                        "Either the operation is missing from this YAML or the mapping needs an operation_override.",
            }]
        else:
            diffs = diff_canonicals(zd, oa)

        report = render_report(e, zd, oa, diffs)
        (REPORTS_DIR / f"{e.article_id}.md").write_text(report)

        counts = Counter((d["kind"], d["severity"]) for d in diffs)
        summary.append({
            "article_id": e.article_id,
            "article_title": e.article_title,
            "yaml_path": e.yaml_path,
            "total": len(diffs),
            "high": sum(v for k, v in counts.items() if k[1] == "high"),
            "draft": zd.get("source", {}).get("draft"),
            "status": "ok",
        })
        print(f"ok    {e.article_id}  diffs={len(diffs)}")

    if not args.article:
        write_index(summary)
        print(f"\nwrote {len(summary)} reports, INDEX.md")


if __name__ == "__main__":
    sys.exit(main() or 0)
