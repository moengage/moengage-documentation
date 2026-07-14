---
name: review-sdk-changelog
description: Review MoEngage Android or iOS SDK changelog files from the perspective of a junior developer who reads them to decide whether to upgrade and what action to take. Covers upgrade decision clarity, content quality, formatting consistency, versioning accuracy, and link correctness for entries post-January 2025.
license: MIT
compatibility: MoEngage Mintlify docs repo. Targets developer-guide/release-notes/android-sdk.mdx and developer-guide/release-notes/ios-sdk.mdx.
metadata:
  author: MoEngage
  version: "0.1"
---

# Review SDK changelog files

This skill reviews `android-sdk.mdx` and `ios-sdk.mdx` under `developer-guide/release-notes/` from the perspective of a junior developer who:

- Reads the changelog before deciding whether to upgrade the SDK.
- Looks up links when a new feature or breaking change is mentioned.
- Scans quickly and relies on visual signals (badges, headings) to find what matters.
- Does not know which internal changes require action and which are safe to ignore.

## How to use this skill

Invoked via `/review-sdk-changelog <path-to-mdx-file>`. The file path is passed as an argument.

1. Read the file at the path provided. Focus on entries from January 2025 onwards — skip older entries.
2. Run through every checklist section below.
3. Group findings by severity:
   - **Blocking** — factually wrong, broken link, version number error, or missing information that would cause a failed upgrade.
   - **Content gap** — missing information a junior needs to decide whether to upgrade or take action.
   - **Style** — formatting, inconsistency, word choice that degrades scannability without blocking integration.
4. Present findings in that order. Include file path and line number for every blocking and style issue.

Never guess at correct SDK API names, version numbers, or default values. Mark uncertain items as unverified.

---

## The junior developer's core questions

Every changelog entry should answer at least one of these:

1. **Do I need to upgrade?** Is there a fix or feature I need?
2. **Will this break my code?** Are there API changes, deprecations, or behaviour changes?
3. **What do I need to do?** Is there a migration step, a new configuration, or no action required?
4. **Where do I learn more?** Is there a doc link for new features?

Flag any entry that answers none of these.

---

## Checklist

### 1. Upgrade decision clarity

Every entry must make it clear whether developer action is required.

- [ ] Entries that contain only internal changes (e.g., "Internal Improvements", "Internal fixes", "Internal bugfixes") explicitly state "No developer action required." If they don't, flag them — a junior cannot tell whether to act.
- [ ] Entries labelled "Improvements" that are actually fixes (or vice versa) are flagged. The badge/label must match the content category.
- [ ] "What's New" entries that introduce a new feature include either a doc link or a code snippet. A feature announcement with no actionable path is incomplete.
- [ ] Deprecation notices include:
  - The version in which the deprecated API will be removed (e.g., "will be removed in 11.0.0").
  - An approximate timeline or note about urgency (not just a version number in isolation).
  - A link to the migration guide or the replacement API documentation.
  - A `<Warning>` callout — not buried inside a "What's New" section.
- [ ] Breaking changes have a dedicated `<Warning>` or `<Danger>` callout before the entry's bullet list, not mixed in with improvements.

### 2. Fix descriptions — enough context to identify the issue

A fix entry should let a developer recognise whether they were affected.

- [ ] Fix descriptions name the observable symptom, not just the internal cause. "Fixed a crash when displaying a nudge via test push" is useful. "Internal fixes." is not.
- [ ] Fix descriptions that reference "specific build configurations", "certain OEMs", or "certain conditions" name those configurations, OEMs, or conditions when possible. If not known, say "affects all configurations" or "affected specific OEM builds — upgrade recommended".
- [ ] Fixes for regressions introduced in a specific previous version note which version introduced the regression (e.g., "Regression introduced in 14.04.02, fixed in 14.04.03").
- [ ] Fix entries that describe the same problem across multiple modules (e.g., WorkManager downgrade affecting Core, InApp, Push Amp) are grouped under a shared summary rather than repeating identical text four times.

### 3. "What's New" entries — completeness

- [ ] Every "What's New" or feature entry links to a developer guide page, not a Zendesk/help-centre URL (`/hc/en-us/...`). Help centre links require a login and are outside the developer docs.
- [ ] New APIs introduced in a "What's New" entry include the API name or method signature in the description, or link to a page that shows it. A feature name alone ("Added support for Custom Proxy Domain") is not enough for a developer to start integrating.
- [ ] "What's New" entries that span multiple modules (e.g., "Updates to support Custom Proxy Domain" repeated across `richNotification`, `cards-ui`, `pushkit`) are consolidated into one entry with a list of affected modules, rather than duplicated verbatim.

### 4. Badge / tag consistency

Changelogs use coloured badges to categorise changes. Inconsistency here breaks the visual scanning pattern a junior relies on.

#### Android SDK
- [ ] All badge labels use one of exactly three categories: **What's New**, **Improvements**, **Fixes**. No other labels (e.g., "Deprecations" should be a sub-section under Fixes, not a separate badge colour).
- [ ] All badges use the same component implementation. The file must not mix raw `<span style={{...}}>` implementations with `<Badge>` components across different releases. Pick one and apply it to all 2025+ entries.
- [ ] The colour values are consistent across all entries. Flag any release that uses a hex value that differs from the established set:
  - What's New / Improvements: green family
  - Fixes: amber/orange family
- [ ] No entry uses an "Improvements" badge (green) to describe a fix, or a "Fixes" badge (orange) to describe an internal improvement.

#### iOS SDK
- [ ] All 2025+ entries use `<Badge>` components, not raw `<span style={{...}}>`. Entries from 2026 currently use `<span>` while 2025 entries use `<Badge>` — this inconsistency needs to be resolved.
- [ ] The Release Summary format is consistent across all 2025+ entries — either always `<Card title="Release Summary">` or always a bare `### Release Summary` heading. Not both.

### 5. Heading hierarchy

A junior developer relies on the heading structure to navigate a long page. Inconsistent heading levels break the table of contents and visual hierarchy.

#### Android SDK
- [ ] Release dates use `#` (H1) consistently for all 2025+ entries. Flag any date using `##` (H2) or lower.
- [ ] Module names within a release use `##` (H2) consistently. Flag any module using `###` (H3) in the same release block.
- [ ] The "Release Summary" heading inside the `<div>` wrapper uses `###` consistently. Flag any entry using `####`.
- [ ] "All Modules" section headings, when used, follow the same `##` level as individual module headings.

#### iOS SDK
- [ ] Release dates use `#` (H1) for all 2025+ entries.
- [ ] Module names use `##` (H2) for all 2025+ entries.
- [ ] No `<div style={{ marginTop: '8px' }}>` wrappers around single bullet points — use a standard Markdown bullet list instead.
- [ ] `<Badge>` followed by `\` (backslash line continuation) used for inline content — verify this renders correctly in Mintlify. If it creates a stray backslash, use a blank line + bullet instead.

### 6. Version number accuracy

- [ ] All module version numbers in release summaries match the `##` headings in the same release block. If the table lists `richNotification: 6.6.0`, the heading below must be `## Rich Notification 6.6.0` (or equivalent).
- [ ] Version numbers use consistent zero-padding within the file. `10.08.1` and `10.10.0` use different conventions in iOS SDK — choose one and apply consistently.
- [ ] BOM version numbers in the release summary table match the version in the BOM link href. A mismatch (e.g., cell shows `1.6.0` but link points to `bom-v2.0.0`) is a blocking error — developers following the link get the wrong BOM.
- [ ] Version numbers in module headings use a period between each segment: `4.4.0`, not `4.40` or `4.4`.
- [ ] Catalog version links and BOM version links go to the correct GitHub release tags. Spot-check at least the most recent two releases.
- [ ] Deprecated API removal version is stated as a concrete version number, not "a future release".

### 7. Module name consistency

The same module must be named identically across the entire file. A developer grepping for "RichNotification" will miss an entry logged as "richNotification" or "Rich Notification".

Common inconsistencies to check (applicable to both files):

| Module | Acceptable form | Flag if seen as |
|---|---|---|
| Core Android SDK | `Core SDK` | "Core MoE SDK", "moe-android-sdk", "All Modules" (when only Core changed) |
| Rich Notification | `Rich Notification` | "RichNotification", "richNotification" |
| Cards UI | `Cards UI` | "Cards ui", "cards-ui" |
| HMS Pushkit | `Pushkit` | "pushkit" |
| In-App (iOS) | `InApp` | "InApps" (inconsistent plural), "in-app" |
| Encrypted Storage | `Encrypted Storage` | "encryptedStorage" |

### 8. Internal links and external URLs

- [ ] All doc links use root-relative paths starting with `/developer-guide/` or `/user-guide/`. No absolute `https://www.moengage.com/docs/...` URLs.
- [ ] No links to Zendesk help-centre paths (`/hc/en-us/articles/...`). These require authentication and are outside the developer docs site.
- [ ] All internal paths use kebab-case. Flag PascalCase segments such as `Custom-Proxy-Domain-iOS` or `Push-Display-Handled-by-Application`.
- [ ] Links use root-relative paths without file extensions: `/developer-guide/android-sdk/push/...`, not `../push/...` or `.mdx` suffixes.
- [ ] Anchor links in cross-references (e.g., `#core-sdk-14-09-01`) match the actual heading slugs Mintlify generates from the entry headings. Heading `## Core SDK 14.09.01` generates slug `#core-sdk-14-09-01`.

### 9. Content completeness for new features

When a new feature is introduced, a junior developer needs to know whether it requires integration work.

- [ ] New features that require code changes or configuration say so explicitly. Features that work automatically say "No code changes required."
- [ ] New module introductions (e.g., `Personalize 1.0.0`) link to the getting-started guide for that module, not just to the module's overview.
- [ ] Features introduced in "What's New" that have prerequisites (minimum OS version, other SDK modules, backend configuration) list them inline or link to a page that does.

### 10. Date format

- [ ] All release dates in `#` headings use the same format. The established format for these files is ordinal long form: `# 6th May 2026`. Flag any entry using DD-MM-YYYY, abbreviated month names, or date-as-inline-bold-text.
- [ ] Ordinal suffixes are correct: 1st, 2nd, 3rd, 4th–20th, 21st, 22nd, 23rd, 24th–30th, 31st. Flag "05th" (should be "5th"), "21th" (should be "21st"), etc.

### 11. General writing quality

A junior developer reads changelog entries quickly and under pressure — they are deciding whether to block a release for an upgrade, or whether a production bug they're seeing is already fixed. Every word should earn its place.

#### Sentence structure

- [ ] Every entry is a complete sentence or a clear imperative phrase. Flag bare noun phrases and fragments:
  - Bad: `"Session trigger in-app not working."`
  - Bad: `"Border application fixes or resizable in-apps."`
  - Bad: `"Internal improvements."`
  - Good: `"Fixed an issue where session-triggered in-app messages were not displaying."`
  - Good: `"Fixed border rendering on resizable in-app messages."`
- [ ] Entries start with the subject of the change, not with "We", "MoEngage", or "The SDK":
  - Bad: `"MoEngage has optimized memory usage on app launch."`
  - Good: `"Optimized memory usage on app launch."`
  - Bad: `"We have introduced support for Custom Proxy Domains."`
  - Good: `"Added support for Custom Proxy Domains to route SDK traffic through a customer-owned subdomain."`
- [ ] Entries use past tense for fixes and past tense or present-tense noun phrases for new features:
  - Fixes: `"Fixed a crash when displaying a nudge via test push."` ✓
  - What's New: `"Added support for provisional push notifications."` ✓ or `"Support for provisional push notifications."` ✓
  - Avoid future tense in release notes: `"This will allow clients to..."` → `"Allows clients to..."`

#### Passive voice

- [ ] Passive constructions that obscure what changed are rewritten actively:
  - Bad: `"A blank notification was shown on certain OEMs upon clicking the last notification."`
  - Good: `"Fixed a blank notification shown on Samsung and Xiaomi devices when tapping the last notification in a group."`
  - Bad: `"Sticky notification with notification id not removed on dismiss click."`
  - Good: `"Fixed sticky notifications not being dismissed when the user taps the dismiss button."`
- [ ] Passive is acceptable when the subject genuinely does not matter: `"Replaced usage of APIs deprecated in iOS/tvOS 13."` is fine — the agent is clear from context.

#### Vague language

Flag each of the following patterns with a suggested rewrite:

- [ ] **"Certain"** without specification: `"certain OEMs"`, `"certain build configurations"`, `"certain conditions"`. Replace with the specific OEM, configuration, or condition if known. If not known, say `"some devices"` or `"some build configurations — upgrade recommended if affected"`.
- [ ] **"Some"** without context: `"Fixed an issue where some constants were causing unresolved errors."` — Which constants? Which error message would a developer see? If the error message is known, include it: `"Fixed 'Unresolved reference: X' build errors caused by missing constant declarations."`
- [ ] **"Updates to support X"** — describes the means, not the outcome: `"Updates to support Custom Proxy Domain."` → `"Updated to route network traffic through Custom Proxy Domains when configured."` or simply `"Added Custom Proxy Domain support."` Flag this pattern in every module that repeats it verbatim.
- [ ] **"Improvements"** without saying what improved: `"Internal improvements."` is never acceptable in a published changelog. Either name what improved (`"Reduced app launch time by removing redundant initialisation calls."`) or omit the entry entirely.
- [ ] **"Fixed issues"** (plural, unnamed): `"Fixed click and lifecycle callback execution issues."` → `"Fixed cases where click callbacks and lifecycle events were not fired when an in-app message was dismissed by the user."`
- [ ] **"Allowing clients to..."** — "clients" is MoEngage's word for customers, not for developers. Use "you" or restructure: `"Allowing clients to customize the MoEngage Webview in HTML InApps."` → `"Added an API to customise the WebView used in HTML in-app messages."`

#### Link anchor text

- [ ] `"refer [here](...)"` → use the page or feature name as the anchor text:
  - Bad: `"For more information, refer [here](/developer-guide/...)."`
  - Good: `"For more information, see [Custom Proxy Domain setup](/developer-guide/...)."`
  - Good: `"For setup instructions, see [Self-Handled In-Apps](/developer-guide/...)."`
- [ ] `"refer to the doc"` with no link is always flagged as a content gap (missing link), not just a style issue.
- [ ] Anchor text that repeats the URL path (e.g., `"[/developer-guide/android-sdk/push]"`) should be replaced with a human-readable label.

#### Capitalisation and terminology

- [ ] API and method names are in backticks: `logNotificationClicked`, `getSelfHandledInApps()`, `initializeDefaultInstance`. Plain text references to code identifiers are flagged.
- [ ] Feature names use consistent capitalisation matching the MoEngage product name:
  - `In-App` (hyphenated, title case) — not `in-app`, `InApp`, or `In App` in prose.
  - `Push Amplification` — not `push amp` or `push-amp` in prose (though `push-amp` is the module identifier).
  - `Cards` — not `cards` when referring to the product feature.
- [ ] SDK module names in prose use the form established in the Module Status Legend, not the Gradle artifact ID.

#### What's New entries — phrasing standards

"What's New" entries announce a feature a developer can now use. They follow a consistent structure:

```
<Feature name>: <One-sentence description of what it does and why a developer would use it>. For more information, see [<Guide name>](<link>).
```

Examples:
- Good: `"Custom Proxy Domain: Route SDK network traffic through a customer-owned subdomain to bypass ad blockers and private DNS filters. For setup, see [Custom Proxy Domain](/developer-guide/ios-sdk/sdk-integration/advanced/custom-proxy-domain-ios)."`
- Bad: `"Custom Proxy Domain: Introduced support for Custom Proxy Domains to route SDK traffic through a customer-owned subdomain for bypassing ad blockers and private DNS services."` — "Introduced support for" is padding; start with what it does.
- Bad: `"Updates to support Custom Proxy Domain."` — This describes a dependency bump, not a feature available to developers.

Flag entries that:
- Lead with `"Introducing..."`, `"Introduced support for..."`, or `"Added support for..."` — these can be cut to start with the feature name directly.
- Do not explain the developer benefit in one sentence.
- Have no link for a feature that requires integration.

#### Fixes entries — phrasing standards

Fix entries follow this structure:

```
Fixed <what was broken> <when/condition>. [No action required. / Upgrade recommended if you observe <symptom>.]
```

Examples:
- Good: `"Fixed a crash that occurred when an in-app nudge was displayed via a test push notification. Upgrade recommended if you use test push."`
- Good: `"Fixed sticky notifications with a custom ID not being removed when the dismiss button was tapped."`
- Bad: `"Fixed click and lifecycle callback execution issues."` — No symptom, no condition, no action guidance.
- Bad: `"Resolved an issue."` — Names nothing.

Flag entries that:
- Use `"Resolved an issue where..."` — prefer `"Fixed..."` for brevity.
- Describe the internal cause (`"WorkManager dependency version mismatch"`) without the developer-visible symptom (`"Kotlin compilation error when building with AGP 8.x"`).
- Do not tell the developer whether they need to act.

#### Deprecation entries — phrasing standards

Deprecation entries are the highest-stakes entries in a changelog for a junior developer — they signal future breaking changes. They must be unambiguous.

```
Deprecated: `<OldMethod()>` is deprecated and will be removed in <version> (<estimated date>). Use `<NewMethod()>` instead. See [Migration guide](<link>).
```

Examples:
- Good: `"Deprecated: \`getSelfHandledInApp(context, SelfHandledAvailableListener)\` is deprecated and will be removed in 11.0.0 (estimated Q3 2026). Use \`getSelfHandledInApp(context, SuccessCallback, FailureCallback)\` instead. See [Self-Handled In-Apps](/developer-guide/android-sdk/in-app-messages/in-app-nativ)."`
- Bad: `"All listener-based APIs for self-handled In-Apps are now deprecated and will be removed in version 11.0.0. We recommend migrating to the new Success/Failure callback-based APIs."` — "We recommend" is weak; the removal is mandatory, not a recommendation.

Flag entries that:
- Say `"We recommend migrating"` for a mandatory breaking change — use `"Migrate before upgrading to <version>"`.
- List deprecated APIs in a table but have no inline code formatting on the method names.
- Give a removal version without an estimated date or sprint.
- Have no link to migration guidance.

---

## Common patterns to flag

Drawn from observed issues across both files.

| Pattern | What to check |
|---|---|
| "Internal Improvements." / "Internal fixes." | No developer value. Replace with "No developer action required" or remove. |
| "Updates to support X." (repeated per module) | Consolidate into one entry listing all affected modules. |
| `<span style={{...}}>` badge | Replace with `<Badge>` component. Flag hex colour inconsistencies. |
| "Fixes" badge on "Improvements" content | Badge label must match entry category. |
| `## 11th December 2025` (H2 date) | Dates must be H1. |
| `#### Release Summary` | Must be `### Release Summary`. |
| `4.40` version number | Missing decimal point — should be `4.4.0`. |
| BOM cell version ≠ BOM link version | Blocking: developer follows link and lands on wrong release. |
| `/hc/en-us/articles/...` link | Replace with `/developer-guide/...` root-relative link. |
| `https://www.moengage.com/docs/...` link | Replace with root-relative path. |
| PascalCase in link path | Normalise to kebab-case. |
| "refer [here]" | Replace with descriptive anchor text: "see [Feature Name](link)". |
| "refer to the doc" with no link | Content gap — add the link. |
| `<div style={{ marginTop: '8px' }}>` around a single bullet | Use a plain Markdown bullet. |
| Deprecation inside "What's New" | Move to `<Warning>` callout with removal version + migration link. |
| "will be removed in X.0.0" with no timeline | Add estimated date or sprint/release cycle note. |
| "We recommend migrating" for a mandatory breaking change | Replace with "Migrate before upgrading to X.0.0". |
| `\` line continuation after `<Badge>` | Verify Mintlify renders this without a stray backslash. |
| "05th", "21th" | Fix ordinal suffix. |
| Version number zero-padding inconsistency | Pick one convention and apply consistently across the file. |
| Sentence fragment as entry | Rewrite as a complete sentence starting with "Fixed" or the feature name. |
| "MoEngage has..." / "We have..." | Remove subject — start with the verb: "Optimized...", "Added...". |
| "Certain OEMs" / "certain conditions" | Name the specific OEM or condition, or say "upgrade recommended if affected". |
| "Updates to support X" (repeated per module) | Consolidate + rewrite: "Added X support." |
| "Improvements" with no specifics | Name what improved, or omit the entry entirely. |
| "Resolved an issue where..." | Replace with "Fixed..." for brevity. |
| API/method name in plain text | Wrap in backticks: `methodName()`. |
| "Introducing..." / "Introduced support for..." | Cut to the feature name: "Custom Proxy Domain: Routes SDK traffic through...". |
| "Allowing clients to..." | Replace "clients" with "you" or restructure: "Added an API to...". |

---

## Severity definitions

**Blocking** — Factually incorrect, broken link, version number that would cause a failed build or wrong dependency, or missing information that makes a feature announcement impossible to act on.

**Content gap** — Information a junior developer needs to decide whether to upgrade or to integrate a new feature, but cannot find in the entry.

**Style** — Formatting, naming, word choice, or consistency issues that degrade scannability without blocking a developer's work.

---

## Output format

```
## Blocking issues

### 1. <Short title> (line N)
<What is wrong and why it blocks a developer action.>

## Content gaps

### 1. <Short title> (line N or "throughout")
<What is missing and what a junior developer would need.>

## Style

### 1. <Short title> (line N)
<Specific fix: old text → new text, or description of the change needed.>
```

Always include line numbers for blocking and style issues. For content gaps that apply to a pattern throughout the file, state "throughout" instead of a single line number.
