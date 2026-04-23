"""Parse Zendesk Help Center article HTML into canonical JSON.

The Zendesk articles follow a fairly consistent layout:

  <p>(summary)</p>
  <div class="callout">... optional note ...</div>
  <h1>API Endpoint</h1>       <pre><code>METHOD URL</code></pre>
  <h1>Authentication</h1>      ... description ...
  <h1>Request Headers</h1>     <table>Key|Required|Sample Values|Description</table>
  <h1>Request Body</h1>        <table>Key|Required|Values|Description</table>   (optional)
  <h1>Request Query Parameters</h1> same shape                                   (optional)
  <h1>Response</h1>            <table>Key|Data Type|Description</table>
  <h1>Response Codes</h1>      <table>Status Code|Request State|Description</table>
  <h1>Rate Limit</h1>          <p>...</p>
  <h1>Sample cURL Request</h1> <pre><code>...</code></pre>
  <h1>Sample Response</h1>     (tabs with code blocks per status)

We iterate h1 sections and dispatch to handlers. Missing or renamed sections
are tolerated; we record what we find.
"""
from __future__ import annotations

import html
import re
from typing import Any

from bs4 import BeautifulSoup, NavigableString, Tag

from .canonical import empty_canonical, normalize_required


SECTION_ALIASES = {
    "api endpoint": "endpoint",
    "endpoint": "endpoint",
    "authentication": "authentication",
    "request headers": "headers",
    "request header": "headers",
    "headers": "headers",
    "header": "headers",
    "request body": "request_body",
    "request body parameters": "request_body",
    "request body fields": "request_body",
    "body parameters": "request_body",
    "body": "request_body",
    "request parameters": "request_body",
    "request query parameters": "request_body",
    "query parameters": "request_body",
    "request path parameters": "request_body",
    "path parameters": "request_body",
    "parameters": "request_body",
    "response": "response",
    "response body": "response",
    "response parameters": "response",
    "response fields": "response",
    "response codes": "response_codes",
    "status codes": "response_codes",
    "response status codes": "response_codes",
    "rate limit": "rate_limit",
    "rate limits": "rate_limit",
    "sample curl request": "sample_curl",
    "sample curl": "sample_curl",
    "sample request": "sample_curl",
    "sample requests": "sample_curl",
    "sample payload": "sample_curl",
    "sample response": "sample_response",
    "sample responses": "sample_response",
}


def _text(tag) -> str:
    """Get clean, whitespace-collapsed text."""
    if tag is None:
        return ""
    if isinstance(tag, NavigableString):
        s = str(tag)
    else:
        s = tag.get_text(" ", strip=False)
    s = html.unescape(s)
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _block_text(tag) -> str:
    """Get text, but keep paragraph breaks as newlines."""
    if tag is None:
        return ""
    parts = []
    for p in tag.find_all(["p", "li"], recursive=True):
        t = _text(p)
        if t:
            parts.append(t)
    if not parts:
        return _text(tag)
    return "\n".join(parts)


def _iter_siblings_until_next_section(h: Tag, section_tags: tuple[str, ...]):
    for sib in h.next_siblings:
        if isinstance(sib, Tag) and sib.name in section_tags:
            return
        yield sib


def _pick_section_tags(soup: BeautifulSoup) -> tuple[str, ...]:
    """Articles mix h1 and h2 for section headings. Collect all heading levels
    that contain at least one recognisable section label and treat all of them
    as section delimiters."""
    tags: list[str] = []
    for tag_name in ("h1", "h2"):
        for h in soup.find_all(tag_name):
            if _classify_section(_text(h)) is not None:
                tags.append(tag_name)
                break
    if not tags:
        tags = ["h1"]
    return tuple(tags)


def _first(tag_name: str, scope):
    for el in scope:
        if isinstance(el, Tag):
            found = el.find(tag_name)
            if found is not None:
                return found
    return None


def _find_table(scope):
    for el in scope:
        if not isinstance(el, Tag):
            continue
        tbl = el if el.name == "table" else el.find("table")
        if tbl is not None:
            return tbl
    return None


def _table_rows(table: Tag) -> list[list[Tag]]:
    rows = []
    for tr in table.find_all("tr"):
        cells = tr.find_all(["td", "th"])
        if cells:
            rows.append(cells)
    return rows


def _parse_table_dict(table: Tag, column_map: dict[str, list[str]]) -> list[dict[str, str]]:
    """Parse a table into a list of row dicts keyed by logical column name.

    column_map: {"name": ["Key"], "required": ["Required"], "type": ["Values", "Data Type", "Value"], ...}
    First row is treated as header.
    """
    rows = _table_rows(table)
    if not rows:
        return []
    header_cells = rows[0]
    header_norm = [_text(c).lower() for c in header_cells]

    idx: dict[str, int] = {}
    for logical, aliases in column_map.items():
        for a in aliases:
            a_norm = a.lower()
            for i, h in enumerate(header_norm):
                if h == a_norm or a_norm in h:
                    idx[logical] = i
                    break
            if logical in idx:
                break

    out = []
    for row in rows[1:]:
        if len(row) < 2:
            continue
        entry: dict[str, str] = {}
        for logical in column_map:
            i = idx.get(logical)
            if i is None or i >= len(row):
                entry[logical] = ""
                continue
            cell = row[i]
            if logical == "description":
                entry[logical] = _block_text(cell)
            else:
                entry[logical] = _text(cell)
        if any(v for v in entry.values()):
            out.append(entry)
    return out


def _classify_section(h1_text: str) -> str | None:
    t = (h1_text or "").lower().strip().rstrip(":")
    if t in SECTION_ALIASES:
        return SECTION_ALIASES[t]
    for key, logical in SECTION_ALIASES.items():
        if key in t:
            return logical
    return None


_METHOD_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b", re.IGNORECASE)


def _parse_endpoint(children) -> dict[str, str]:
    code = _first("code", children) or _first("pre", children)
    raw = _text(code) if code else ""
    raw = raw.strip()

    # Common case: "POST https://..."
    m = re.match(r"^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(\S+)", raw, re.IGNORECASE)
    if m:
        return {"method": m.group(1).upper(), "url": m.group(2)}

    parts = raw.split()
    if parts and parts[0].upper() in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
        return {"method": parts[0].upper(), "url": parts[1] if len(parts) > 1 else ""}

    # Newer layout: method in a separate `<p>Method: <strong>POST</strong></p>` paragraph.
    method = ""
    for el in children:
        if isinstance(el, Tag) and el.name in ("p", "div"):
            t = _text(el)
            mm = re.search(r"method\s*[:\-]?\s*(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)", t, re.IGNORECASE)
            if mm:
                method = mm.group(1).upper()
                break

    # URL is whatever was in the code block (stripped).
    return {"method": method, "url": raw}


def _parse_callouts(soup: BeautifulSoup) -> list[str]:
    out = []
    for div in soup.select("div.callout, .callout"):
        txt = _block_text(div)
        if txt:
            out.append(txt)
    return out


def _find_code_blocks(children) -> list[str]:
    blocks = []
    for el in children:
        if not isinstance(el, Tag):
            continue
        for pre in el.find_all(["pre", "code"], recursive=True):
            t = pre.get_text()
            t = html.unescape(t)
            t = t.replace("\xa0", " ")
            blocks.append(t.strip())
    return blocks


def _parse_sample_response(children) -> dict[str, str]:
    """Sample Response section usually has tabs keyed by status code."""
    out: dict[str, str] = {}
    tab_menus = []
    tabs = []
    for el in children:
        if not isinstance(el, Tag):
            continue
        tab_menus.extend(el.select(".tabs-menu"))
        tabs.extend(el.select(".tab"))
    # Build ordered list of labels from all tabs-menu groups.
    labels: list[str] = []
    for menu in tab_menus:
        for span in menu.find_all(["span", "a"], class_=["tabs-link"]):
            labels.append(_text(span))
    # Get pre bodies for the same tab order.
    bodies: list[str] = []
    for t in tabs:
        pre = t.find(["pre", "code"])
        body = ""
        if pre is not None:
            body = html.unescape(pre.get_text())
        bodies.append(body.strip())

    # Pair them up; fall back to index if counts mismatch.
    if labels and len(labels) == len(bodies):
        for lbl, body in zip(labels, bodies):
            if lbl and body:
                out[lbl.strip()] = body
    else:
        for i, body in enumerate(bodies):
            key = labels[i] if i < len(labels) else str(i)
            if body:
                out[key] = body

    if not out:
        # Fallback: collect every code block and try to guess a status code from the body.
        for body in _find_code_blocks(children):
            m = re.search(r"\b([1-5]\d{2}|5xx)\b", body[:200])
            key = m.group(1) if m else str(len(out))
            out[key] = body
    return out


def parse_zendesk_html(body_html: str, meta: dict[str, Any]) -> dict[str, Any]:
    soup = BeautifulSoup(body_html, "lxml")
    # Strip HTML comments wholesale since Zendesk has commented-out legacy tabs.
    for c in soup.find_all(string=lambda s: isinstance(s, NavigableString) and getattr(s, "output_ready", False) is False):
        pass  # no-op; bs4 handles comments separately below
    from bs4 import Comment
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()

    canonical = empty_canonical()
    canonical["source"] = {
        "kind": "zendesk",
        "article_id": meta.get("article_id"),
        "article_url": meta.get("article_url"),
        "yaml_path": None,
        "operation_title": meta.get("article_title"),
        "draft": meta.get("draft"),
        "updated_at": meta.get("updated_at"),
    }
    canonical["title"] = meta.get("article_title") or ""

    section_tags = _pick_section_tags(soup)
    first_h = soup.find(list(section_tags))

    if first_h is not None:
        summary_tags = []
        for sib in first_h.previous_siblings:
            if isinstance(sib, Tag) and sib.name in ("p", "ul", "ol"):
                summary_tags.append(sib)
        summary_tags.reverse()
        canonical["summary"] = "\n".join(_text(t) for t in summary_tags if _text(t))
    else:
        canonical["summary"] = _text(soup).strip()

    # Top-level callouts (appear once per page, outside of section blocks).
    canonical["notes"] = _parse_callouts(soup)

    for h in soup.find_all(list(section_tags)):
        label = _text(h)
        section = _classify_section(label)
        if section is None:
            continue

        children = list(_iter_siblings_until_next_section(h, section_tags))

        if section == "endpoint":
            canonical["endpoint"] = _parse_endpoint(children)
        elif section == "headers":
            tbl = _find_table(children)
            if tbl is not None:
                rows = _parse_table_dict(tbl, {
                    "name": ["Key", "Name", "Header"],
                    "required": ["Required"],
                    "sample": ["Sample Values", "Sample", "Example"],
                    "description": ["Description"],
                })
                for r in rows:
                    r["required"] = normalize_required(r.get("required", ""))
                canonical["headers"] = rows
        elif section == "request_body":
            tbl = _find_table(children)
            if tbl is not None:
                rows = _parse_table_dict(tbl, {
                    "name": ["Key", "Parameter", "Field", "Name"],
                    "required": ["Required"],
                    "type": ["Values", "Value", "Data Type", "Type"],
                    "description": ["Description"],
                })
                for r in rows:
                    r["required"] = normalize_required(r.get("required", ""))
                canonical["request_body"].extend(rows)
        elif section == "response":
            tbl = _find_table(children)
            if tbl is not None:
                rows = _parse_table_dict(tbl, {
                    "name": ["Key", "Field", "Parameter", "Name"],
                    "type": ["Data Type", "Type", "Value", "Values"],
                    "description": ["Description"],
                })
                canonical["response_fields"] = rows
        elif section == "response_codes":
            tbl = _find_table(children)
            if tbl is not None:
                rows = _parse_table_dict(tbl, {
                    "code": ["Status Code", "Code"],
                    "state": ["Request State", "State", "Status"],
                    "description": ["Description"],
                })
                canonical["response_codes"] = rows
        elif section == "rate_limit":
            paragraphs = []
            for el in children:
                if isinstance(el, Tag) and el.name in ("p", "ul", "ol", "div"):
                    t = _block_text(el)
                    if t:
                        paragraphs.append(t)
            canonical["rate_limit"] = "\n".join(paragraphs).strip()
        elif section == "sample_curl":
            blocks = _find_code_blocks(children)
            canonical["samples"]["curl"] = blocks[0] if blocks else ""
        elif section == "sample_response":
            canonical["samples"]["responses"] = _parse_sample_response(children)

    return canonical
