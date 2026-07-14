---
name: review-android-sdk
description: Review Android SDK documentation from the perspective of a junior Android developer performing an integration for the first time. Covers integration correctness, code validity, navigation flow, deprecated APIs, and writing standards. Use when asked to review any page under developer-guide/android-sdk/.
license: MIT
compatibility: MoEngage Mintlify docs repo. Pairs with writing-rules.mdc and doc-author skill.
metadata:
  author: MoEngage
  version: "0.1"
---

# Review Android SDK documentation

This skill reviews documentation pages under `developer-guide/android-sdk/` from the perspective of a junior Android developer (1–2 years experience, familiar with Kotlin/Java and Gradle, but integrating a third-party analytics SDK for the first time).

## How to use this skill

This skill is invoked via `/review-android-sdk <path-to-mdx-file>`. The page path is passed as an argument.

1. Read the file at the path provided.
2. Identify which integration area the page covers: SDK setup, data tracking, push notifications, in-app messages, cards, compliance, or migration.
3. Run through every checklist section below.
4. Group findings by severity: **Blocking** (prevents integration or causes a build/runtime failure), **Content gap** (missing information a junior developer needs to proceed), **Style** (writing standards and formatting).
5. Present findings in that order, with file path and line number for each issue.

Never guess at the correct SDK API, class name, or default values. Mark uncertain items as unverified rather than inventing them.

---

## Integration area orientation

Android SDK documentation covers several distinct integration layers. Know which one a page targets and verify the page makes this clear.

| Area | Key files a developer edits | Common tools |
|---|---|---|
| SDK setup | `build.gradle` / `build.gradle.kts`, `Application.kt`, `AndroidManifest.xml` | Android Studio, Gradle |
| Data tracking | `Application.kt`, Activity/Fragment files | — |
| Push (FCM) | `build.gradle`, `google-services.json`, `Application.kt`, `AndroidManifest.xml` | Firebase Console |
| In-app messages | `Activity` / `Fragment` files, `build.gradle` | — |
| Cards | `Activity` / `Fragment` files, `build.gradle` | — |
| Compliance / opt-out | `Application.kt` | — |
| Migration | `build.gradle`, `Application.kt`, `AndroidManifest.xml` | — |

**Flag any page that references a class, method, or module without first telling the reader which dependency to add.** A junior developer has no way to resolve an unknown symbol without that context.

---

## Checklist

### 1. Frontmatter

- [ ] `title` is present and in title case ("Configure Push Notifications", not "Configure push notifications").
- [ ] `description` is present and summarises the page purpose in one sentence.
- [ ] `keywords` is present when the page covers terms that readers might search for but that do not appear in `title` or `description`.

### 2. Prerequisites

- [ ] A prerequisites block appears before any procedural steps.
- [ ] The block specifies the **minimum SDK version** required (e.g., "MoEngage Android SDK 13.6.00 or above").
- [ ] The block lists the prior pages that must be completed first — for example, push pages must require SDK initialization; in-app and cards pages must require SDK initialization and the relevant module dependency.
- [ ] If a feature requires a specific third-party library (Glide, Firebase, etc.), that requirement appears in prerequisites, not buried mid-section. A missing prerequisite that causes a runtime crash is a **Blocking** issue.
- [ ] The prerequisites block does not mix post-integration notes (expected behaviors, verification tips) with setup requirements.

### 3. Dependency and Gradle instructions

These are the most common source of copy-paste errors for a junior Android developer.

- [ ] Every new class or API introduced on the page has its Gradle dependency shown **before** the first code snippet that uses it. If the dependency was shown on a previous page, the page links to that page rather than leaving the reader to guess.
- [ ] Gradle snippets specify which file they belong in: project-level `build.gradle` / `settings.gradle` vs app-level `build.gradle`. "Add to `build.gradle`" without a path is always ambiguous — flag it.
- [ ] Kotlin DSL (`.kts`) and Groovy DSL snippets are either shown in separate tabs or the page explicitly says which one it is using. Mixing them in the same block is a build error.
- [ ] The page is consistent with the project-wide preference for BOM-based dependency declarations. If a page shows a version number inline instead of using the BOM, it either explains why or links to the BOM page.
- [ ] No dependency uses the deprecated `compile` directive. Flag any occurrence and replace with `implementation`.
- [ ] Version placeholders like `<version>` or `x.y.z` are explicitly labeled as placeholders and include a link to the release notes where the current version can be found.
- [ ] The `allprojects { repositories {} }` pattern in project-level `build.gradle` is flagged: projects created with Android Studio Flamingo or later use `settings.gradle` for repository declarations, not `allprojects`.

### 4. Code validity

Junior developers copy SDK code snippets directly into their projects. Every snippet must be immediately compilable.

- [ ] Kotlin snippets include the correct import statements, or the page explicitly states "add this import" above the snippet. Classes like `ProjectConfig`, `MoEAnalyticsHelper`, `StorageSecurityConfig`, and `NetworkRequestConfig` are not in the standard Android library — missing imports cause unresolved-symbol errors.
- [ ] Java snippets include the correct import statements. Java does not infer imports from context; what works in Kotlin (with IDE auto-import) still requires an explicit import in a documentation snippet.
- [ ] Code blocks tagged `java` contain Java syntax, not Kotlin. Flag any Kotlin constructor syntax (e.g., `Intent(ACTION_X)`) or Kotlin-specific APIs in Java blocks.
- [ ] Code blocks tagged `kotlin` contain Kotlin syntax, not Java.
- [ ] Code blocks tagged `xml` contain XML, not Kotlin or Java.
- [ ] Code blocks tagged `javascript` or `js` do not contain Android/Kotlin/Java code.
- [ ] Method calls show all required arguments. A stub like `setFirstName()` with no arguments will not compile — show the actual signature: `setFirstName(context, "value")`.
- [ ] No syntactically invalid placeholders inside method calls, such as `MoEngage.Builder(application, , )` with empty arguments. Use a named placeholder in a comment or angle-bracket notation: `MoEngage.Builder(application, "<APP_ID>", "<DATA_CENTER>")`.
- [ ] Type lists for user attributes (custom event properties, user attribute values) are accurate for Android/Kotlin/Java. Types such as `List<int>`, `List<num>`, and `num` are Dart/Flutter types and must not appear in Android documentation.
- [ ] All code blocks have a language tag. A block without a language tag gets no syntax highlighting — flag it.

### 5. API currency

- [ ] The page does not reference deprecated APIs without clearly marking them as deprecated and providing the replacement.
  - `setUniqueId()` → replaced by `identifyUser()` since SDK 13.6.00
  - `NudgeView` embedded in Activities → deprecated since InApp SDK 7.0.0; use `showNudge()` instead
  - `compile` Gradle directive → replaced by `implementation` since Gradle 3.0
  - Mi Push (Xiaomi) → discontinued; Mi-specific configuration steps should be removed or marked as legacy
- [ ] Version numbers cited as "the latest version" or "2.x.xx or later" are replaced with specific version numbers or a link to the release notes. "Latest" is a moving target and becomes incorrect the moment a new version ships.
- [ ] If a page covers behavior that changed in a specific SDK version, a version callout is present at the top of the relevant section: "Starting from SDK version X.Y.Z, …"

### 6. Java and Kotlin parity

- [ ] If a page targets Java as well as Kotlin (indicated by tabs or dual blocks), every code example has both a Kotlin and a Java version. A Java-only developer who sees a Kotlin-only snippet cannot proceed.
- [ ] Both language versions are functionally equivalent — the same API calls, the same order of operations. Flag any case where the Java version has extra calls absent from the Kotlin version (or vice versa) without explanation.

### 7. Registration location for callbacks and listeners

Android has a strict lifecycle model. Registering in the wrong place means callbacks fire when the listener is not set up.

- [ ] Any listener or callback that can fire when the app is in the background (push callbacks, auth listeners, geofence events) has an explicit note to register it in `Application.onCreate()`, not in an `Activity` or `Fragment`.
- [ ] If registration must happen after SDK initialization, the page says so and shows the correct relative order of calls.

### 8. Integration sequence and navigation

- [ ] If the page is part of a multi-page integration flow (SDK setup, push setup, etc.), it includes a "Next step" pointer at the bottom that links to the logically next page.
- [ ] If the page is not the starting point of a flow, it includes either a prerequisites section or a "Before you begin" link to the page that must be completed first.
- [ ] The page does not end abruptly on a table, a code block, or a dependency list with no summary or pointer to what comes next.
- [ ] Where the page says "follow the steps described in [X]", the steps it references actually exist on the linked page. Broken cross-references are a **Blocking** issue.

### 9. Duplicate and conflicting content

- [ ] If a topic (data center configuration, advertising ID tracking, Glide version) is covered on more than one page, the pages are consistent and cross-linked. Contradictory information between pages — especially version numbers — is a **Blocking** issue.
- [ ] If a page repeats the same installation section multiple times (once per feature variant, for example), the page says "skip this if you already added the dependency" to prevent duplicate Gradle entries.

### 10. Checklist and release guide currency

When reviewing `checklist/release-checklist.mdx` or any page that serves as an integration checklist:

- [ ] No checklist item references a deprecated API (see section 5).
- [ ] No checklist item references a discontinued third-party service (Mi Push / Xiaomi).
- [ ] Checklist items for optional modules (Push Amplification Plus, Huawei HMS) are clearly labeled as optional.
- [ ] Each checklist item maps to an existing, reachable documentation page.

### 11. Troubleshooting pages

- [ ] Troubleshooting steps for one platform (iOS, React Native, Flutter) do not appear in the Android troubleshooting pages without a clear platform label.
- [ ] All quoted error messages, log lines, and exception names are accurate. A typo in an error message string makes it unsearchable.
- [ ] Steps that describe a fix do not accidentally invert the condition — "the SDK is synced" instead of "the SDK is NOT synced" leads developers in the wrong direction.
- [ ] Performance numbers cited (e.g., "SDK initialization takes 10–15 ms") are consistent with the values on the `performance/sdk-performance.mdx` page.
- [ ] Links to third-party libraries or tools are official sources (GitHub org pages, official docs) — not personal forks or individual developer GitHub repos.

### 12. Migration pages

- [ ] The page has a version-range callout at the top that clearly states who needs to follow it: "Follow this guide if you are upgrading from SDK X.x.x to Y.y.y."
- [ ] Deprecated API tables use standard column headers: "Deprecated API" and "Replacement API" (not informal labels like "Then" and "Now").
- [ ] Migration steps refer to the correct target migration guide. A "10.x → 12.x" migration should not point to the 10→11 guide.
- [ ] Very old migration guides (4.x → 5.x era, GCM → FCM era) have a prominent callout at the top identifying the SDK age and whether it is still relevant for current integrations.

### 13. Internal links

- [ ] All internal links use root-relative paths starting with `/developer-guide/` or `/user-guide/`. No relative paths (`../`) and no absolute `https://www.moengage.com/docs/…` URLs.
- [ ] Links point to specific pages (`.mdx` files), not to directories. A link like `/developer-guide/android-sdk/data-tracking` resolves to a 404 unless a redirect or index page exists — flag it.
- [ ] Anchor links (e.g., `#step-3-configure-fcm`) match the actual heading slug Mintlify generates from the heading text.

### 14. Images

- [ ] Every image has descriptive `alt` text that explains what the image shows. Auto-generated or single-word alt text (`"Screenshot"`, `"Image"`, `"Step3"`) is not acceptable.
- [ ] Images that show dashboard UI reflect the current MoEngage dashboard design. Visibly outdated screenshots should be flagged.

### 15. Callout component usage

- [ ] `<Warning>` is used for steps that, if skipped, cause a build failure, runtime crash, or data loss. Using `<Info>` for these downgrades the urgency.
- [ ] `<Info>` is used for supplementary context, not for mandatory steps.
- [ ] `<Tip>` is used for best practices and optimizations — not prerequisites.
- [ ] No callout body starts with a redundant bold label like `**Warning:**` — the component's own header handles labeling.

### 16. Verification step

- [ ] After completing all integration steps, the page tells the reader how to verify the integration worked. Examples:
  - "Build and run the app — check logcat for `[MoEngage] SDK initialized successfully`."
  - "Trigger a test event and confirm it appears in the MoEngage dashboard under **Analyze > Events**."
- [ ] Troubleshooting guidance or a link to the relevant troubleshooting page is present for the most likely failure modes.

### 17. General writing standards

- [ ] Second-person voice throughout ("you", not "the developer" or "the user").
- [ ] Active voice. Flag passive constructions: "the listener must be registered" → "register the listener".
- [ ] "follow the below steps" → "follow these steps".
- [ ] No double negatives: "If you don't want the SDK not to track…" → "To prevent the SDK from tracking…"
- [ ] No marketing language: "powerful", "seamless", "robust", "easily", "simply".
- [ ] No filler phrases: "it's important to note", "in order to", "please note that".
- [ ] Title case for all headings, including the frontmatter `title`.

---

## Common patterns to flag

These issues appear repeatedly in Android SDK pages based on past reviews.

| Pattern | What to check |
|---|---|
| Missing `moe-push-firebase` dependency | Pages that use `MoEFireBaseHelper` or `MoEFireBaseMessagingService` must show the `moe-push-firebase` Gradle dependency before the first code snippet. |
| Glide prerequisite buried mid-page | Any in-app or cards page that requires Glide must state this in the prerequisites block, not mid-section. Runtime crashes caused by missing Glide produce a non-obvious error. |
| `cards-ui` missing from dependency block | Pages that reference `CardActivity` or `CardFragment` must include `cards-ui` in the Gradle dependency block, not just `cards-core`. |
| `DATA_CENTER_X` ambiguous placeholder | Placeholder values that look like real enum values (`DATA_CENTER_X`) must be replaced with `DATA_CENTER_<YOUR_REGION>` or explained with a comment. |
| Flutter/Dart types in Android docs | `List<int>`, `List<num>`, `num` are Dart types. Android/Kotlin equivalents are `IntArray`, `List<Int>`, `Double`, etc. |
| `setUniqueId()` in release checklist | This API was deprecated in SDK 13.6.00. All references must use `identifyUser()`. |
| `NudgeView` in integration steps or checklist | Deprecated since InApp SDK 7.0.0. References must use `showNudge()` instead. |
| Mi Push checklist items | Mi Push was discontinued. All Mi-specific steps must be removed or marked legacy. |
| `compile` directive in Gradle | Deprecated since Gradle 3.0 (2017). Replace all occurrences with `implementation`. |
| `allprojects` repository block | New projects (Android Studio Flamingo+) use `settings.gradle` for repository declarations. Flag `allprojects { repositories {} }` without a note. |
| `javascript` tag on Java code block | Java code blocks tagged `javascript` get wrong syntax highlighting. Tag must be `java`. |
| `text` tag on code blocks | Every code block needs a real language tag (`kotlin`, `java`, `xml`, `groovy`, `gradle`, `bash`). |
| Stale version numbers | Any version cited as "the latest" or as a specific number that appears older than the current SDK release — flag it and note that it may be stale. |
| Duplicate data center table | The data center ↔ `DataCenter` enum table appears on both `sdk-initialization.mdx` and `data-center.mdx` with different row counts. If reviewing either page, check consistency with the other. |
| Registration in Activity instead of Application | Listeners for push callbacks, authentication, and geofence events must be registered in `Application.onCreate()`. |
| Cross-platform troubleshooting bleed | React Native and Flutter FAQ items appearing in Android troubleshooting pages must be labeled or moved. |
| Step reference mismatch in migration guides | "Follow steps 1–4 on [linked page]" must be verified — those steps must actually exist at the link destination. |
| `build.gradle` without path qualifier | Always specify: project-level `build.gradle` (root) vs app-level `build.gradle` (under `app/`). |
| Page ends without next-step pointer | Integration flow pages (SDK setup, push setup, data tracking) must end with a link to the next page in the flow. |
| Conflicting Glide versions | `cards.mdx` and `in-app-nativ.mdx` have historically listed different Glide versions. When reviewing either, check consistency with the other. |

---

## Severity definitions

Use these consistently when reporting findings.

**Blocking** — Prevents the reader from completing the integration, causes a build error, runtime crash, or broken link. Examples: missing Gradle dependency, syntactically invalid code, broken cross-reference, prerequisite buried mid-page.

**Content gap** — Information a junior developer needs but cannot find on this page. The integration could fail silently or require significant guesswork. Examples: missing next-step pointer, no verification step, no explanation of where a method must be called, deprecated API used without marking it.

**Style** — Formatting, word choice, or convention issues. Does not block integration but reduces trust and consistency. Examples: typos, wrong language tag on a code block, double negation, passive voice.

---

## Output format

Present findings in this structure:

```
## Blocking issues

### 1. <Short title> (line N)
<What the issue is and why it blocks integration.>

## Content gaps

### 1. <Short title>
<What's missing and what a junior developer needs to proceed.>

## Style

### 1. <Short title> (line N)
<Specific fix: old text → new text, or description of change needed.>
```

Always include file path and line number for blocking and style issues. For content gaps that span the whole page, a line number is not required.
