---
name: uncontributing
description: Use before opening an issue, creating a branch, committing for a pull request, or writing a pull request title or description in the Jano repository. Walks through CONTRIBUTING.md (one change per PR, feature/ branch names, Conventional Commit titles that decide the version, the description format with character limits, evidence) and checks the result with .github/scripts/check-pr.js.
metadata:
  internal: true
---

# Contributing to Jano

`CONTRIBUTING.md` is the source of truth; this skill is the order to apply it in. If the
two disagree, follow `CONTRIBUTING.md` and point out the difference.

## 1. Is it in scope, and is it new?

- Jano does one job: it makes a repository's README explain itself, its sections and
  text measured by `readme.py`, its hero and section scenes drawn as animated SVG. It does
  not make GIFs, videos or other images; its one social card is the preview it cuts from the hero. If the change does not serve that job, say so and stop: it will be rejected.
- Search for the same work before writing anything:
  ```
  gh pr list --repo ilien-dev/jano --state all --search "<keywords>"
  gh issue list --repo ilien-dev/jano --state all --search "<keywords>"
  ```
  If a PR or issue already covers it, report it to the user instead of duplicating it.

## 2. One thing only

Name the single change in one sentence. If the sentence needs an "and", it is two PRs:
for example a fix in `build.py` **and** a new rule in `SKILL.md` **and** a README edit are
three pull requests. Propose the split to the user and do the first one. Leave unrelated
fixes you notice for later; mention them, do not include them.

## 3. Branch

`feature/` followed by 1 to 4 lowercase words (letters and digits) joined by single
hyphens, for every kind of change: `feature/outline-rotated-text`, `feature/fix-contrast-check`.
Regex: `^feature/[a-z0-9]+(-[a-z0-9]+){0,3}$`.

## 4. Code

- `skills/jano/SKILL.md` is loaded whole every time someone runs the skill. Add a line
  only for a failure you saw, and say it in as few words as the rest of the file does.
- A change to `skills/jano/scripts/build.py` comes with a test in `tests/run.py`.
- A change to `README.md` goes with the same change in `README.es.md`.
- Never edit the version in `.claude-plugin/plugin.json`, `.release-please-manifest.json`
  or `CHANGELOG.md`: the release workflow writes them.

Before committing:
```
uv run tests/run.py
```
It must pass; report a failure with its output.

## 5. Title

A Conventional Commit of at most 72 characters, lowercase after the type, no final
period. It becomes the squash commit on `main` and a line of the changelog, and its type
decides the next version, so pick the type that tells the truth about the change:

- `feat:` the skill or the build can do something new (minor release).
- `fix:` the skill or the build did something wrong (patch release).
- `docs:` README, CONTRIBUTING, comments. `refactor:`, `test:`, `ci:`, `chore:` for the
  rest. None of these release anything.
- A change to `skills/jano/SKILL.md` is a `feat` or a `fix`, never `docs`.
- `!` after the type (`feat!:`) when existing heroes or sources stop working.

## 6. Description

Copy `.github/pull_request_template.md` and fill every section. Limits are counted
after HTML comments are removed; delete the template comments anyway.

| Section | Limit | Content |
|---|---|---|
| `## What` | 280 chars | The one change, one or two sentences. |
| `## Why` | 280 chars | The problem for users. `Closes #N` when there is an issue. |
| `## How` | 500 chars | The approach and the main files. |
| `## Evidence` | 300 chars of text | Images, GIFs and links do not count. |
| `## Checklist` | — | Every box ticked, honestly. Untick and explain if one is not true. |

Write plainly: what changed, not how hard it was. No headings beyond these, no summary
at the end.

**Evidence.**
- A change to how heroes look or move: build a hero with it (run the skill on a
  repository, or build `tests/fixture/assets/hero.src.svg`) and capture the preview page,
  before and after when something changed. A GIF shows motion; a screenshot does not.
  Save the files in a temporary folder, not in the repository.
- GitHub has no API to upload images into a PR description. Open the PR, then give the
  user the absolute paths of the files and ask them to drag them into the description.
  Put a placeholder line in Evidence meanwhile, e.g. `GIF: to be attached.`
- Non-visual change: name the tests that cover it, or the exact steps used to check it.

## 7. Check before opening

Write the description to a temporary file and run:
```
node .github/scripts/check-pr.js --branch <branch> --title "<title>" --body-file <file>
```
The same check runs in CI as `Branch name and description`. Fix every problem it lists,
then open the PR:
```
gh pr create --title "<title>" --body-file <file>
```
Do not merge. Every PR needs an approval from someone with write access, and the
maintainer decides. Do not merge the `chore(main): release` pull request either: that
one publishes a version, and only the maintainer does it.

## Issues

Issues are contributions too. Use the forms in `.github/ISSUE_TEMPLATE/` (blank issues
are disabled): one bug or one idea per issue, the problem before the solution, and
search first.
