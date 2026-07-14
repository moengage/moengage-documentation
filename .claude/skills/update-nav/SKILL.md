---
name: update-nav
description: Add new pages to the MoEngage docs.json navigation structure. Updates navigation groups based on the correct tab (Home, User Guide, Developer Guide, API Guide) and the user journey. Use when the user asks to add a page to navigation, update docs.json, add to nav, or include a new page in the sidebar.
---

# Update MoEngage navigation

Add new documentation pages to `docs.json` so they appear in the sidebar.

## MoEngage navigation structure

`docs.json` uses `navigation.tabs` with 4 top-level tabs:

1. **Home** — landing/overview pages.
2. **User Guide** — dashboard product docs (campaigns, flows, analyze, segment, content, data, intelligence, personalize, decisioning, inform, settings, use cases, release notes).
3. **Developer Guide** — SDK integration docs (iOS, Android, Web, React Native, Flutter, Cordova, Unity, Capacitor, Ionic, Personalize, partner integrations).
4. **API Guide** — REST API reference.

Each tab contains `groups`. Each group has a `group` name and a list of `pages`. Pages can be strings (file paths without extension) or nested groups.

## Instructions

1. **Identify the page.** Determine which file is being added.
   - If not specified, ask the user for the file path.
   - Confirm the file path is correct and relative to the repo root (for example, `user-guide/campaigns-and-channels/push/android-push/new-feature`).
   - Verify the MDX file actually exists before editing `docs.json`.

2. **Determine the tab.** Based on the file path:
   - `user-guide/...` → **User Guide** tab.
   - `developer-guide/...` → **Developer Guide** tab.
   - `api/...` → **API Guide** tab.
   - Top-level landing content → **Home** tab.

3. **Determine the group within that tab.** Figure out where in the navigation the page belongs.
   - Ask the user if they haven't specified a group.
   - Groups align with the user journey and product area. Examples: under User Guide, "Campaigns & Channels", "Flows", "Analyze", "Segment". Under Developer Guide, "iOS SDK", "Android SDK", "Web SDK", etc.
   - Read `docs.json` to see current navigation structure, group names, and nesting patterns.

4. **Read current docs.json.**
   - Understand the existing navigation structure for the relevant tab.
   - Find the correct group (and any nested sub-groups) to add to.
   - Note the format and patterns used — some groups list strings; others nest child groups with their own `pages`.

5. **Update docs.json.**
   - Add the new page entry to the appropriate group. The slug is the file path without the `.mdx` extension — it must exactly mirror the folder structure on disk. For example, a file at `user-guide/settings/channels/delivery-controls/do-not-disturb.mdx` becomes `"user-guide/settings/channels/delivery-controls/do-not-disturb"`.
   - Never invent or shorten a slug. If the file is at `developer-guide/ios/push/setup.mdx`, the entry is `"developer-guide/ios/push/setup"` — not `"developer-guide/ios/setup"` or anything else.
   - Maintain consistent formatting and indentation.
   - Preserve alphabetical or logical ordering within the group if that's the existing pattern.
   - Ensure valid JSON syntax.

6. **Show the change.**
   - Show the user the diff so they can confirm placement.
   - Confirm the page now appears in the correct tab and group.

## Navigation structure notes

- Pages are organized by user journey, not by file structure.
- Navigation group names should match existing patterns — don't invent new group names without asking.
- Each entry typically uses just the file path (for example, `"user-guide/content/templates/push-templates"`).
- Only update the English navigation in `docs.json`. Translations are handled automatically after the PR merges.
- If the group doesn't exist yet, ask whether to create a new group (and where) before editing.

## Example

If the user says "Add the new `android-push-v13-upgrade.mdx` page at `developer-guide/android/push/` to the Developer Guide navigation":

1. Verify `developer-guide/android/push/android-push-v13-upgrade.mdx` exists.
2. Read `docs.json` and find the Developer Guide tab → Android SDK group → Push sub-group.
3. Propose adding `"developer-guide/android/push/android-push-v13-upgrade"` after the existing entries in that sub-group (or ask the user where within the sub-group to place it).
4. Show the diff.
5. Apply on confirmation.

## Common pitfalls

- Adding the file extension (`.mdx`) to the path — don't.
- Using a slug that doesn't match the actual file path — the slug must mirror the folder structure exactly. Verify with the real file path before editing.
- Adding a page to the wrong tab because the file path was misread.
- Adding to the root of a tab instead of a specific group.
- Editing the `docs.json` in ways that break JSON validity (missing commas, stray brackets). After editing, run `mint validate` or `python3 -c "import json; json.load(open('docs.json'))"` to confirm the file still parses.
