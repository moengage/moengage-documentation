---
argument-hint: <path-to-mdx-file>
description: Review an Android or iOS SDK changelog file from the perspective of a junior developer who reads it to decide whether to upgrade and what action to take. Covers upgrade clarity, content quality, badge consistency, version accuracy, and link correctness for 2025+ entries.
---

Review the SDK changelog at `$ARGUMENTS`.

1. Read the file at `$ARGUMENTS`. Focus on entries from January 2025 onwards — skip older entries unless they establish a pattern relevant to newer ones.
2. Apply the full checklist from `.claude/skills/review-sdk-changelog/SKILL.md`, keeping the junior developer's core questions in mind:
   - Do I need to upgrade?
   - Will this break my code?
   - What do I need to do?
   - Where do I learn more?
3. Report findings grouped by severity:
   - **Blocking** — factually wrong, broken link, version number error, or missing information that causes a failed upgrade.
   - **Content gap** — information a junior needs to act but cannot find in the entry.
   - **Style** — formatting, inconsistency, or word choice issues.

Include file path and line number for every blocking and style issue.
