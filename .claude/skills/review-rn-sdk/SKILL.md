---
name: review-rn-sdk
description: Review React Native SDK documentation for writing standards, technical accuracy, RN-specific usability, and Mintlify component correctness. Use when asked to review any page under developer-guide/react-native-sdk/.
license: MIT
compatibility: MoEngage Mintlify docs repo. Pairs with the general writing-rules.mdc and doc-author skill.
metadata:
  author: MoEngage
  version: "0.1"
---

# Review React Native SDK documentation

This skill reviews documentation pages under `developer-guide/react-native-sdk/` from the perspective of a junior React Native developer performing an integration for the first time.

## How to use this skill

This skill is invoked via `/review-rn-sdk <path-to-mdx-file>`. The page path is passed as an argument.

1. Read the file at the path provided.
2. Identify which platform layers the page covers (iOS native, Android native, JavaScript/TypeScript, or all three).
3. Run through every checklist section below.
4. Group findings by severity: **Blocking** (prevents integration or causes broken links/renders), **Content gap** (missing information a junior dev needs), **Style** (writing standards, formatting).
5. Present findings in that order, with file path and line number for each issue.

Never guess at the correct SDK API or default values. Mark uncertain items as unverified rather than inventing them.

---

## Platform-layer orientation

React Native apps have three distinct layers. Know which one a page is targeting and check that the page says so explicitly.

| Layer | Location in a project | Common tooling |
|---|---|---|
| JavaScript / TypeScript | `src/`, `App.tsx`, etc. | npm / Yarn, Metro |
| iOS native | `ios/<App>.xcworkspace` | Xcode, CocoaPods / SPM |
| Android native | `android/` | Android Studio, Gradle |

**Flag any page that touches the iOS or Android native layer without telling the reader to open that layer's IDE first.** A junior RN developer defaults to their code editor and will be confused by Xcode or Android Studio steps with no orientation.

---

## Checklist

### 1. Frontmatter

- [ ] `title` is present and in title case ("Set Up iOS Notification Extensions", not "Set up iOS notification extensions").
- [ ] `description` is present and summarises the page's purpose in one sentence.
- [ ] `keywords` is present when the page covers terms not already in `title` or `description`.

### 2. Prerequisites

- [ ] A prerequisites block appears at the top, before any procedural steps.
- [ ] The block specifies the **minimum SDK version** required (e.g., "React Native SDK 12.6.0 or above"). Version-gating is critical in SDK docs — missing it causes silent failures.
- [ ] The block lists any **other SDK pages** that must be completed first (e.g., file-based initialization, App Group configuration).
- [ ] If the page or section covers an iOS-native step, the prerequisites state that the reader must open `ios/<App>.xcworkspace` in Xcode.
- [ ] If the page or section covers an Android-native step, the prerequisites state that the reader must open the `android/` directory in Android Studio (or edit `android/` files directly).
- [ ] Prerequisite content is not mixed with post-integration behavior. For example, a "you may see a keychain prompt — click Always Allow" note belongs after the integration steps, not in a prerequisites callout.

### 3. Internal links

- [ ] All internal links use root-relative paths starting with `/developer-guide/` or `/user-guide/`. No relative paths (`../`) and no absolute `https://www.moengage.com/docs/...` URLs.
- [ ] Links are kebab-case and match the actual file path. RN SDK pages commonly copy links from iOS SDK pages — check that the path does not reference `/ios-sdk/` or `/sdk-integration/react-native/` when the file lives under `/developer-guide/react-native-sdk/push/basic/` or similar.
- [ ] Anchor links (e.g., `#step-5-additional-configuration-optional`) match the actual heading slug Mintlify generates. Headings with "(Optional)" appended generate slugs that include `-optional`.

### 4. Cross-references within the page

- [ ] Any phrase like "as described in Step N" or "from Step N" refers to the correct step **on this page**. Pages that were adapted from sibling docs (iOS SDK, Flutter SDK) often carry step numbers that no longer align.
- [ ] Options tables that reference step numbers (e.g., "`--enable-push-notification-templates` — Required if the content extension from Step 2 is used") use the step number from **this page**, not the source page.

### 5. CocoaPods / SPM steps — RN autolinking context

React Native autolinks many packages. An instruction to add `pod 'MoEngage-iOS-SDK'` to the Podfile may conflict with autolinking.

- [ ] When the CocoaPods tab shows a full `target 'YourApp' do … end` block, verify whether the main SDK pod is already autolinked by the React Native package. If it is, call out that only the additional subspec (e.g., `pod 'MoEngage-iOS-SDK/RichNotification'`) is new.
- [ ] The Podfile target name is the iOS app target name, not the RN project root. Clarify this for juniors who may not know the distinction.
- [ ] `pod repo update && pod install` is correct syntax; flag `pod repo update; pod install` or missing `&&`.

### 6. iOS-native steps (Xcode)

- [ ] Steps that happen in Xcode start with the IDE context: which project (`.xcworkspace`, not `.xcodeproj`), which target (app target vs extension target), and which tab (Build Phases, Signing & Capabilities, Build Settings).
- [ ] When the page instructs the reader to add a Run Script phase, it also states that **User Script Sandboxing must be disabled** (`ENABLE_USER_SCRIPT_SANDBOXING = No` in Build Settings). Missing this causes a "Permission Denied" build failure.
- [ ] Apple Developer portal links go to `https://developer.apple.com/account/resources/identifiers/list`, not to `idmsa.apple.com/IDMSWebAuth/signin?appIdKey=...` deep-links that may break or require active sessions.
- [ ] When an integrator tool or script creates extension targets automatically, the page states this explicitly: "The tool creates the target on first build — you do not need to add a target manually." Juniors who don't know this will try to create the target themselves and create conflicts.

### 7. Android-native steps

- [ ] Gradle snippets specify which file they go in: `android/build.gradle` (project-level) vs `android/app/build.gradle` (app-level). Ambiguous references to "the `build.gradle` file" are a common source of confusion.
- [ ] All Android file paths are relative to the RN project root, not the Android module root. Write `android/app/src/main/res/values/moengage.xml`, not `src/main/res/values/moengage.xml`.
- [ ] Permission entries are in `android/app/src/main/AndroidManifest.xml`, not a generic "manifest".
- [ ] When showing dependency version strings, use the exact version or a variable like `$moe_version` that is defined in the snippet. Never use `x.y.z` as a placeholder without marking it clearly as a placeholder.
- [ ] When a page shows both a `package.json` flag and a `build.gradle` dependency as alternative ways to add the same library, explicitly frame them as "choose one". A junior who does both risks version conflicts or duplicate dependencies.
- [ ] `build.gradle(.kts)` notation is cryptic to juniors. Spell it out: "If using Groovy, edit `build.gradle`. If using Kotlin build scripts, edit `build.gradle.kts`." Preferably use separate `<Tab>` blocks for Groovy vs Kotlin DSL when the syntax differs.
- [ ] Hardcoded AndroidX / third-party library versions in code snippets (e.g., `androidx.core:core:1.9.0`) can go stale. Either note the minimum required version and link to the library's release page, or use a variable. Never silently pin to an old version without comment.
- [ ] `<Info>` callouts that describe critical constraints — "do not remove the `InitializationProvider` from the manifest" or "this will cause a build failure" — should be `<Warning>`, not `<Info>`.
- [ ] JSON code blocks used to illustrate `package.json` configuration must not contain inline comments (`// like this`). JSON does not support comments; copying the block directly causes a JSON parse error. Move explanations into the prose or use a table below the block.
- [ ] The `AndroidX` library name is spelled with capital X: `AndroidX`, not `Androidx`. Flag any occurrence of `Androidx` in prose or headings.
- [ ] Pages that include an H1 heading (`# Heading`) in the body alongside a frontmatter `title` will render two H1s. Mintlify generates the page H1 from `title`. Use `##` for the first heading in the body.
- [ ] When optional feature flags are listed (e.g., `richNotification`, `pushAmp`), and they link to documentation, verify the links go to RN SDK pages (`/developer-guide/react-native-sdk/…`) rather than Android native SDK pages (`/developer-guide/android-sdk/…`). If no RN-specific page exists, note it.

### 8. JavaScript / TypeScript steps

- [ ] Import paths match the published package name (e.g., `import MoEngage from 'react-native-moengage'`). Do not fabricate import names.
- [ ] TypeScript type annotations, if shown, are accurate for the SDK's exported types.
- [ ] Code examples use `async/await` or explicit `.then()` chains — not mixed styles in the same snippet.

### 9. Step continuity and numbered-list rendering

Mintlify / MDX breaks numbered-list continuation when block elements (`<Frame>`, `<Tabs>`, `<Info>`, etc.) appear between list items at the top level. The list restarts numbering after each block.

- [ ] Check all numbered lists that are interrupted by block components. Either nest the block inside the list item, or restructure the steps so blocks appear after the list completes.
- [ ] Inline `<Info>` or `<Note>` callouts that belong to a specific step should be inside the list item, not between list items at the top level.
- [ ] Heading levels inside a step (`###`, `####`) do not restart list numbering but can visually escape the step's context. Use a subheading only when the content is long enough to warrant it; prefer a bold lead-in otherwise.

### 10. Images

- [ ] Every `<img>` has descriptive `alt` text that explains what the image shows. Auto-generated names like `"Newrunscriptphase"`, `"Path"`, `"I OS"`, `"Appgroup"`, `"Provisioningprofile"` are not acceptable.
  - Good: `"Adding a new Run Script Phase in the Xcode app target Build Phases tab"`
  - Bad: `"Newrunscriptphase"`
- [ ] Images with `className="hidden dark:block"` have a light-mode counterpart, or the dark-only class is removed so the image displays in all themes.
- [ ] Image `title` attributes, if present, match the `alt` text or are removed. Duplicate or inconsistent title/alt is noise.

### 11. Table content

- [ ] No emoji (✅, ❌, ⚠️, etc.) in table cells. Use plain text: "Required", "Optional", "—".
- [ ] Column values of `(default)` or `—` are explained in a table caption or a preceding paragraph so a junior knows what "default" means in context.

### 12. Code blocks

- [ ] Every code block has a language tag: ` ```swift `, ` ```kotlin `, ` ```bash `, ` ```ruby `, ` ```json `, ` ```typescript `, etc.
- [ ] Code block titles (the string after the language tag, e.g., ` ```bash Swift Package Manager (SPM) `) are spelled correctly. Watch for "Swift Packet Manager" instead of "Swift Package Manager".
- [ ] Shell commands in ` ```bash ` blocks that span multiple lines are chained correctly with `&&` (sequential, stop on failure) or shown as separate code blocks if they are independent steps.
- [ ] `$OPTIONS` and other shell placeholder variables in run-script commands are explained in a follow-up list or table before they are used, not after.

### 13. Callout component usage

- [ ] `<Tip>` is used for best practices and recommendations — not for prerequisites. Use a dedicated **Prerequisites** section or an `<Info>` callout for prerequisites.
- [ ] `<Warning>` body text does not start with a bold label like `**Information**` — the component's own header handles labeling.
- [ ] `<Info>` and `<Note>` are not used for mandatory steps or blocking requirements. Those belong in `<Warning>` or in the main flow.

### 14. Verification step

- [ ] After completing all integration steps, the page tells the reader how to verify the integration worked. Examples:
  - "Build and run the app — look for `[MoEngage] Extension configured successfully` in the Xcode console."
  - "Send a test push from the MoEngage dashboard and confirm the impression appears in **Analytics > Push > Impressions**."
- [ ] Troubleshooting guidance (or a link to it) is present for the most likely failure modes.

### 15. General writing standards

- [ ] Second-person voice throughout ("you", not "the developer" or "the user").
- [ ] Active voice. Flag passive constructions like "the extension must be added" → "add the extension".
- [ ] "follow the below steps" → "follow these steps".
- [ ] No marketing language: "powerful", "seamless", "robust", "easily", "simply".
- [ ] No filler phrases: "it's important to note", "in order to", "please note that".
- [ ] Sentence case for all headings, including the frontmatter `title`.

---

## Common patterns to flag

These issues appear repeatedly in RN SDK pages copied or adapted from iOS SDK or Flutter SDK documentation.

| Pattern | What to check |
|---|---|
| Step N cross-references | Step numbers in "Required if the content extension from Step N" often refer to step numbers from the source page, not this page. |
| Copied paths | Internal links copied from `/developer-guide/ios-sdk/...` or `/developer-guide/android-sdk/...` are wrong in an RN SDK page. |
| PascalCase paths | Links ending in `Integrating-MoEngage-Service-Extension` should be kebab-case. |
| Podfile full block | Showing the full `target 'YourApp'` block implies the reader should add all of it; call out what's new vs already present via autolinking. |
| Over-escaped build settings | `**ENABLE\_USER\_SCRIPT\_SANDBOXING**` should be `` `ENABLE_USER_SCRIPT_SANDBOXING` ``. |
| Missing sandboxing step | Every page that adds an Xcode Run Script Phase must include the "set ENABLE_USER_SCRIPT_SANDBOXING to No" step. |
| Missing Xcode entry point | Any iOS-native step needs "open `ios/<App>.xcworkspace` in Xcode" before the first step. |
| Typo in code-block title | "Swift Packet Manager" → "Swift Package Manager". |
| idmsa.apple.com links | Replace with `https://developer.apple.com/account/resources/identifiers/list`. |
| "(three gaps)" with two bullets | Count the items after any "N reasons/gaps/causes" phrase. |
| Dark-only images | `className="hidden dark:block"` with no light-mode image — invisible in light mode. |
| JSON comments | `// comment` inside a ` ```json ` block is invalid JSON. Move comments to prose. |
| `Androidx` spelling | Must be `AndroidX` (capital X) in all prose and headings. |
| Ambiguous `build.gradle` | "build.gradle" without a path is ambiguous — always prefix with `android/app/` or `android/`. |
| Duplicate H1 | `# Heading` in the body + frontmatter `title` = two H1s. Use `##` for the first body heading. |
| Package.json vs Gradle alternatives | When both are shown for the same outcome, label them as "choose one" to prevent both being applied. |
| Stale pinned versions | AndroidX versions like `1.9.0`, `1.4.2` in snippets may be outdated — flag without the latest version note. |
| Android feature flag links to Android native SDK | Optional module docs linked from RN pages should go to RN paths, not `/developer-guide/android-sdk/…`. |

---

## Severity definitions

Use these consistently when reporting findings.

**Blocking** — Prevents the reader from completing the integration, causes a broken link or broken render, or contains factually incorrect information that would break the build or the feature.

**Content gap** — Information a junior developer needs but cannot find on this page. The integration could fail or require significant guesswork. Examples: missing verification step, missing platform orientation, missing "which file" context for a code snippet.

**Style** — Formatting, word choice, or convention issues. Does not block integration but reduces quality and consistency.

---

## Output format

Present findings in this structure:

```
## Blocking issues

### 1. <Short title> (line N)
<What the issue is and why it blocks integration.>

## Content gaps

### 1. <Short title>
<What's missing and what a junior would need to proceed.>

## Style

### 1. <Short title> (line N)
<Specific fix: old text → new text, or description of the change needed.>
```

Always include file path + line number for blocking and style issues. For content gaps that span the whole page, a line number is not required.
