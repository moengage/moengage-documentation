---
allowed-tools: Bash(gh pr list *), Bash(gh pr view *), Bash(gh pr diff *)
description: Update MoEngage release notes with summaries of recent pull requests from specified repositories. Highlights bug fixes and new features for end users. Use when the user asks to update release notes, document recent changes, or add new entries to the changelog.
agent: opus
argument-hint: [...repo]
---

MoEngage keeps release notes in two places:
- **Dashboard / product changes** → `user-guide/release-notes/YYYY/<month>-YYYY.mdx` (monthly files, for example `user-guide/release-notes/2026/april-2026.mdx`).
- **SDK changes** → `developer-guide/release-notes/<sdk>/...` (per-SDK directories like `ios-sdk`, `android-sdk`, `flutter-sdk`, etc.).

Update the correct file for each repository in `#ARGUMENTS`. If in doubt, ask which file to update before writing.

Steps:

1. Ask me what date range of repositories to look at. Keep the date range consistent with the previous release notes update. Only make one release notes update per run.
2. Look at the repositories listed in `#ARGUMENTS`.
3. We do not use GitHub Releases. Only look at closed pull requests within the chosen date range:
   ```
   gh pr list --repo {owner/repo} --state merged --search "merged:{YYYY-MM-DD}..{YYYY-MM-DD}"
   ```
4. For each pull request, invoke `@agents/pr-summarizer` in parallel to generate a summary file under `summaries/`.
5. Read each summary from `summaries/` and group them by:
   - Repository / SDK.
   - Change type — new feature, bug fix, improvement, deprecation, breaking change.
6. Tell me a high-level summary of what was changed across all PRs before writing anything.
7. Update the correct release notes file(s) using Mintlify components and the existing style of neighboring release notes pages. For a monthly user-guide update, open the month's file (create it if missing) and add entries grouped by MoEngage product area (Campaigns & Channels, Flows, Analyze, Segment, Content, Data, Intelligence, Personalize, Decisioning, Inform, Settings).

Content filter — include:
- New features that customers can see or use.
- Bug fixes with customer impact.
- Behavioral changes, deprecations, and breaking changes.

Content filter — exclude:
- Internal tooling, refactors, CI changes, dependency bumps without customer impact.
- Package version bumps for internal libraries.
- Infrastructure changes.
- Incremental implementation PRs that are part of a larger shipped feature already described.

Wait for my confirmation on the grouping and summary before editing release notes files.
