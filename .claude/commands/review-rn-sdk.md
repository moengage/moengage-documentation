---
argument-hint: <path-to-mdx-file>
description: Review a React Native SDK documentation page for writing standards, technical accuracy, RN-specific usability, and Mintlify component correctness. Assumes a junior React Native developer as the reader.
---

Review the React Native SDK documentation page at `$ARGUMENTS`.

1. Read the file at `$ARGUMENTS`.
2. Identify which platform layers the page covers (iOS native, Android native, JavaScript/TypeScript, or a combination).
3. Apply the full checklist from `.claude/skills/review-rn-sdk/SKILL.md`.
4. Report findings grouped by severity:
   - **Blocking** — prevents integration, breaks a link or render, or is factually wrong.
   - **Content gap** — information a junior RN developer needs but cannot find.
   - **Style** — formatting, word choice, or convention issues.

Include file path and line number for every blocking and style issue.
