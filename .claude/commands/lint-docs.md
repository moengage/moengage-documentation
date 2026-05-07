---
allowed-tools: Bash(mint *), Bash(vale *), Bash(git diff *)
description: Check MoEngage documentation for broken links, Vale style errors, and OpenAPI spec validity. Propose fixes for issues found. Use when the user asks to lint, check for broken links, run Vale, or fix documentation errors.
---

Run the standard MoEngage docs lint pass:

1. Run `mint broken-links` to check internal links across the repo. Cross-reference any issues against the current git diff (`git diff --name-only main`) so we prioritize broken links introduced by recent changes.
2. Run `mint validate` to validate the build, including OpenAPI specs under `api/`.
3. If the Vale CLI is available, run `vale $(git diff --name-only main)` on all changed files. Vale uses MoEngage's prose style rules from the repo's `.vale.ini` if present.

After running the commands:

- Summarize the failures by category (broken internal links, Vale alerts by level, OpenAPI validation errors).
- Group issues by file so a writer can fix them one page at a time.
- Propose a fix plan for each failure. Prefer the smallest reasonable change.
- Do not apply fixes yet — show the plan first and wait for confirmation.

## mint CLI reference

```
mint <command>

Commands:
  mint dev                       initialize a local preview environment
  mint broken-links              check for invalid internal links
  mint validate                  validate documentation build
  mint update                    update the CLI to the latest version
  mint version                   display the current version of the CLI and client [aliases: v]

Options:
  -h, --help     Show help                                             [boolean]
  -v, --version  Show version number                                   [boolean]
```

## Vale CLI reference

```
vale - A command-line linter for prose.

Usage:  vale [options] [input...]
    vale myfile.md myfile1.md mydir1
    vale --output=JSON [input...]

Flags:

 --config         A file path (--config='some/file/path/.vale.ini').
 --ext            An extension to associate with stdin (--ext=.md).
 --filter         An expression to filter rules by.
 --glob           A glob pattern (--glob='*.{md,txt}.')
 -h, --help       Print this help message.
 --ignore-syntax  Lint all files line-by-line.
 --minAlertLevel  The minimum level to display (--minAlertLevel=error).
 --no-exit        Don't return a nonzero exit code on errors.
 --no-global      Don't load the global configuration.
 --no-wrap        Don't wrap CLI output.
 --output         An output style ("line", "JSON", or a template file).
 -v, --version    Print the current version.

Commands:

 ls-config        Print the current configuration to stdout.
 ls-dirs          Print the default configuration directories to stdout.
 ls-metrics       Print the given file's internal metrics to stdout.
 ls-vars          Print the supported environment variables to stdout.
 sync             Download and install external configuration sources.
```

See https://vale.sh for more setup information.
