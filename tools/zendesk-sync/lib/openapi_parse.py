"""Parse an OpenAPI YAML operation into canonical JSON.

Matches operations by summary (case-insensitive) against the mapping entry's
`operation_title`. When the title is ambiguous inside a YAML (same summary
used twice) we fall back to the operationId.
"""
from __future__ import annotations

import re
from typing import Any

import yaml

from .canonical import empty_canonical, normalize_required


METHODS = ("get", "post", "put", "patch", "delete", "head", "options")


def load_yaml(path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def _resolve_ref(doc: dict, ref: str) -> dict:
    assert ref.startswith("#/"), f"external refs not supported: {ref}"
    parts = ref[2:].split("/")
    cur: Any = doc
    for p in parts:
        cur = cur[p]
    return cur


def _deref(doc: dict, node: Any, seen: set[str] | None = None) -> Any:
    """Return a fully-dereferenced copy of node. Handles simple cycles."""
    seen = seen or set()
    if isinstance(node, dict):
        if "$ref" in node and isinstance(node["$ref"], str):
            ref = node["$ref"]
            if ref in seen:
                return {"$ref": ref, "__cycle__": True}
            seen2 = seen | {ref}
            target = _resolve_ref(doc, ref)
            return _deref(doc, target, seen2)
        return {k: _deref(doc, v, seen) for k, v in node.items()}
    if isinstance(node, list):
        return [_deref(doc, v, seen) for v in node]
    return node


def _schema_type(schema: dict) -> str:
    if not isinstance(schema, dict):
        return ""
    t = schema.get("type")
    if isinstance(t, list):
        t = next((x for x in t if x != "null"), t[0] if t else "")
    if t == "array":
        item_t = _schema_type(schema.get("items") or {})
        if item_t:
            return f"array of {item_t}"
        return "array"
    if t == "object":
        return "object"
    return t or ""


def _flatten_properties(schema: dict) -> list[dict[str, str]]:
    if not isinstance(schema, dict):
        return []
    # Handle anyOf/oneOf: merge the first object schema's properties.
    for key in ("anyOf", "oneOf", "allOf"):
        arr = schema.get(key)
        if isinstance(arr, list):
            merged = {}
            merged_required: list[str] = []
            for sub in arr:
                if not isinstance(sub, dict):
                    continue
                for p, s in (sub.get("properties") or {}).items():
                    merged[p] = s
                merged_required.extend(sub.get("required") or [])
            if merged:
                schema = {
                    "type": "object",
                    "properties": merged,
                    "required": list(dict.fromkeys(merged_required)),
                    "description": schema.get("description", ""),
                }
                break

    props = schema.get("properties") or {}
    required = set(schema.get("required") or [])
    out: list[dict[str, str]] = []
    for name, prop in props.items():
        if not isinstance(prop, dict):
            prop = {}
        out.append({
            "name": name,
            "required": "required" if name in required else "optional",
            "type": _schema_type(prop),
            "description": (prop.get("description") or "").strip(),
        })
    return out


_RATE_LIMIT_RE = re.compile(r"#+\s*Rate\s*Limit\s*\n+(.+?)(?:\n\n|\n#|\Z)", re.IGNORECASE | re.DOTALL)


def _extract_rate_limit(x_mint: dict | None, description: str | None) -> str:
    text = ""
    if isinstance(x_mint, dict):
        text = x_mint.get("content") or ""
    if not text and description:
        text = description
    m = _RATE_LIMIT_RE.search(text or "")
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    return ""


_NOTE_RE = re.compile(r"<Note>\s*(?:\*\*Note\*\*\s*\n+)?(.+?)</Note>", re.IGNORECASE | re.DOTALL)


def _extract_notes(x_mint: dict | None, description: str | None) -> list[str]:
    blobs = []
    for src in (x_mint.get("content") if isinstance(x_mint, dict) else None, description):
        if src:
            for m in _NOTE_RE.finditer(src):
                blobs.append(m.group(1).strip())
    return blobs


def _find_operation(
    doc: dict, mapping_title: str
) -> tuple[str, str, dict] | None:
    target = (mapping_title or "").strip().lower()
    paths = doc.get("paths") or {}
    candidates: list[tuple[int, str, str, dict]] = []
    for path, item in paths.items():
        if not isinstance(item, dict):
            continue
        for method in METHODS:
            op = item.get(method)
            if not isinstance(op, dict):
                continue
            summary = (op.get("summary") or "").strip().lower()
            op_id = (op.get("operationId") or "").strip().lower()
            score = 0
            if summary == target:
                score = 100
            elif target in summary or summary in target:
                score = 80
            elif op_id and (op_id in target.replace(" ", "") or target.replace(" ", "") in op_id):
                score = 60
            if score:
                candidates.append((score, path, method, op))
    if not candidates:
        return None
    candidates.sort(key=lambda x: -x[0])
    _, path, method, op = candidates[0]
    return path, method, op


def _server_url(doc: dict) -> str:
    servers = doc.get("servers") or []
    if servers and isinstance(servers[0], dict):
        return (servers[0].get("url") or "").rstrip("/")
    return ""


def _parse_headers(op: dict, doc: dict) -> list[dict[str, str]]:
    headers: list[dict[str, str]] = []
    # Header parameters
    for p in op.get("parameters") or []:
        p = _deref(doc, p)
        if (p or {}).get("in") != "header":
            continue
        schema = p.get("schema") or {}
        headers.append({
            "name": p.get("name", ""),
            "required": "required" if p.get("required") else "optional",
            "sample": str(p.get("example", "")),
            "description": (p.get("description") or "").strip(),
        })
    # Security schemes implied at operation or doc level.
    sec_entries = op.get("security")
    if sec_entries is None:
        sec_entries = doc.get("security") or []
    schemes = (doc.get("components") or {}).get("securitySchemes") or {}
    for s in sec_entries:
        if not isinstance(s, dict):
            continue
        for name in s.keys():
            scheme = schemes.get(name) or {}
            scheme_type = scheme.get("type")
            if scheme_type == "http" and scheme.get("scheme") in ("basic", "bearer"):
                headers.append({
                    "name": "Authorization",
                    "required": "required",
                    "sample": "",
                    "description": (scheme.get("description") or "").strip(),
                })
            elif scheme_type == "apiKey" and scheme.get("in") == "header":
                headers.append({
                    "name": scheme.get("name") or name,
                    "required": "required",
                    "sample": "",
                    "description": (scheme.get("description") or "").strip(),
                })
    return headers


def _parse_request_body(op: dict, doc: dict) -> list[dict[str, str]]:
    rb = op.get("requestBody")
    if not rb:
        return []
    content = (rb.get("content") or {}).get("application/json") or {}
    schema = content.get("schema")
    if not schema:
        return []
    schema = _deref(doc, schema)
    return _flatten_properties(schema)


def _parse_responses(op: dict, doc: dict):
    fields: list[dict[str, str]] = []
    codes: list[dict[str, str]] = []
    responses = op.get("responses") or {}
    samples: dict[str, str] = {}
    for code, resp in responses.items():
        resp = _deref(doc, resp)
        codes.append({
            "code": str(code),
            "state": "",
            "description": (resp.get("description") or "").strip(),
        })
        content = (resp.get("content") or {}).get("application/json") or {}
        # Grab the schema properties for the FIRST success response only.
        if str(code).startswith("2") and not fields:
            schema = content.get("schema")
            if schema:
                fields = _flatten_properties(_deref(doc, schema))
        ex = content.get("example")
        if ex is not None:
            samples[str(code)] = ex if isinstance(ex, str) else yaml.safe_dump(ex, sort_keys=False)
        elif content.get("examples"):
            ex_items = content["examples"]
            if isinstance(ex_items, dict):
                first = next(iter(ex_items.values()), None)
                if isinstance(first, dict) and "value" in first:
                    v = first["value"]
                    samples[str(code)] = v if isinstance(v, str) else yaml.safe_dump(v, sort_keys=False)
    return fields, codes, samples


def _extract_code_sample(op: dict) -> str:
    for key in ("x-codeSamples", "x-code-samples", "x-codesamples"):
        samples = op.get(key)
        if isinstance(samples, list):
            for s in samples:
                if not isinstance(s, dict):
                    continue
                lang = (s.get("lang") or "").lower()
                if lang in ("curl", "shell", "bash"):
                    return s.get("source", "")
    return ""


def parse_openapi_operation(yaml_path, operation_title: str, mapping_meta: dict) -> dict | None:
    doc = load_yaml(yaml_path)
    match = _find_operation(doc, operation_title)
    if match is None:
        return None
    path, method, op = match

    canonical = empty_canonical()
    canonical["source"] = {
        "kind": "openapi",
        "article_id": mapping_meta.get("article_id"),
        "article_url": mapping_meta.get("article_url"),
        "yaml_path": mapping_meta.get("yaml_path"),
        "operation_title": op.get("summary") or operation_title,
        "operation_id": op.get("operationId"),
        "path": path,
        "method": method.upper(),
    }
    canonical["title"] = op.get("summary") or ""
    canonical["summary"] = (op.get("description") or "").strip()

    server = _server_url(doc)
    canonical["endpoint"] = {
        "method": method.upper(),
        "url": f"{server}{path}",
    }

    canonical["headers"] = _parse_headers(op, doc)
    canonical["request_body"] = _parse_request_body(op, doc)

    fields, codes, samples = _parse_responses(op, doc)
    canonical["response_fields"] = fields
    canonical["response_codes"] = codes
    canonical["samples"]["responses"] = samples
    canonical["samples"]["curl"] = _extract_code_sample(op)

    canonical["rate_limit"] = _extract_rate_limit(op.get("x-mint"), op.get("description"))
    canonical["notes"] = _extract_notes(op.get("x-mint"), op.get("description"))

    return canonical
