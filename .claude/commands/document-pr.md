---
allowed-tools: Bash(gh pr *)
description: Analyze a pull request and create or update MoEngage documentation for a new or changed feature. Identifies which pages need updates and suggests locations for new content. Use when the user asks to document a PR, add docs for a feature, or write documentation for a pull request.
argument-hint: [pr-number] [repository]
---

I need to document a new or changed feature. Please:

1. Analyze the code changes in pull request `#$1` in repository `$2`.
   - If the GitHub CLI exists, run `gh pr view $1 --repo $2`, `gh pr view $1 --repo $2 --comments`, and `gh pr diff $1 --repo $2` to get the PR metadata, discussion, and code changes.
2. Determine which MoEngage docs section this belongs in:
   - `user-guide/` for dashboard-facing product features.
   - `developer-guide/<sdk>/` for SDK changes (iOS, Android, Web, React Native, Flutter, Cordova, Unity, Capacitor, Ionic, Personalize, ecommerce platforms).
   - `api/` for REST API changes.
3. Search through the docs for existing pages that cover the affected area. Prefer updating an existing page to creating a new one.
4. Identify:
   - Which pages need updates and what sections of each page.
   - Whether a new page is needed, and if so, propose a title, file path (kebab-case `.mdx`), and the navigation group in `docs.json` where it belongs.
   - Whether release notes need an entry (`user-guide/release-notes/YYYY/<month>-YYYY.mdx` for product changes; `developer-guide/release-notes/<sdk>/` for SDK changes).
5. Show me your plan for making these content updates before writing anything. The plan should list:
   - Files to edit (with the specific section in each).
   - Files to create (with proposed titles and nav placement).
   - Open questions where you're not sure of behavior, defaults, or wording.

Wait for my confirmation before writing the actual content.
