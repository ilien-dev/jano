# Contributing to Jano

Thanks for wanting to help. Contributing to Jano does not only mean pull requests:
a clear issue that reports a bug or proposes an improvement is a contribution too.

Jano does one job: it draws a repository a looping animated SVG hero for its README, in
dark and light. It does not write the README's text, and it does not make GIFs, videos,
social cards or logos for anything else. **A contribution that drifts away from that job
will be rejected**, however well it is made.

## Nothing is guaranteed

Opening an issue or a pull request does not guarantee that it will be accepted or merged.
Every change is reviewed before it goes in, with no exceptions, including the
maintainer's own. A change can be declined for its scope, its approach or the cost of
maintaining it.

## Before you start

- **Search first.** Look through the [open pull requests](https://github.com/ilien-dev/jano/pulls)
  and the [issues](https://github.com/ilien-dev/jano/issues), open and closed. Someone may
  already be working on the same thing, or it may have been discussed and declined.
  If you find it, add to that conversation instead of starting a new one.
- **For anything bigger than a small fix, open an issue first** and wait for an answer.
  It is the cheapest way to find out whether the change fits before you write it.

## Issues

Use the templates: **Bug report** or **Feature request**. One issue per problem or idea.

- A bug report says what you did, what you expected, what happened, and which agent,
  model and Jano version you used. For a hero that looks or moves wrong, attach a
  screenshot or a GIF.
- A feature request says the problem first, and only then the solution you have in mind.

## Pull requests

### One thing at a time

Each pull request does **one thing**. If you want the build to outline text inside
rotated groups, the PR does that and nothing else: no new rule in the skill, no README
edit, no unrelated cleanup. Those go in their own pull requests.

Keep it as simple as possible. The smaller and more focused a PR is, the easier it is to
see what it is about and to decide whether it can go in. A PR that mixes several changes
will be asked to split, or closed.

The skill's instructions are short on purpose, because every line costs context to each
person who runs it. A PR that adds a rule to `SKILL.md` says what went wrong without it.

### Branch name

```
feature/<1 to 4 words>
```

All lowercase, words of letters and digits joined by single hyphens, at most four words.
This holds for every kind of change, fixes and docs included.

- `feature/outline-rotated-text` ✓
- `feature/fix-contrast-check` ✓
- `feature/Rotated-Text` ✗ (uppercase)
- `fix/contrast` ✗ (does not start with `feature/`)
- `feature/add-the-new-contrast-check` ✗ (five words)

### Title

The title is a [Conventional Commit](https://www.conventionalcommits.org/) of at most 72
characters, lowercase after the type and with no final period. PRs are squash-merged, the
title becomes the commit on `main`, and it becomes a line of the changelog, so it has to
describe the change exactly.

The type decides the next version. Nobody writes a version number.

| Type | Use it for | Release |
|---|---|---|
| `feat:` | The skill or the build can do something new | minor, 0.2.0 → 0.3.0 |
| `fix:` | The skill or the build did something wrong | patch, 0.2.0 → 0.2.1 |
| `docs:` | README, CONTRIBUTING, comments | none |
| `refactor:` `test:` `ci:` `chore:` | No change in what a user gets | none |

A change to `skills/jano/SKILL.md` changes what users get, so it is a `feat` or a `fix`,
never `docs`. A change that breaks existing heroes or sources gets a `!` after the type
(`feat!:`).

### Description

Start from the template GitHub fills in for you
([`.github/pull_request_template.md`](.github/pull_request_template.md)). Every section is
required and has a limit:

| Section | Limit | What goes in it |
|---|---|---|
| **What** | 280 characters | The one change this PR makes. |
| **Why** | 280 characters | The problem it solves. Link the issue (`Closes #12`). |
| **How** | 500 characters | The approach, and the main files it touches. |
| **Evidence** | 300 characters of text | A GIF or screenshot; how you checked it. |
| **Checklist** | — | Every box ticked. |

**Evidence.** A change to how heroes look or move needs a GIF or a screenshot of a hero
built with it, before and after when something changed. Drag the files into the
description box on GitHub to upload them. Images, GIFs and links do not count toward the
limit. For a change with nothing to see, name the tests that cover it or say how you
checked it.

A CI check verifies the branch name, the title length and the description. You can run
it yourself before opening the PR:

```
node .github/scripts/check-pr.js --branch feature/outline-rotated-text \
  --title "fix: outline text inside rotated groups" --body-file pr.md
```

### Code

- `uv run tests/run.py` must pass. CI runs it on every PR. A change to `build.py` comes
  with a test in `tests/run.py`.
- Code, comments and docs are in English. `README.es.md` is the only Spanish file, and a
  change to `README.md` goes with the same change there.
- Do not edit the version in `.claude-plugin/plugin.json` or `CHANGELOG.md`; the release
  workflow does it.

### Review

A pull request is merged only after an approval from someone with write access to the
repository (for now, the maintainer) and with every check green. Answer review comments
in the PR; keep extra changes for another PR.

## How releases happen

Each merge to `main` updates one pull request that a bot keeps open, titled
`chore(main): release X.Y.Z`. It holds the next version number, computed from the titles
merged since the last release, and the new section of `CHANGELOG.md`. The maintainer
merges it when it is time to release, and that creates the tag and the GitHub Release.

## Working with an AI agent

The rules are the same. Agents that read `.claude/skills` or `.agents/skills` have a
`uncontributing` skill that walks through them step by step.
