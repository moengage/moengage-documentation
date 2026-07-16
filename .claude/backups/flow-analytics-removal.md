# Backup: Flow Analytics APIs removed from the Flows API docs

**Branch:** `add/flows-api-docs`
**Removed on:** 2026-07-16
**Reason:** Per PM (Lokesh) sync-up call — the current review covers only the 4 core Flow
APIs. Analytics APIs must NOT be part of this review. They are a planned quick follow-up.

## The 2 analytics endpoints removed
- `GET /v5/flows/{flow_id}/analytics`
- `GET /v5/flows/{flow_id}/analytics/channels/{channel}`

## Where the full analytics content lives (for restore)

Analytics was **fully removed** from all three files (spec paths + schemas + parameters,
navigation, and overview references). The complete, working analytics content is preserved
in git at commit **`57cba0982`** (the commit right before removal, where `flows.yaml` still
had everything).

To see exactly what was removed:

```bash
git show 57cba0982:api/flows/flows.yaml            # full spec incl. analytics
git show 57cba0982:api/flows/flows-overview.mdx    # overview incl. analytics refs
git show 57cba0982:docs.json                       # nav incl. Flow Analytics group
git diff 57cba0982 HEAD -- api/flows docs.json     # the exact removal diff
```

## How to restore (when PM says bring analytics back)

The analytics parts removed from each file:

1. **`api/flows/flows.yaml`** — re-add:
   - The 2 analytics **paths** (`/v5/flows/{flow_id}/analytics` and
     `/v5/flows/{flow_id}/analytics/channels/{channel}`).
   - The analytics **parameters**: `ActivityAfter`, `ActivityBefore`, `AttributionType`,
     `MetricType`, `ChannelEnum`.
   - The analytics **schemas**: `FlowAnalyticsResponse`, `FlowAnalyticsData`, `SummaryEntry`,
     `TripStats`, `ConversionGoalStat`, `ConversionMetrics`, `DropStatsEntry`, `ReasonCount`,
     `SplitStageStats`, `SplitStage`, `BranchStat`, `FlowChannelAnalyticsResponse`,
     `FlowChannelAnalyticsData`, `AggregatedChannelStats`, `ChannelPerformance`,
     `ChannelDelivery`, `CampaignStat`.
   - The `info.description` bullets for the 2 analytics endpoints, the analytics rate-limit
     note, the "and the analytics endpoints" auth mention, and the two "Flow Analytics
     endpoints" request-id descriptions.

   Fastest path: pull these blocks straight from `git show 57cba0982:api/flows/flows.yaml`.

2. **`docs.json`** — re-add the `"group": "Flow Analytics"` openapi group inside the API-tab
   Flows group, listing the 2 analytics endpoint pages. (See it in
   `git show 57cba0982:docs.json`.)

3. **`api/flows/flows-overview.mdx`** — re-add: the analytics mention in `description` and the
   intro, the "Endpoint groups" section, the 2 analytics rows in the Endpoints table, the
   "and the analytics endpoints" auth line, and the "Flow Analytics" FAQ group. (See it in
   `git show 57cba0982:api/flows/flows-overview.mdx`.)

## After restoring
Run `mint validate`. (A pre-existing, unrelated warning about
`/components/ProfileCalculator.jsx` importing `react` is expected — not from these files.)
