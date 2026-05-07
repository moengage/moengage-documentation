---
name: doc-reader
description: Read and navigate external documentation efficiently. Invoke when the task requires checking how a specific function, endpoint, or configuration option works; when the user references an API, SDK, library, or third-party tool by name; when any docs URL or documentation site is mentioned; or when implementing something that depends on an external service or package. Adapted from Mintlify's doc-reader skill.
license: MIT
compatibility: Requires internet access. Works best with Mintlify-powered documentation sites which provide MCP servers and llms.txt files.
metadata:
  author: MoEngage (adapted from Mintlify)
  version: "0.1"
---

# Read external documentation effectively

This skill helps you efficiently consume external documentation (including MoEngage's own published docs at https://www.moengage.com/docs/ and third-party references like FCM, APNs, Stripe, etc.) without overwhelming your context window or missing important information.

## Quick reference: choose your approach

| Situation | Approach |
|-----------|----------|
| First visit to a doc site | Check for llms.txt, then MCP |
| Know exactly what you're looking for | MCP search or grep llms-full.txt |
| Need to read a specific page | Try `.md` URL variant first, then HTML |
| Exploring / browsing | View HTML page in browser |
| Need comprehensive understanding | Load llms-full.txt (check length first) |
| Multiple doc sites in one task | Set up MCPs for each |

## Step 1: Discover what's available

When you encounter a documentation site, check for AI-friendly resources.

### Check for llms.txt

Every well-structured doc site should have an llms.txt file at the root. For example `https://docs.example.com/llms.txt` or `https://example.com/docs/llms.txt`.

The MoEngage docs themselves publish `https://www.moengage.com/docs/llms.txt` (and `llms-full.txt`).

This file contains:
- A description of what the documentation covers.
- Links to each page in the docs.

Sites may also have llms-full.txt files at the root which contain all the content as a single markdown file.

### Try markdown URL variants

Many doc sites (including every Mintlify-powered site) serve clean markdown versions of pages at `.md` URL variants. Prefer the `.md` extension for easier parsing:

```
https://docs.example.com/page      →  try https://docs.example.com/page.md
```

If it returns valid markdown (not a 404 or HTML error), use it instead of fetching the HTML.

### Check for skill.md

Some documentation sites provide a skill.md file that teaches you how to work with the product:

```
https://docs.example.com/skill.md
```

Read the skill to understand the product. Add it if it will help with your current task:

```bash
npx skills add docs.example.com/skill.md
```

### Check for MCP server

Some documentation sites provide MCP servers for semantic search. The endpoint often follows this pattern:

```
https://docs.example.com/mcp
```

## Step 2: Set up MCP if available

MCP (Model Context Protocol) servers let you search documentation semantically rather than relying on keyword matching or loading entire files.

### Connecting to the MCP

For Claude Code:

```json
{
  "mcpServers": {
    "example-docs": {
      "type": "http",
      "url": "https://docs.example.com/mcp"
    }
  }
}
```

Once connected, you'll have a search tool following the naming pattern `Search{DocsTitle}` (for example, `SearchMoEngage`).

### Managing multiple MCPs

When working with multiple doc sources:

1. Give each MCP a descriptive name based on the product or library.
2. Use the appropriate MCP for each query rather than searching all.

## Step 3: Choose your consumption strategy

### Strategy A: MCP search (preferred for targeted questions)

Use when:
- You have a specific question or topic.
- You're looking for a particular API, function, or concept.
- You want semantically relevant results, not just keyword matches.

### Strategy B: Fetch markdown variant (for reading specific pages)

Use when:
- You need to read a specific documentation page.
- MCP search returned a result but you need the full page content.
- HTML rendering is adding noise or causing truncation.

Try the `.md` variant of the page URL:

```bash
curl -s "https://docs.example.com/page.md"
```

If it returns valid markdown, use it. If it 404s, fall back to HTML (Strategy E).

### Strategy C: Grep llms-full.txt (for keyword-specific searches)

Use when:
- You need exact matches (function names, error codes, specific terms).
- MCP isn't available.
- You want to see all occurrences of a term.

```bash
curl -s "https://docs.example.com/llms-full.txt" | grep -C 3 "your-search-term"
```

### Strategy D: Load full content (for comprehensive understanding)

Use when:
- You need complete context about a library or API.
- `llms-full.txt` is small enough (< 15k tokens recommended).
- You're doing extensive work that references many parts of the docs.

**Always check length first:**
```bash
curl -sI "https://docs.example.com/llms-full.txt" | grep -i content-length
```

If the file is too large, consider:
- Loading specific files identified from llms.txt instead.
- Using MCP search for specific topics.
- Loading in chunks as needed.

### Strategy E: View HTML page (for exploration and navigation)

Use when:
- You need to understand the documentation structure.
- The user needs to navigate or click through the docs.
- You want to see diagrams, interactive examples, or formatted content.

HTML pages provide navigation menus, interactive code, diagrams, and links to related topics.

**Watch for truncation.** Pages over ~150,000 characters may get cut off. If a page seems incomplete, try the `.md` URL variant or look for section-specific files in llms.txt.

## Common patterns

### Pattern: Research before implementation

1. Fetch llms.txt to understand documentation scope.
2. Set up MCP if available.
3. Use MCP search for your specific questions.
4. Load relevant sections as needed.
5. Keep MCP connected for follow-up questions during implementation.

### Pattern: Debugging with docs

1. Search for the exact error message or code using grep.
2. If no results, use MCP search with a description of the problem.
3. Load the relevant section for full context on the solution.

### Pattern: Learning a new library

1. View the HTML landing page to understand structure.
2. Load llms-full.txt if small enough, or use section-specific files.
3. Set up MCP for ongoing reference during development.

### Pattern: Quick reference lookup

1. MCP search with the function or method name.
2. Or grep llms-full.txt for exact matches.

## Tips for efficiency

1. **Prefer MCP for Mintlify sites** — semantic search is more efficient than loading and parsing raw text.
2. **Cache strategically** — if you'll reference the same docs repeatedly, loading llms-full.txt once may be more efficient than multiple MCP searches.
3. **Use section files** — if llms.txt links to section-specific files (like `api/llms.txt`), load only what you need.
4. **Parallel MCP searches** — when working with multiple doc sources, search them in parallel rather than sequentially.

## Handling edge cases

### No llms.txt available

Fall back to:
1. Check if there's an MCP endpoint anyway.
2. Try `.md` URL variants of specific pages you need.
3. Use WebFetch to read specific documentation pages.
4. Search the web for the documentation.

### Very large documentation sets

For docs over 15k tokens:
1. Use MCP search instead of loading the full file.
2. Load section-specific files as needed.
3. Ask the user which areas are most relevant.

### Page not found (404)

If a page 404s:
1. Check the 404 page for links to relevant content.
2. Check llms.txt for the current URL — it reflects the live site structure.
3. Search the MCP with the page topic to find where the content moved.
4. Note to the user that the content may have moved and provide the updated URL.

### Outdated or conflicting information

If docs seem outdated:
1. Check for version indicators in the docs.
2. Note the discrepancy to the user.
3. Suggest checking the changelog or release notes.
