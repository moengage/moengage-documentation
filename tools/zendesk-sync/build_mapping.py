"""Build mapping.yaml from the CSV and the list of out-of-sync article URLs.

Run once (or whenever the inputs change):

    python build_mapping.py

Inputs:
  - ./inputs/out_of_sync_urls.txt   : one URL per line, the 62 URLs
  - ./inputs/yaml_article_map.csv   : the CSV exported from the planning sheet
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / "inputs"
URLS_FILE = INPUTS / "out_of_sync_urls.txt"
CSV_FILE = INPUTS / "yaml_article_map.csv"
OUT_FILE = ROOT / "mapping.yaml"

# Corrections for CSV yaml-name -> actual file on disk.
YAML_ALIASES = {
    "coupons-list.yaml": "coupons.yaml",
    "cohorts-audience.yaml": "cohort-audience.yaml",
}

# Articles missing from the CSV. Curated by looking at the Zendesk section
# and our local yaml layout. Add here if `build_mapping.py` complains.
MANUAL_ASSIGNMENTS: dict[str, tuple[str, str, bool]] = {
    # article_id: (yaml_file_name, article_title, needs_review)
    # needs_review=True means the CSV did not cover this article and the
    # placement is a best guess that a human should confirm.
    "4404674776724": ("data.yaml", "Overview", False),
    "42053298082708": ("campaigns.yaml", "Global Control Group API", True),
    "43505841794452": ("catalog.yaml", "Get Item Details", False),
}


# Explicit per-article overrides applied after building the base mapping.
# Use these when the Zendesk article title does not match any YAML operation
# summary as-is. Values:
#   operation_override:  single summary/operationId for 1:1 articles
#   operation_overrides: list for articles that cover multiple YAML ops
#   skip_diff:           non-API reference articles (overviews, setup guides)
OVERRIDES: dict[str, dict] = {
    # Campaigns: the YAML has one unified Create/Update/Search Campaign per
    # verb; Zendesk splits them by channel (email/push/sms).
    "27896715162516": {"operation_override": "Create Campaign"},       # Create Email Campaigns
    "38466364097044": {"operation_override": "Create Campaign"},       # Create Push Campaigns
    "27896779501332": {"operation_override": "Update Campaign"},       # Update Email Campaigns
    "38466513599892": {"operation_override": "Update Campaign"},       # Update Push Campaign
    "27896777540756": {"operation_override": "Search Campaigns"},      # Get Email Campaign Details
    "38466670624276": {"operation_override": "Search Campaigns"},      # Get Push Campaign Details
    "40800964029076": {"operation_override": "Search Campaigns"},      # Get SMS Campaign Details

    # Cohort / Audience Sync → Sync Cohort Members
    "4426761481108": {"operation_override": "Sync Cohort Members"},

    # Custom Segments: the Zendesk "Archive and UnArchive…" article covers two
    # YAML ops; "File Segment API" covers four.
    "27877389154068": {"operation_overrides": ["Archive Segment", "Unarchive Segment"]},
    "13277936457748": {"operation_override": "Create Filter Segment"},
    "4405027805844":  {"operation_overrides": [
        "Create File Segment",
        "Add Users to File Segment",
        "Remove Users from File Segment",
        "Replace Users from File Segment",
    ]},

    # Inform API → Send Transactional Alert
    "10699624590868": {"operation_override": "Send Transactional Alert"},

    # Catalog
    "43505841794452": {"operation_override": "Get Items"},

    # Data API
    "4413174104852": {"operation_override": "Track Event"},
    "4628698189588": {"operation_override": "Track App Install"},
    "10990676421908": {"operation_override": "Merge Users"},
    "27513633367572": {"operation_override": "Test Connection API"},
    "4413174113044":  {"operation_override": "Bulk Import Users and Events"},  # Bulk Import
    "31951172951444": {"operation_override": "Import Details"},                 # File Import Status

    # Email / Push / SMS / OSM / Inapp template APIs
    "36398727638932": {"operation_override": "Update User Email Opt-in Preferences"},  # Email Optin
    "15475075894164": {"operation_override": "Get Specific Template"},                  # Get a Specific Email Template
    "15506305637140": {"operation_override": "Get All Templates"},                      # Get all templates
    "4405026835220":  {"operation_override": "Submit a GDPR / CCPA Data Request"},      # GDPR old id
    "43742143072276": {"operation_override": "Submit a GDPR / CCPA Data Request"},      # GDPR new id
    "31256295491348": {"operation_override": "Search In-app Templates"},
    "38536975180564": {"operation_override": "End Broadcast Live Activity"},
    "38536957005076": {"operation_override": "Update Broadcast Live Activity"},
    "28544200636692": {"operation_override": "View Archived Message"},
    "35163337484948": {"operation_override": "Search OSM Templates"},
    "14226294477972": {"operation_override": "Search for Push Templates"},
    "4404548252820":  {"operation_override": "Send Push Notification"},
    "14229094128788": {"operation_override": "Search SMS Templates"},
    "4409329518484":  {"operation_override": "Download Campaign Report"},
    "32895300259732": {"operation_override": "Get Campaign Stats"},
    # 4404674776724 Overview — not an endpoint; skip diff, keep for ledger.
    "4404674776724": {"skip_diff": True, "skip_reason": "Data APIs overview page — not a single operation"},
    # MoEngage Streams — feature setup guide, not API reference.
    "4952761690644": {"skip_diff": True, "skip_reason": "Feature/setup guide, no OpenAPI operation"},
    # Personalize API — article documents 5 separate operations; needs human split.
    "24787922896276": {"skip_diff": True, "skip_reason": "Multi-endpoint article; split into per-op diffs manually"},

    # Global Control Group — no op exists yet in campaigns.yaml.
    "42053298082708": {"skip_diff": True, "skip_reason": "No existing OpenAPI operation; net-new article to add"},
}

# api/<dir>/<file>.yaml on disk. We just map filename -> relative path.
API_DIR = ROOT.parents[1] / "api"


def discover_yaml_paths() -> dict[str, str]:
    out = {}
    for p in API_DIR.glob("*/*.yaml"):
        rel = p.relative_to(ROOT.parents[1])
        out[p.name] = str(rel)
    return out


def slug_to_title(slug: str) -> str:
    return slug.replace("-", " ").strip()


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_url(url: str) -> tuple[str, str]:
    """Return (article_id, title_slug_as_text)."""
    url = url.strip()
    url = re.sub(r"#.*$", "", url)
    path = urlparse(url).path
    m = re.search(r"/articles/(\d+)-(.+?)/?$", path)
    if not m:
        m2 = re.search(r"/articles/(\d+)/?$", path)
        if not m2:
            raise ValueError(f"could not parse article id from {url}")
        return m2.group(1), ""
    article_id = m.group(1)
    title = slug_to_title(m.group(2))
    return article_id, title


def parse_csv(csv_path: Path) -> list[tuple[str, str]]:
    """Return list of (yaml_file_name, article_title) pairs.

    The CSV has four columns: yaml_file, section, subsection, article_title.
    yaml_file appears on rows that start a new file and is blank for rows
    belonging to the previous file. Titles can appear in any of columns
    1/2/3 depending on the row (some yamls use col 1, others col 3).
    """
    pairs: list[tuple[str, str]] = []
    current_yaml = None
    seen: set[tuple[str, str]] = set()
    with open(csv_path) as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            row = [c.strip() for c in row]
            while len(row) < 4:
                row.append("")
            yaml_col, c1, c2, c3 = row[0], row[1], row[2], row[3]
            if yaml_col:
                current_yaml = yaml_col
            if not current_yaml:
                continue
            for candidate in (c3, c2, c1):
                if candidate:
                    key = (current_yaml, candidate)
                    if key not in seen:
                        seen.add(key)
                        pairs.append(key)
    return pairs


def build():
    urls = [
        u.strip() for u in URLS_FILE.read_text().splitlines()
        if u.strip() and not u.strip().lower().startswith("article")
    ]
    if not urls:
        raise SystemExit(f"No URLs found in {URLS_FILE}")

    csv_pairs = parse_csv(CSV_FILE)
    yaml_files_on_disk = discover_yaml_paths()

    # Build a lookup: normalized article title -> list of (yaml_file, original_title)
    title_to_yaml: dict[str, list[tuple[str, str]]] = {}
    for yaml_name, title in csv_pairs:
        title_to_yaml.setdefault(norm(title), []).append((yaml_name, title))

    mapping: list[dict] = []
    unmapped: list[dict] = []
    collisions: list[dict] = []

    for url in urls:
        article_id, url_title = parse_url(url)
        n = norm(url_title)

        if article_id in MANUAL_ASSIGNMENTS:
            ma_yaml, ma_title, _ = MANUAL_ASSIGNMENTS[article_id]
            candidates = [(ma_yaml, ma_title)]
        else:
            candidates = title_to_yaml.get(n, [])

        if not candidates:
            # Try relaxed matches: substring in either direction.
            relaxed = []
            for k, v in title_to_yaml.items():
                if not k or not n:
                    continue
                if k == n or k in n or n in k:
                    relaxed.extend(v)
            candidates = list({tuple(x) for x in relaxed})
            candidates = [tuple(x) for x in candidates]

        if not candidates:
            unmapped.append({"article_id": article_id, "article_url": url, "article_title": url_title})
            continue

        if len(candidates) > 1:
            collisions.append({
                "article_id": article_id,
                "article_url": url,
                "article_title": url_title,
                "candidates": [{"yaml": c[0], "title": c[1]} for c in candidates],
            })

        yaml_name, original_title = candidates[0]
        resolved_yaml = YAML_ALIASES.get(yaml_name, yaml_name)
        yaml_rel = yaml_files_on_disk.get(resolved_yaml)
        if not yaml_rel:
            unmapped.append({
                "article_id": article_id,
                "article_url": url,
                "article_title": url_title,
                "reason": f"yaml file {resolved_yaml} not found on disk",
            })
            continue

        entry = {
            "article_id": article_id,
            "article_url": url,
            "article_title": original_title,
            "yaml_path": yaml_rel,
            "operation_title": original_title,
        }
        if article_id in MANUAL_ASSIGNMENTS and MANUAL_ASSIGNMENTS[article_id][2]:
            entry["needs_review"] = True
        ov = OVERRIDES.get(article_id)
        if ov:
            entry.update(ov)
        mapping.append(entry)

    # Sort by yaml_path then title for readability.
    mapping.sort(key=lambda x: (x["yaml_path"], x["operation_title"]))

    with open(OUT_FILE, "w") as f:
        yaml.safe_dump(mapping, f, sort_keys=False, allow_unicode=True, width=120)

    print(f"Wrote {len(mapping)} entries to {OUT_FILE}")
    if collisions:
        print(f"\n{len(collisions)} URL(s) matched multiple CSV rows (first match used, review below):")
        for c in collisions:
            print(f"  - {c['article_id']} {c['article_title']}")
            for cand in c["candidates"]:
                print(f"      -> {cand['yaml']} :: {cand['title']}")
    needs_review = [m for m in mapping if m.get("needs_review")]
    if needs_review:
        print(f"\n{len(needs_review)} entry(ies) flagged needs_review (manual placement, please confirm):")
        for m in needs_review:
            print(f"  - {m['article_id']} {m['article_title']} -> {m['yaml_path']}")

    if unmapped:
        print(f"\n{len(unmapped)} URL(s) could not be mapped:")
        for u in unmapped:
            print(f"  - {u}")
        sys.exit(1)


if __name__ == "__main__":
    build()
