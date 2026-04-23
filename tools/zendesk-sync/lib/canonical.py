"""Canonical representation of a single API operation.

Both the Zendesk HTML parser and the OpenAPI YAML parser emit dicts in this
shape. The diff tool compares these dicts, not raw HTML/YAML text, so small
formatting differences (&nbsp;, whitespace, HTML entities) don't produce
false positives.
"""
from __future__ import annotations

from typing import Any


def empty_canonical() -> dict[str, Any]:
    return {
        "source": {
            "kind": "",            # "zendesk" or "openapi"
            "article_id": None,
            "article_url": None,
            "yaml_path": None,
            "operation_title": None,
            "draft": None,
            "updated_at": None,
        },
        "title": "",
        "summary": "",             # top-level paragraph under the title
        "endpoint": {
            "method": "",          # e.g. "POST"
            "url": "",             # e.g. "https://api-{dc}.moengage.com/..."
        },
        "headers": [],             # list of {name, required, sample, description}
        "request_body": [],        # list of {name, required, type, description}
        "response_fields": [],     # list of {name, type, description}
        "response_codes": [],      # list of {code, state, description}
        "rate_limit": "",
        "samples": {
            "curl": "",
            "responses": {},       # {status_code_str: body}
        },
        "notes": [],               # standalone callouts / notes captured from page
    }


FIELD_NORMALIZE = {
    "required": {
        "required": "required",
        "yes": "required",
        "y": "required",
        "true": "required",
        "optional": "optional",
        "no": "optional",
        "n": "optional",
        "false": "optional",
        "": "",
    },
}


def normalize_required(val: str) -> str:
    return FIELD_NORMALIZE["required"].get((val or "").strip().lower(), (val or "").strip().lower())
