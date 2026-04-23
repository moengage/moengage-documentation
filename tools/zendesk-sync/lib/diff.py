"""Compute a classified diff between two canonical JSON snapshots.

The diff is emitted as a list of dicts with:
  kind: "structural" | "textual" | "sample"
  severity: "high" | "medium" | "low"
  path:  e.g. "request_body.template_id.type"
  zendesk: value from Zendesk
  openapi: value from OpenAPI
  note:  short human-readable summary
"""
from __future__ import annotations

import difflib
import re
from typing import Any


def _norm_text(s: str) -> str:
    if not s:
        return ""
    s = s.replace("\xa0", " ").strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    return s


def _norm_url(s: str) -> str:
    """Treat placeholders 0X / {dc} / {{0X}} as equivalent; strip trailing slash."""
    if not s:
        return ""
    s = s.strip().rstrip("/")
    s = re.sub(r"\{\{?\s*[A-Za-z_]+\s*\}?\}", "{dc}", s)
    s = re.sub(r"0X|0x", "{dc}", s)
    return s.lower()


def _norm_type(s: str) -> str:
    if not s:
        return ""
    s = _norm_text(s).lower()
    mapping = {
        "list of strings": "array of string",
        "list of string": "array of string",
        "array of strings": "array of string",
        "list of integers": "array of integer",
        "array of integers": "array of integer",
        "list of booleans": "array of boolean",
        "array of booleans": "array of boolean",
        "list of objects": "array of object",
        "array of objects": "array of object",
        "list of json objects": "array of object",
        "array of json objects": "array of object",
        "json object": "object",
        "json": "object",
        "integer": "integer",
        "int": "integer",
        "bool": "boolean",
        "str": "string",
    }
    s = mapping.get(s, s)
    # Treat any "list of <X>" that's not in the map as an array.
    if s.startswith("list of "):
        s = "array of object"
    return s


def _types_compatible(zd: str, oa: str) -> bool:
    """Relaxed equality: OpenAPI 'array of object' matches any Zendesk array-of-anything,
    and plain 'object' matches any Zendesk object-like type."""
    z = _norm_type(zd)
    o = _norm_type(oa)
    if z == o:
        return True
    if z.startswith("array of") and o == "array of object":
        return True
    if o.startswith("array of") and z == "array of object":
        return True
    return False


def _norm_rate_limit(s: str) -> str:
    s = _norm_text(s).lower()
    s = re.sub(r"requests?\s+per\s+minute", "rpm", s)
    s = re.sub(r"r\.?p\.?m\.?", "rpm", s)
    s = re.sub(r"(\d)\s*rpm", r"\1 rpm", s)
    return s


def _index_by_name(items: list[dict], key: str = "name") -> dict[str, dict]:
    return {(it.get(key) or "").strip(): it for it in items if it.get(key)}


def _text_similarity(a: str, b: str) -> float:
    a, b = _norm_text(a), _norm_text(b)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def diff_canonicals(zd: dict, oa: dict) -> list[dict[str, Any]]:
    diffs: list[dict[str, Any]] = []

    # Endpoint
    if _norm_url(zd["endpoint"].get("url", "")) != _norm_url(oa["endpoint"].get("url", "")):
        diffs.append({
            "kind": "structural", "severity": "high",
            "path": "endpoint.url",
            "zendesk": zd["endpoint"].get("url", ""),
            "openapi": oa["endpoint"].get("url", ""),
            "note": "Endpoint URL differs",
        })
    if (zd["endpoint"].get("method") or "").upper() != (oa["endpoint"].get("method") or "").upper():
        diffs.append({
            "kind": "structural", "severity": "high",
            "path": "endpoint.method",
            "zendesk": zd["endpoint"].get("method"),
            "openapi": oa["endpoint"].get("method"),
            "note": "HTTP method differs",
        })

    # Headers
    _diff_listed("headers", zd.get("headers") or [], oa.get("headers") or [], diffs)
    # Request body
    _diff_listed("request_body", zd.get("request_body") or [], oa.get("request_body") or [], diffs)
    # Response fields
    _diff_listed("response_fields", zd.get("response_fields") or [], oa.get("response_fields") or [], diffs, has_required=False)
    # Response codes
    _diff_codes(zd.get("response_codes") or [], oa.get("response_codes") or [], diffs)

    # Rate limit
    if _norm_rate_limit(zd.get("rate_limit", "")) != _norm_rate_limit(oa.get("rate_limit", "")):
        diffs.append({
            "kind": "textual", "severity": "medium",
            "path": "rate_limit",
            "zendesk": zd.get("rate_limit", ""),
            "openapi": oa.get("rate_limit", ""),
            "note": "Rate limit text differs",
        })

    # Notes / callouts
    _diff_notes(zd.get("notes") or [], oa.get("notes") or [], diffs)

    # Samples: curl and response bodies are too noisy for exact diff; only flag
    # presence differences and large similarity drops.
    _diff_samples(zd.get("samples") or {}, oa.get("samples") or {}, diffs)

    return diffs


def _diff_listed(kind: str, zd_list: list, oa_list: list, diffs: list, has_required: bool = True):
    zd_idx = _index_by_name(zd_list)
    oa_idx = _index_by_name(oa_list)
    zd_names = list(zd_idx.keys())
    oa_names = set(oa_idx.keys())

    # Added in Zendesk (missing in OpenAPI)
    for name in zd_names:
        if name not in oa_names:
            diffs.append({
                "kind": "structural", "severity": "high",
                "path": f"{kind}.{name}",
                "zendesk": zd_idx[name],
                "openapi": None,
                "note": f"Field `{name}` exists in Zendesk but is missing from OpenAPI",
            })

    # Removed in Zendesk (extra in OpenAPI). Could be deprecated or intentional.
    for name in oa_idx:
        if name not in zd_idx:
            diffs.append({
                "kind": "structural", "severity": "medium",
                "path": f"{kind}.{name}",
                "zendesk": None,
                "openapi": oa_idx[name],
                "note": f"Field `{name}` exists in OpenAPI but not in Zendesk (may be deprecated or Zendesk is missing it)",
            })

    # Fields present on both sides: compare attributes.
    for name in zd_names:
        if name not in oa_idx:
            continue
        zd = zd_idx[name]
        oa = oa_idx[name]

        if has_required:
            zr = (zd.get("required") or "").lower()
            or_ = (oa.get("required") or "").lower()
            if zr and or_ and zr != or_:
                diffs.append({
                    "kind": "structural", "severity": "high",
                    "path": f"{kind}.{name}.required",
                    "zendesk": zr,
                    "openapi": or_,
                    "note": f"`{name}` required flag differs",
                })

        zt = zd.get("type", "")
        ot = oa.get("type", "")
        if zt and ot and not _types_compatible(zt, ot):
            diffs.append({
                "kind": "structural", "severity": "high",
                "path": f"{kind}.{name}.type",
                "zendesk": zt,
                "openapi": ot,
                "note": f"`{name}` type differs",
            })

        zd_desc = _norm_text(zd.get("description", ""))
        oa_desc = _norm_text(oa.get("description", ""))
        if zd_desc != oa_desc:
            sim = _text_similarity(zd_desc, oa_desc)
            if sim >= 0.97:
                continue
            severity = "low" if sim > 0.85 else "medium"
            diffs.append({
                "kind": "textual", "severity": severity,
                "path": f"{kind}.{name}.description",
                "zendesk": zd.get("description", ""),
                "openapi": oa.get("description", ""),
                "note": f"`{name}` description differs (similarity {sim:.2f})",
            })


def _code_bucket(code: str) -> str:
    """Group status codes so Zendesk '5xx' matches OpenAPI '500', '503', etc."""
    code = str(code).strip().lower()
    if code in ("5xx", "500", "502", "503", "504"):
        return "5xx"
    if code in ("4xx", "400"):
        # Leave specific 4xx codes alone; only literal '4xx' collapses.
        return code
    return code


def _diff_codes(zd: list, oa: list, diffs: list):
    zd_idx = {_code_bucket(c.get("code")): c for c in zd if c.get("code")}
    oa_idx = {_code_bucket(c.get("code")): c for c in oa if c.get("code")}
    for code in zd_idx:
        if code not in oa_idx:
            diffs.append({
                "kind": "structural", "severity": "medium",
                "path": f"response_codes.{code}",
                "zendesk": zd_idx[code],
                "openapi": None,
                "note": f"Response code `{code}` documented in Zendesk, absent in OpenAPI",
            })
    for code in oa_idx:
        if code not in zd_idx:
            diffs.append({
                "kind": "structural", "severity": "low",
                "path": f"response_codes.{code}",
                "zendesk": None,
                "openapi": oa_idx[code],
                "note": f"Response code `{code}` in OpenAPI only",
            })
    for code in zd_idx:
        if code not in oa_idx:
            continue
        zd_desc = _norm_text(zd_idx[code].get("description", ""))
        oa_desc = _norm_text(oa_idx[code].get("description", ""))
        if zd_desc and oa_desc and zd_desc != oa_desc:
            sim = _text_similarity(zd_desc, oa_desc)
            if sim < 0.9:
                diffs.append({
                    "kind": "textual", "severity": "low",
                    "path": f"response_codes.{code}.description",
                    "zendesk": zd_idx[code].get("description", ""),
                    "openapi": oa_idx[code].get("description", ""),
                    "note": f"Response code {code} description differs (similarity {sim:.2f})",
                })


def _diff_notes(zd_notes: list[str], oa_notes: list[str], diffs: list):
    """Best-effort match zendesk notes to openapi notes by similarity."""
    zd_norm = [_norm_text(n) for n in zd_notes]
    oa_norm = [_norm_text(n) for n in oa_notes]
    oa_unused = list(range(len(oa_norm)))

    for i, zn in enumerate(zd_norm):
        best = (-1, 0.0)
        for j in oa_unused:
            sim = _text_similarity(zn, oa_norm[j])
            if sim > best[1]:
                best = (j, sim)
        if best[1] >= 0.55:
            oa_unused.remove(best[0])
            if best[1] < 0.95:
                diffs.append({
                    "kind": "textual", "severity": "low",
                    "path": f"notes[{i}]",
                    "zendesk": zd_notes[i],
                    "openapi": oa_notes[best[0]],
                    "note": f"Note text differs (similarity {best[1]:.2f})",
                })
        else:
            diffs.append({
                "kind": "textual", "severity": "medium",
                "path": f"notes[{i}]",
                "zendesk": zd_notes[i],
                "openapi": None,
                "note": "Zendesk has a note/callout not reflected in OpenAPI",
            })
    for j in oa_unused:
        diffs.append({
            "kind": "textual", "severity": "low",
            "path": f"notes.openapi[{j}]",
            "zendesk": None,
            "openapi": oa_notes[j],
            "note": "OpenAPI has a note/callout not present in Zendesk",
        })


def _diff_samples(zd: dict, oa: dict, diffs: list):
    zd_curl = (zd.get("curl") or "").strip()
    oa_curl = (oa.get("curl") or "").strip()
    if bool(zd_curl) != bool(oa_curl):
        diffs.append({
            "kind": "sample", "severity": "low",
            "path": "samples.curl",
            "zendesk": "present" if zd_curl else "missing",
            "openapi": "present" if oa_curl else "missing",
            "note": "cURL sample present on one side only",
        })
    elif zd_curl and oa_curl:
        sim = _text_similarity(zd_curl, oa_curl)
        if sim < 0.75:
            diffs.append({
                "kind": "sample", "severity": "low",
                "path": "samples.curl",
                "zendesk": zd_curl,
                "openapi": oa_curl,
                "note": f"cURL sample differs (similarity {sim:.2f})",
            })

    zd_resp = {_code_bucket(c) for c in (zd.get("responses") or {}).keys()}
    oa_resp = {_code_bucket(c) for c in (oa.get("responses") or {}).keys()}
    only_zd = zd_resp - oa_resp
    only_oa = oa_resp - zd_resp
    if only_zd:
        diffs.append({
            "kind": "sample", "severity": "low",
            "path": "samples.responses",
            "zendesk": sorted(only_zd),
            "openapi": [],
            "note": f"Zendesk has sample responses not in OpenAPI: {sorted(only_zd)}",
        })
    if only_oa:
        diffs.append({
            "kind": "sample", "severity": "low",
            "path": "samples.responses",
            "zendesk": [],
            "openapi": sorted(only_oa),
            "note": f"OpenAPI has sample responses not in Zendesk: {sorted(only_oa)}",
        })
