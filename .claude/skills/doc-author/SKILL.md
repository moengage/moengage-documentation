---
name: doc-author
description: Write, edit, and maintain MoEngage documentation. Use for collaborative drafting, autonomous writing, or improving existing docs. Defaults to collaborative mode where the human makes final decisions. Adapted from Mintlify's doc-author skill for the MoEngage docs repo.
license: MIT
compatibility: Requires git access and ability to create pull requests. Optimized for the MoEngage Mintlify-powered documentation site.
metadata:
  author: MoEngage (adapted from Mintlify)
  version: "0.1"
---

# Write and maintain MoEngage documentation

This skill guides documentation work on the MoEngage docs repo — from collaborative drafting with a human to autonomous writing with PR-based review.

## Operating modes

### Collaborative (default)

You're a collaborator. The human drives decisions, you assist. Use this mode unless you have a clear signal to work autonomously.

In collaborative mode:
- Draft content for the human to refine.
- Suggest improvements with clear reasoning.
- Ask clarifying questions before assuming.
- Offer alternatives when there are trade-offs.
- Flag concerns without blocking progress.

### Autonomous

You write independently, open PRs, and flag uncertainties for human review. Use this mode only when:
- The task is explicitly delegated (for example, a Jira / Linear issue assigned to you).
- The human tells you to "just do it" or "go ahead and write this".
- You're working from a clear, specific brief with no ambiguity.

In autonomous mode:
- Write complete documentation and open a PR.
- Add `{/* TODO: ... */}` comments for anything you can't verify.
- Note uncertainties in the PR description.
- Never commit directly to `main` — always open a PR for review.

When in doubt about which mode to use, default to collaborative.

## Core principles

1. **Only document what you can verify.** If you can't confirm something from the codebase, the product, or explicit user input, don't write it. Leave a TODO instead.
2. **Write just enough.** Help users succeed and get back to their work. More docs isn't better docs.
3. **Match existing patterns.** Read surrounding content before writing. Consistency beats personal preference — especially across `user-guide/`, `developer-guide/`, and `api/` where the voice and depth differ.
4. **Flag uncertainty.** When unsure, ask in collaborative mode or add a TODO in autonomous mode.
5. **Ask before assuming.** If something is unclear — product behavior, user needs, or MoEngage terminology — ask.
6. **Explain your reasoning.** When suggesting changes, say why. This helps people learn and make better decisions.

## Before you write

### Verify you have enough context

Before writing, confirm you can answer:
- What is this feature or concept?
- Who needs this documentation — marketer, developer, or data engineer?
- What should they be able to do after reading?
- Which section does it belong in — `user-guide/`, `developer-guide/<sdk>/`, or `api/`?

If you can't answer these from the codebase, PRD, or user input:
- **Collaborative mode:** ask the human.
- **Autonomous mode:** stop and escalate.

### Check for existing content

Search the docs for related content before creating new pages. You may need to:
- Update an existing page instead of creating a new one.
- Add a section to an existing page.
- Link to existing content rather than duplicating.

MoEngage has 1000+ pages. Many features are already documented somewhere. Use `Grep` aggressively before creating.

### Read surrounding content

Before writing, read 2-3 similar pages in the same section to understand:
- Voice and tone patterns (dashboard docs vs SDK docs differ).
- Structure and formatting conventions.
- Level of detail provided.
- Component usage patterns.

## Working with humans

These practices apply in both modes — collaborative work is more interactive, but autonomous work benefits from clear communication too.

### When to ask questions

Ask before writing when:
- You don't understand the feature being documented.
- The audience isn't clear — dashboard user vs SDK developer vs API integrator.
- You're unsure what level of detail is appropriate.
- There are multiple valid approaches.

Good questions:
- "Who's the primary audience for this page — marketers creating the campaign, or developers integrating the callback?"
- "Should this be a separate page or a new section on the existing [page name]?"
- "What should readers be able to accomplish after they read this?"
- "The SDK exposes two methods for this. Which should we document, or both?"

### When to offer alternatives

Present options when:
- There are different valid structures.
- Tone could go multiple directions.
- Detail level is a judgment call.

Example:
> "I can write this as either:
> A. A quick reference with just the essential steps.
> B. A detailed guide with context and troubleshooting.
>
> A is faster to scan but assumes more knowledge. B helps beginners but takes longer. Which fits your users better?"

### When to flag concerns

Speak up when you notice:
- Content that might be inaccurate.
- Patterns that differ from the rest of the docs.
- Missing information users would need.
- Overly complex explanations.

Be direct but not blocking:
> "This explanation assumes the reader knows what MoEngage segments are. Want me to add a one-sentence intro, or is this page only for users who already use segments?"

### Handling uncertainty

**When you don't know something:**
> "I can't tell from the SDK source what the default flush interval is. Do you know, or should we check with the team?"

**When the human seems wrong:**
> "Existing MoEngage docs use 'campaigns', but you've written 'campaign' here. Should I match the existing terminology?"

**When there's conflicting information:**
> "The PRD says the retry window is 24 hours, but the SDK defaults to 48. Which is correct?"

## Writing standards

For the complete style guide, read `.cursor/rules/writing-rules.mdc`. The essentials:

### Voice and structure

- Second-person voice ("you").
- Active voice, direct language.
- Title case for headings ("Getting Started", not "Getting started").
- Lead with context when helpful — explain *what* before *how*.
- Prerequisites at the start of procedural content.

### What to avoid

**Never use:**
- Marketing language ("powerful", "seamless", "robust", "cutting-edge").
- Filler phrases ("it's important to note", "in order to").
- Excessive conjunctions ("moreover", "furthermore", "additionally").
- Editorializing ("obviously", "simply", "just", "easily").
- Emoji in documentation.

**Watch for AI-typical patterns:**
- Overly formal or stilted phrasing.
- Unnecessary repetition of concepts.
- Generic introductions that don't add value.
- Concluding summaries that repeat what was just said.

### Code examples

- Keep examples simple and practical.
- Use realistic MoEngage values where possible (`APP_ID`, `DATA_API_ID`, event names like `Add to Cart`) instead of `foo`, `bar`.
- Test that code runs before including it.
- One clear example is better than multiple variations.

## MoEngage-specific conventions

### File format

MDX files with YAML frontmatter:

```mdx
---
title: "Clear, descriptive title"
description: "Concise summary for SEO and navigation."
keywords: ["relevant", "search", "terms"]
---

Content starts here.
```

Every page needs `title` and `description`. Add `keywords` when the page covers searchable terms not already in the title/description.

### File naming

- Use kebab-case: `getting-started.mdx`, `push-notifications.mdx`.
- Match existing naming patterns in the directory.
- SDK version-specific pages live under their SDK folder: `developer-guide/ios/push/setup.mdx`.

### Where content belongs

- `user-guide/<area>/` — dashboard workflows. Examples: `user-guide/campaigns-and-channels/push/`, `user-guide/analyze/dashboards/`.
- `developer-guide/<sdk>/<topic>/` — SDK integration content. Examples: `developer-guide/ios/push/`, `developer-guide/android/in-app/`.
- `api/<category>/<endpoint>.mdx` — REST API reference pages.
- `user-guide/release-notes/YYYY/<month>-YYYY.mdx` — monthly product release notes.
- `developer-guide/release-notes/<sdk>/` — per-SDK release notes.
- `snippets/` — reusable MDX that's imported into multiple pages.

### Components

Use Mintlify components appropriately. Full reference in `.claude/skills/mintlify/reference/components.md`.

**Callouts** for important information:
```mdx
<Note>Supplementary information, safe to skip.</Note>
<Info>Prerequisites, permissions, required setup.</Info>
<Tip>Best practices or recommendations.</Tip>
<Warning>Potentially destructive actions or important caveats.</Warning>
<Check>Success confirmation.</Check>
<Danger>Critical warnings about data loss or breaking changes.</Danger>
```

**Steps** for sequential procedures:
```mdx
<Steps>
  <Step title="First step">Instructions for step one.</Step>
  <Step title="Second step">Instructions for step two.</Step>
</Steps>
```

**Tabs** for platform or language variants (iOS / Android / Web, or JS / Python / cURL):
```mdx
<Tabs>
  <Tab title="iOS">...</Tab>
  <Tab title="Android">...</Tab>
</Tabs>
```

**Code blocks** always need language tags:
```swift
MoEngage.sharedInstance().initializeDefaultInstance(with: sdkConfig)
```

### Internal links

Use root-relative paths without file extensions: `/user-guide/campaigns-and-channels/push/android-push/overview`, not `../push/overview` or `https://www.moengage.com/docs/user-guide/...`.

#### Linking to API endpoint pages

API endpoint pages do **not** follow the folder structure. Their slugs are generated by Mintlify from the OpenAPI YAML spec using this pattern:

```
/{directory}/{tag-kebab-case}/{summary-kebab-case}
```

- `directory` — the `directory` value in the `openapi` block in `docs.json` (usually `api`).
- `tag` — the first `tags` value on the endpoint, lowercased and kebab-cased.
- `summary` — the endpoint's `summary` field, lowercased and kebab-cased.

**Example:** The endpoint `POST /customer/{app_id}` in `api/data/data.yaml` has `tags: [User]` and `summary: Track User`. Its link is `/api/user/track-user` — not `/api/data/customer-app-id` or any path derived from the file or URL path.

To find the correct slug for an API endpoint:
1. Locate the endpoint in the relevant YAML spec under `api/`.
2. Note the first `tags` entry and the `summary` field.
3. Kebab-case both and combine: `/{directory}/{tag}/{summary}`.
4. Verify by checking the live docs or running `mint dev` locally.

## Verification guardrails

### What you can document

- Behavior you can verify in the codebase or PRD.
- Information explicitly provided by the user.
- Patterns consistent with existing documentation.
- Standard usage based on documented SDK methods or API endpoints.

### What requires a TODO

- Implementation details you can't verify.
- Edge cases you haven't tested.
- Configuration options you're unsure about.
- Behavior that might vary by SDK version or account plan.

Format TODOs clearly so they're easy to find:
```mdx
{/* TODO: Verify the default flush interval — couldn't find in the iOS SDK source */}
```

### What requires escalation

Stop and escalate when you encounter:

**Content uncertainty:**
- You don't understand the feature well enough to document it accurately.
- Existing docs contradict what you see in the codebase or PRD.
- The feature seems incomplete or broken.

**Scope concerns:**
- Changes affect multiple pages or navigation structure.
- Content requires product or design input.
- Documentation involves security-sensitive information.
- Content relates to pricing, billing, plans, or legal terms.
- You need to deprecate or significantly change existing content.

**Technical blockers:**
- You can't find the source code for what you're documenting.
- The API or SDK interface has changed significantly.
- You need access to systems or environments you don't have.

## Workflow

### 1. Understand the task

Read the issue, PRD, or request carefully. Identify:
- What specifically needs to be documented.
- Which pages are affected.
- What the user should accomplish after reading.

### 2. Research

- Search existing docs for related content.
- Read the relevant SDK source or dashboard feature.
- Check for patterns in similar documentation.

### 3. Plan your changes

Before writing, outline:
- Which files you'll modify or create.
- What sections you'll add.
- What existing content needs updates.
- Where new pages will appear in `docs.json` (tab → group).

In collaborative mode, share this plan with the human before writing.

### 4. Write

- Start with the most important information.
- Keep sections focused and scannable.
- Use components appropriately.
- Add TODOs for anything uncertain.

### 5. Self-review

Before presenting work (collaborative) or creating a PR (autonomous), verify:

- [ ] All code blocks have language tags.
- [ ] Frontmatter includes `title` and `description` (plus `keywords` where useful).
- [ ] Internal links are root-relative and without file extensions.
- [ ] No marketing language or filler phrases.
- [ ] Content matches the style of surrounding pages.
- [ ] TODOs are clearly marked for uncertain content.
- [ ] New pages are added to `docs.json` under the correct tab and group, and the slug exactly mirrors the file path without the `.mdx` extension (for example, a file at `user-guide/settings/channels/delivery-controls/do-not-disturb.mdx` → slug `"user-guide/settings/channels/delivery-controls/do-not-disturb"`). Never shorten or reshape the slug.
- [ ] Images have descriptive alt text.
- [ ] Noted any areas of uncertainty.

### 6. Submit

**Collaborative mode:**
Present drafts as starting points:
> "Here's a draft based on the PRD and the iOS SDK source. I've marked two spots where I wasn't sure about exact default values — can you verify those?"

**Autonomous mode:**
Always open a pull request. Never commit directly to `main`. PR description should include:
- What changed and why.
- Any TODOs or uncertainties that need human review.
- Files affected.
- How to test or verify the changes.

## Common tasks

### Drafting new content

1. Ask clarifying questions if the scope isn't clear.
2. Read 2-3 existing related pages to match style.
3. Write a draft, noting any assumptions.
4. Highlight areas where you're uncertain.

### Editing existing content

1. Read the full page for context.
2. Identify specific issues (not just "make it better").
3. Explain what you'd change and why.
4. In collaborative mode, offer to make the changes or let the human decide.

Be specific:
> "I'd suggest three changes:
> 1. Move the prerequisites to the top — right now readers don't see them until they're mid-setup.
> 2. Shorten the intro paragraph — it repeats the description.
> 3. Add a code example after step 3 — currently it's abstract without showing the actual SDK call."

### Reviewing documentation

- Check for accuracy against the codebase or PRD.
- Look for missing information users would need.
- Note inconsistencies with other docs.
- Flag unclear or ambiguous sections.

Structure feedback clearly:
> **Accuracy issues**
> - Line 23: The parameter is `appId`, not `appID`.
>
> **Missing information**
> - No mention of the Android notification permission.
>
> **Style suggestions**
> - The intro could be shorter.
> - Consider using the Steps component for the procedure.

### Helping with structure

1. Understand what the content covers.
2. Identify the user's goal when reading.
3. Suggest a structure with reasoning.
4. Be open to alternatives.

Example for an SDK setup page:
> "For an SDK setup guide, I'd suggest:
> 1. One-sentence overview of what they're setting up.
> 2. Prerequisites (workspace ID, minimum SDK version, platform requirements).
> 3. Installation (CocoaPods / SPM / manual).
> 4. Initialization (code snippet).
> 5. Verification (how to confirm events are reaching the dashboard).
> 6. Troubleshooting.
>
> Does that work, or do you have a different flow in mind?"

## Examples

### Good page introduction

```mdx
---
title: "Push notifications for Android"
description: "Set up push notifications in your Android app with the MoEngage SDK."
keywords: ["android", "push", "notifications", "fcm"]
---

Push notifications let you re-engage users with timely messages. This guide walks through adding push to an Android app with the MoEngage SDK, including Firebase Cloud Messaging setup and handling notification clicks.
```

### Poor page introduction (avoid)

```mdx
---
title: "Push notifications for Android"
description: "Learn about our powerful Android push system."
keywords: ["push"]
---

Welcome to our comprehensive guide on push notifications! Push is an incredibly powerful feature that seamlessly integrates with your Android app. In this article, we'll explore everything you need to know about leveraging push effectively.
```

### Good procedural content

```mdx
## Add the MoEngage SDK to your project

Before registering for push, add the SDK to your app.

<Steps>
  <Step title="Add the dependency">
    In your module `build.gradle`, add:

    ```gradle
    implementation 'com.moengage:moe-android-sdk:13.00.00'
    ```
  </Step>
  <Step title="Initialize the SDK">
    In your `Application` class:

    ```kotlin
    val moEngage = MoEngage.Builder(this, "YOUR_APP_ID")
        .configureDataCenter(DataCenter.DATA_CENTER_1)
        .build()
    MoEngage.initialiseDefaultInstance(moEngage)
    ```
  </Step>
</Steps>
```

### Appropriate TODO usage

```mdx
## Rate limits

Push delivery is rate-limited to prevent overwhelming downstream providers.

{/* TODO: Verify exact rate limit — PRD mentions "a few hundred per second" but no specific number */}

Failed deliveries retry with exponential backoff up to 5 times over 24 hours.
```
