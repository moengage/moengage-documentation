# Backup: Flow Analytics APIs removed from review surface

**Branch:** `add/flows-api-docs`
**Removed on:** 2026-07-16
**Reason:** Per PM (Lokesh) sync-up call — temporarily exclude the 2 analytics-based
Flow APIs from the current review so Rajesh reviews only the 4 core Flow APIs. The
analytics APIs are a planned quick follow-up.

## Important: nothing was deleted from the spec

The 2 analytics endpoints are **still fully present in `api/flows/flows.yaml`**
(paths, schemas, examples). They were only removed from navigation and the overview
page. To bring Flow Analytics back, re-apply the three pieces below — no spec work needed.

The 2 analytics endpoints:
- `GET /v5/flows/{flow_id}/analytics`
- `GET /v5/flows/{flow_id}/analytics/channels/{channel}`

---

## Restore step 1 — `docs.json` (re-add the nav group)

In the API tab, inside the `"group": "Flows"` block (icon `diagram-project`), the
`pages` array currently ends with the core-Flows openapi group. Add the
**Flow Analytics** group back as a sibling, immediately after the core Flows group
object. The `pages` array should look like this:

```json
                "pages": [
                  "api/flows/flows-overview",
                  {
                    "group": "Flows",
                    "openapi": {
                      "source": "/api/flows/flows.yaml",
                      "directory": "api"
                    },
                    "pages": [
                      "POST /v5/flows/search",
                      "GET /v5/flows/{flow_id}",
                      "GET /v5/flows/{flow_id}/versions/{version_id}",
                      "PATCH /v5/flows/{flow_id}/status"
                    ]
                  },
                  {
                    "group": "Flow Analytics",
                    "openapi": {
                      "source": "/api/flows/flows.yaml",
                      "directory": "api"
                    },
                    "pages": [
                      "GET /v5/flows/{flow_id}/analytics",
                      "GET /v5/flows/{flow_id}/analytics/channels/{channel}"
                    ]
                  }
                ]
```

(i.e. add the comma after the core Flows group's closing `}` and paste the
`"group": "Flow Analytics"` object.)

---

## Restore step 2 — `api/flows/flows-overview.mdx` (re-add analytics references)

### 2a. Frontmatter `description`
Change:
```
description: "List, read, and control MoEngage Flows."
```
back to:
```
description: "List, read, and control MoEngage Flows, and retrieve flow and channel analytics."
```

### 2b. Intro paragraph (first line after frontmatter)
Change:
```
Use the Flows endpoints to discover flows, view a single flow (including its versions and stages), and change a flow's status. These endpoints read and control flows; they do not create them.
```
back to:
```
Use the Flows endpoints to discover flows, view a single flow (including its versions and stages), change a flow's status, and retrieve analytics. These endpoints read and control flows; they do not create them.
```

### 2c. Restore the "Endpoint groups" section
It was removed entirely. Re-add it **above** the `## Endpoints` heading:
```
## Endpoint groups

The Flows API has two endpoint groups:

| Endpoint group | Purpose |
| --- | --- |
| **Flows** | Search flows, get a single flow (or a specific version) with its stages, and change a flow's status. |
| **Flow Analytics** | Retrieve flow-level trip analytics and channel-level performance and delivery analytics. |

```

### 2d. Endpoints table — re-add the 2 analytics rows
Append these two rows to the end of the `## Endpoints` table:
```
| `GET` | `/v5/flows/{flow_id}/analytics` | Get flow-level trip, drop/exit, split-stage, and conversion analytics. |
| `GET` | `/v5/flows/{flow_id}/analytics/channels/{channel}` | Get channel-scoped aggregated and per-campaign analytics. |
```

### 2e. Authentication section — restore analytics mention
Change:
```
- **View** (`campaigns:view`) for the read endpoints — Search Flows, Get a Single Flow, and Get a Specific Version of a Flow.
```
back to:
```
- **View** (`campaigns:view`) for the read endpoints — Search Flows, Get a Single Flow, Get a Specific Version of a Flow, and the analytics endpoints.
```

### 2f. FAQs — restore the "Flow Analytics" FAQ group
The `## FAQs` section currently has a single `AccordionGroup` (the Flows FAQs) with no
`### Flows` subheading. Restore the `### Flows` subheading above that group, and re-add
the `### Flow Analytics` group after it:

```
### Flows

<AccordionGroup>
  ... (existing Flows accordions stay here) ...
</AccordionGroup>

### Flow Analytics

<AccordionGroup>
  <Accordion title="What time range do the analytics endpoints cover?">
    By default, the last 90 days or since the flow was first published, whichever is shorter. You can narrow the window with `activity_after` and `activity_before`. The filter is based on activity, not entry — a user journey is included if any activity happened within the window.
  </Accordion>
  <Accordion title="Which attribution models are available?">
    `VIEW_THROUGH`, `CLICK_THROUGH`, `IN_SESSION`, `TOTAL_CONVERSIONS`, and `CLICK_CONVERSIONS`. Pass the model you want in the `attribution_type` parameter.
  </Accordion>
  <Accordion title="Why is the flow-level analytics split from channel analytics?">
    A flow can contain many campaign nodes across several channels. Splitting flow-level metrics from channel-level metrics keeps each response focused and its response time predictable.
  </Accordion>
</AccordionGroup>
```

---

## Restore step 3 — validate

Run `mint validate` after restoring. (Note: a pre-existing, unrelated warning about
`/components/ProfileCalculator.jsx` importing `react` is expected and not caused by
these files.)
