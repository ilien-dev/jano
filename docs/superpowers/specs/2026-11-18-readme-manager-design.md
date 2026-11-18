# Jano 1.0: from the hero to the whole README

## Intent

Jano drew one picture, the hero at the top of a README. The owner wants it to run the whole
README: the text (how many sections, how long, which Markdown elements and when) and a picture
over each section that needs one, in the
spirit of the section scenes of AgriciDaniel/claude-seo. The finished README is understood from
top to bottom by a stranger, and each picture explains its section before a word is read.
Behaviour is measured by scripts, not left to the prompt, because an agent skips prompt rules.

## Goals

- A plan file (`assets/readme/plan.json`) that fixes audience, sections with roles, word budgets,
  which sections get a scene, what each scene claims and shows, what moves to `docs/`, the
  user's answers on unfinished features and screenshots.
- `readme.py check` measures plan, README, translations, pictures and judges and exits 1 until
  all pass; `readme.py rules` prints the rules from the same constants the check uses.
- Section scenes (1280×448) built and measured by the existing `build.py`/`check.py`.
- No two pictures show the same thing (hero included): compared by stage words, large shapes and
  the plan's `shows`.
- Cold reads by fresh agents: a blind judge sees each scene without its text block, a reader judge
  sees the README with its pictures as PNGs, a grader compares to the claims. Verdicts are bound
  to file fingerprints, so a stale or skipped judge fails the check.

## Non-goals

- Mascots or characters. Tried in the first trials and dropped by the owner on 2026-11-18: whether a
  character fits cannot be measured. A user who brings one draws it into a stage like any object.

- Coloured text in Markdown (GitHub strips `style`); colour comes from scenes, badges, alerts.
- GIF or video production. A real screenshot may sit inside one scene, only with the user's
  agreement, and the README stays drawn SVG otherwise (owner's instruction).

## Approaches considered

1. **Prompt-only rules in SKILL.md.** Cheapest; rejected, the owner asked for measured behaviour.
2. **A separate README skill beside the hero skill.** Splits identity and duplicates the build;
   rejected.
3. **Extend the pipeline (chosen).** Scenes as a new kind in `build.py`/`check.py`,
   one new script for the README, SKILL.md as the orchestrator, the hero detail moved to
   `references/hero.md`.

## Decisions made for the owner (delegated)

- Audiences: general (5–9 sections, 1,100 words in sight, 3–5 scenes) and technical (6–11,
  1,600, 2–4). The skill proposes, the user confirms.
- Scenes are vector, in the hero's style, not pixel art; claude-seo's structure is borrowed
  (eyebrow, headline as claim, scene per section, game-like loops), not its look.
- Translations get their own scene sources per language and 25% looser word caps.

## Left to the builder

Scene drawing per repository, the exact copy, which old content moves to which `docs/` file.
