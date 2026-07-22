---
argument-hint: [extra context]
description: Review MoEngage documentation changes for writing standards, technical accuracy, frontmatter completeness, component usage, and style consistency. Use when the user asks to review changes, check if docs follow standards, or verify documentation quality.
---

Please review the changes I'm about to commit and check:

1. Do they follow MoEngage writing standards (`.cursor/rules/writing-rules.mdc`, `.claude/CLAUDE.md`)?
2. Do they follow general technical writing best practices — second-person voice, title case, active voice, no promotional language?
3. Are code examples accurate and do they have language tags?
4. Is the frontmatter complete and correct (`title`, `description`, and `keywords` where useful)?
5. Does the content match the style, depth, and structure of neighboring pages in the same section (`user-guide/` / `developer-guide/` / `api/`)?
6. Are Mintlify components used correctly (`Note`, `Warning`, `Tip`, `Info`, `Check`, `Danger`, `Steps`, `Tabs`, `CodeGroup`, `AccordionGroup`, `Card`, `Columns`)?
7. Are internal links root-relative and without file extensions?
8. Do all images have descriptive alt text?
9. Is the page added to `docs.json` under the correct tab (Home / User Guide / Developer Guide / API Guide) and group?
10. Are there any links that need testing?

Use the `document-reviewer` agent for deeper review when the change is large or spans multiple pages.

$ARGUMENTS
