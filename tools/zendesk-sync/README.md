# Zendesk → Mintlify OpenAPI sync tool

One-off tool to reconcile API docs in this repo with the Zendesk Help Center
source of truth (`developers.moengage.com`) before Zendesk is sunset.

## Why this exists

During the Zendesk → Mintlify migration, we converted static HTML articles to
OpenAPI specs. Because the migration took ~3 months, some Zendesk articles
received updates that never made it to the OpenAPI YAMLs. This tool:

1. Pulls the latest content (including unpublished drafts) from Zendesk for a
   pre-mapped list of articles.
2. Parses both the Zendesk HTML and the local OpenAPI YAML into a canonical
   JSON shape.
3. Diffs them and produces a Markdown report per article.
4. An agent (or human) then applies the edits to YAML and opens one PR per
   YAML file.

The tool is read-only against Zendesk. It only writes to this repo.

## Setup

```bash
cd tools/zendesk-sync
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.local.example .env.local
# Edit .env.local with your Zendesk credentials
```

## Usage

Run the full pipeline:

```bash
python fetch.py              # pulls translations for all mapped articles
python parse_zendesk.py      # HTML -> canonical JSON
python parse_openapi.py      # YAML ops -> canonical JSON
python diff.py               # writes reports/<article_id>.md + reports/INDEX.md
```

Scope to a single article for the pilot / debugging:

```bash
python fetch.py --article 18187673580564
python parse_zendesk.py --article 18187673580564
python parse_openapi.py --article 18187673580564
python diff.py --article 18187673580564
```

## Layout

```
tools/zendesk-sync/
  mapping.yaml                 # article_id -> yaml_path + operation_ref
  fetch.py
  parse_zendesk.py
  parse_openapi.py
  diff.py
  lib/                         # shared helpers
  snapshots/                   # gitignored, regenerable
    zendesk/raw/<id>.json      # raw translation payload from Zendesk
    zendesk/canonical/<id>.json
    openapi/canonical/<id>.json
  reports/                     # committed
    <article_id>.md
    INDEX.md
```

## Canonical shape

See `lib/canonical.py` for the schema. Every diff operates on this shape, not
on raw HTML or YAML text, so wording noise (`&nbsp;`, whitespace) doesn't
produce false positives.

## Draft handling

Zendesk stores unpublished edits in the translation object
(`/articles/{id}/translations/en-us.json`) with `draft: true`. We always fetch
from the translation endpoint, so draft content is captured. The `draft` flag
is recorded in every snapshot and surfaced in the diff report so you know
whether a change comes from published or unpublished Zendesk content.
