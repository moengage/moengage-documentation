---
name: mintlify
description: Comprehensive reference for the Mintlify platform as used by the MoEngage docs site. Use when creating pages, configuring docs.json, adding components, setting up navigation, or working with API references. Routes to detailed reference files for all components and configuration options.
license: MIT
compatibility: The MoEngage docs site runs on Mintlify with docs.json at the repo root.
metadata:
  author: MoEngage (platform reference from Mintlify)
  version: "0.1"
---

# Mintlify reference for MoEngage docs

Reference for building documentation on the Mintlify platform that the MoEngage docs site runs on. This file covers essentials that apply to every task. For detailed reference on specific topics, read the files in the reference index below.

## Reference index

Read these files **only when your task requires them**. They live in `.claude/skills/mintlify/reference/` relative to the repo root.

| File | When to read |
|------|-------------|
| `reference/components.md` | Adding or modifying components (callouts, cards, steps, tabs, accordions, code groups, fields, frames, icons, tooltips, badges, trees, mermaid, panels, prompts, colors, tiles, updates, views). |
| `reference/configuration.md` | Changing `docs.json` settings (theme, colors, logo, fonts, appearance, navbar, footer, banner, redirects, SEO, integrations, API config). Also covers snippets, hidden pages, `.mintignore`, custom CSS/JS, and the complete frontmatter field table. |
| `reference/navigation.md` | Modifying site navigation structure (groups, tabs, anchors, dropdowns, products, versions, languages, OpenAPI in nav). |
| `reference/api-docs.md` | Setting up API documentation (OpenAPI, AsyncAPI, MDX manual API pages, extensions, playground config). |

## Before you start

Read the project's `docs.json` first. It defines the MoEngage site's navigation (tabs: Home, User Guide, Developer Guide, API Guide), theme, colors, and configuration.

Search for existing content before creating new pages. You may need to update an existing page, add a section, or link to existing content rather than duplicating.

Read 2-3 similar pages to match the site's voice, structure, and formatting.

## MoEngage project layout

```
moengage-documentation/
├── docs.json                  # Site configuration (required)
├── introduction.mdx
├── user-guide/                # Dashboard product docs (~1000 pages)
│   ├── campaigns-and-channels/
│   ├── flows-cross-channel-messaging/
│   ├── analyze/
│   ├── segment/
│   ├── content/
│   ├── data/
│   ├── ai-and-intelligence/
│   ├── personalize/
│   ├── decisioning/
│   ├── inform/
│   ├── settings/
│   ├── use-cases/
│   └── release-notes/YYYY/    # Monthly release notes
├── developer-guide/           # SDK integration docs
│   ├── ios/
│   ├── android/
│   ├── web/
│   ├── react-native/
│   ├── flutter/
│   ├── ...
│   └── release-notes/<sdk>/   # Per-SDK release notes
├── api/                       # REST API reference (OpenAPI)
├── release-notes/
├── images/                    # Screenshots and illustrations
├── snippets/                  # Reusable MDX components
└── style.css                  # Custom styles
```

`.mintignore` excludes `.claude/`, `.cursor/`, and `archive/` from the build.

### File naming

- Match existing patterns in the directory.
- Default to kebab-case: `getting-started.mdx`, `push-notifications.mdx`.
- Add new pages to `docs.json` navigation or they won't appear in the sidebar.

### Internal links

- Use root-relative paths without file extensions: `/user-guide/campaigns-and-channels/push/android-push/overview`.
- Do not use relative paths (`../`) or absolute URLs for internal pages.

### Images

Store images in the `images/` directory. Reference with root-relative paths. All images require descriptive alt text.

```mdx
![Campaign creation screen showing audience filter panel](/images/campaigns/audience-filter.png)
```

## Page frontmatter

Every MoEngage page requires `title`. Include `description` and (where useful) `keywords` for SEO.

```yaml
---
title: "Clear, descriptive title"
description: "Concise summary for SEO and navigation."
keywords: ["relevant", "search", "terms"]
---
```

### Common frontmatter fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Page title in navigation and browser tabs. |
| `description` | string | No (but expected) | Brief description for SEO. Displays under the title. |
| `sidebarTitle` | string | No | Short title for sidebar navigation. |
| `icon` | string | No | Lucide, Font Awesome, or Tabler icon name. Also accepts a URL or file path. |
| `tag` | string | No | Label next to page title in sidebar (for example, `"NEW"`). |
| `hidden` | boolean | No | Remove from sidebar. Page still accessible by URL. |
| `mode` | string | No | Page layout: `default`, `wide`, `custom`, `frame`, `center`. |
| `keywords` | array | No | Search terms for internal search and SEO. |
| `api` | string | No | API endpoint for interactive playground (e.g., `"POST /users"`). |
| `openapi` | string | No | OpenAPI endpoint reference (e.g., `"GET /endpoint"`). |

## Quick component reference

Below are the most commonly used components. For full props and all 24 components, read `reference/components.md`.

### Callouts

```mdx
<Note>Supplementary information, safe to skip.</Note>
<Info>Helpful context such as permissions or prerequisites.</Info>
<Tip>Recommendations or best practices.</Tip>
<Warning>Potentially destructive actions or important caveats.</Warning>
<Check>Success confirmation or completed status.</Check>
<Danger>Critical warnings about data loss or breaking changes.</Danger>
```

### Steps

```mdx
<Steps>
  <Step title="First step">
    Instructions for step one.
  </Step>
  <Step title="Second step">
    Instructions for step two.
  </Step>
</Steps>
```

### Tabs and code groups

```mdx
<Tabs>
  <Tab title="iOS">
    ```swift
    MoEngage.sharedInstance().initializeDefaultInstance(with: sdkConfig)
    ```
  </Tab>
  <Tab title="Android">
    ```kotlin
    MoEngage.initialiseDefaultInstance(moEngage)
    ```
  </Tab>
</Tabs>
```

```mdx
<CodeGroup>

```javascript Node.js
const response = await fetch('/api/v1/user/add', {
  headers: { Authorization: `Basic ${token}` }
});
```

```python Python
import requests
response = requests.post('/api/v1/user/add',
  headers={'Authorization': f'Basic {token}'})
```

</CodeGroup>
```

### Cards and columns

```mdx
<Columns cols={2}>
  <Card title="Getting Started" icon="rocket" href="/user-guide/getting-started">
    Set up MoEngage for your account.
  </Card>
  <Card title="Send your first campaign" icon="send" href="/user-guide/campaigns-and-channels">
    Create and launch a campaign in minutes.
  </Card>
</Columns>
```

Use `<Columns>` to arrange cards (or other content) in a grid. `cols` accepts 1-4.

### Accordions

```mdx
<AccordionGroup>
  <Accordion title="First section">Content one.</Accordion>
  <Accordion title="Second section">Content two.</Accordion>
</AccordionGroup>
```

## CLI commands

- `npm i -g mint` — Install the Mintlify CLI.
- `mint dev` — Local preview at localhost:3000.
- `mint broken-links` — Check internal links.
- `mint a11y` — Check for accessibility issues.
- `mint validate` — Validate documentation builds, including OpenAPI specs.
- `mint upgrade` — Upgrade from `mint.json` to `docs.json`.

## Writing standards

- Second-person voice ("you").
- Active voice, direct language.
- Title case for headings ("Getting Started", not "Getting started").
- Title case for code block titles.
- All code blocks must have language tags.
- All images must have descriptive alt text.
- No marketing language, filler phrases, or emoji.
- Keep code examples simple, practical, and tested.

Full MoEngage writing rules live in `.cursor/rules/writing-rules.mdc`.

## Common mistakes

- Missing language tag on a code block (use ` ```python `, not ` ``` `).
- Using relative paths (`../page`) instead of root-relative (`/section/page`).
- Forgetting to add new pages to `docs.json` navigation.
- Images without alt text.
- Adding file extensions to internal links (`/page.mdx` instead of `/page`).
- Adding content to non-English sections of `docs.json` — translations are automated.
