---
name: jano
description: "Make a repository's README explain itself: plan its sections and write its text to measured rules, and draw an animated SVG hero and a scene for each section that needs one, in dark and light."
disable-model-invocation: true
---

# jano

Jano runs a repository's README. The finished README is read from top to bottom by someone who
has never seen the project, and they come out knowing what it does, for whom, and how to start.
Every picture explains its part before a word is read: the hero at the top says what the whole
repository is, and the scene over a section says what that section is about. The text is
planned, sized and formatted to rules that a script measures (`scripts/readme.py`), so the
result does not depend on how this run went. Do not commit.

**Only the hero.** When the user asks only for the banner or the hero, do step 1 and then
`references/hero.md`, and touch nothing else in the README but the hero itself.

**The scripts decide when it is done.** `build.py` measures every picture, `readme.py check`
measures the plan, the README, its translations, the pictures and the judges. A step is
finished when its script passes. A warning you leave stays in your report with the reason.

Run the scripts with `uv run <this skill>/scripts/<script>.py`; without `uv`,
`pip install fonttools brotli` and use `python`.

## 1. Learn the repo

Read the README, docs and code until you can write down six things.

**The sentence.** Who uses it and at what moment, what was slow, risky, tedious or impossible for
them before, and what they have after, joined into one sentence with no word of the trade in it:
no protocol, format, language or framework name, except the ones that person would say
themselves ("a Kindle book", "a PDF").

**The flow.** What happens when it is used, as three to five steps with their real names from the
repo: what goes in, what the tool does to it, what comes out.
`a Kindle book with a lock -> Anzu opens it -> an EPUB any reader takes`. This is what the hero
will show, so it has to be true: follow it in the code, do not guess it from the name.

**Only what ships.** What the repo marks as unfinished stays out of the hero: the flow, the
highlights, the strip and the sample content. Look for experimental, beta, preview, planned,
"coming soon", a flag that turns it on, a roadmap, the Unreleased part of a changelog. When the
flow itself is unfinished, stop and ask the user before drawing it as done.

**The kind.** How a person meets it: a screen, a terminal, a call from their own code, something
that works unseen inside another tool, a set of files. The kind decides the hero and the scenes (`references/pictures.md`).

**The audience.** Who the README is written for. Most tools are for people who do not care how
they work: someone who reads books, learns a language, writes, saves money. Some are for
professionals who speak the trade (an SSH library for cloud machines, a database driver, a build
tool for a compiler team). Everything the hero says beyond the name is written for that person:
in the first case in plain words, in the second the trade's own words are fine.

**The highlights.** What would make that person want it, as one of two things, or neither:

- **Figures**, one to four, only when a number is the selling point and that person feels it:
  how much faster, smaller or cheaper it is, measured ("48% fewer tokens", "half the size",
  "in 3 seconds"). Use only what the repo backs (benchmarks, tests, real output). A hero with
  an invented number is worse than no hero; a number that is old or a target is left out.
- **Features**, three to five, when no number sells it: what the person gets, each in two to
  five plain words ("Works offline", "Your books stay yours", "Feedback after you speak").

Test each one by asking whether a person who has never seen the repo would repeat it to a
friend. Counts of the tool's own insides fail that test whatever their size: tests, checks,
files, fonts, stages, review intervals, lines of code, settings. So do numbers that only make
sense once you know the tool ("0 corrections while you talk", "4 stages to mastered"). When
nothing passes, the hero has no highlights: the key phrase and the picture carry it. Fewer and
true beats a full row.

**The key phrase and the description.** The key phrase is your sentence cut down to what a
poster says: ten words or fewer, on one or two lines, the benefit first ("Shorter replies. Up
to 48% fewer tokens."). The description is one or two lines under it, 8 to 24 words, that add
what the phrase leaves out: what kind of thing this is, where it runs, the one detail worth
knowing. When the repo already has a tagline in plain words, it is the key phrase.

**The strip, or none.** A line of text that runs along the bottom, for facts that are a list by
nature: where it runs, what it reads or works with, a measured result per case. Write the
candidates, a few true words each and written for the audience above, then strike what the key phrase, description, highlights,
badges or install section already say (licence, install command, runtime) and the counts of the
tool's insides. Keep a strip only when five or more remain and the picture leaves the bottom
edge free (nothing there travels sideways or runs as text). Otherwise the hero has no strip,
and the picture and the backdrop run to the bottom edge.

**The brief.** Write down what the hero claims, for the user to check before it goes in the
README: the sentence; one real input and output from the repo, with the files they come from;
the file behind each figure and feature; and what you left out as unfinished.

Look for an existing identity (logo, wordmark, `DESIGN.md`, brand folder, site, design tokens,
badge colors) and reuse its colors, mark and rules. The accent is the one the identity declares;
when it declares none, take it from the mark. If there is no identity, pick one accent that suits
the subject; everything else is neutral. When the product has one theme only, derive the other:
the same hues, background and ink swapped, the accent darkened or lightened until text in it
passes contrast. The fonts are the skill's in every hero, whatever the brand uses; the one
exception is a wordmark the repo ships as a file, which is used as shapes.

A brand rule that cannot hold at hero size (interface text of 11 px) gives way to the sizes
below; its rules on color and on the mark always hold. Where the brand keeps its accent off
text, or the accent is too pale to read, the words this skill puts "in the accent" take a
darker or lighter tone of the same hue that passes contrast, and the pure accent stays on
shapes.

The hero speaks the language of the main README. Sample content may be shortened; it is never
something the tool would not produce, and it names no real third party (`example.com`, not a
real shop).

## 2. Ask the user, once

Run `readme.py survey <repo>`. It lists what is there now, the lines that mark something
unfinished, whether the project has a screen, and the questions to ask. Ask them in one message
(with a question tool when you have one), each with your proposal and its reason:

- **Audience.** General (people who use the result) or technical (professionals of the trade).
  Propose the one your notes from step 1 point to. It sets the section count, the word budget,
  the number of scenes and how much trade vocabulary the text may use.
- **Unfinished features**, one by one: keep it in the README or leave it out. Leaving out is
  the default; what is kept is said to be unfinished where it appears.
- **A real screen**, only when the survey found one: the scenes are drawn SVG; may one section
  show a real screenshot inside its scene instead? Ask only when a drawing would explain that
  section less well than the real screen (a demo of an app the reader will use), and propose
  which section.

- **Backdrop.** Whether the pictures have a background pattern, still or moving, and which
  one. Propose from what the repository is about (`references/hero.md`, "The backdrop is chosen,
  not assumed"): none, a still pattern or a moving one, and a pattern that fits the subject; when
  none fits, the survey's `backdrop_pick` for this repository. Dots are a fallback, not the
  default.

Record each answer in the plan (step 3). Without answers, the plan does not pass.

## 3. Plan: `assets/readme/plan.json`

Run `readme.py rules` and read all of it: the roles a section can play, the word budget of each,
which ones take a scene for each audience, the alerts each role allows, and the shape of the
plan. Then write the plan:

- **The sections, in reading order.** Start from the existing README: keep its true content,
  give every `##` a role, merge what repeats, cut what no reader of this audience needs. The
  usual order is: lead (the top block), demo or features, how it works, install, use, then
  reference, FAQ, limits, licence. A role appears once.
- **What goes to docs/.** A section whose true content is longer than its role allows keeps a
  summary and links a file in `docs/` that holds the rest; the plan names that file in "docs".
  Technical depth (architecture, protocol, every option, benchmarks in full) goes there, written
  as a page of its own. Make the file when it does not exist, from the README's current text.
- **The scenes.** Each scene names its "claim" (what the reader understands from the picture
  alone, one sentence) and "shows" (the objects it draws). The hero has "shows" too. No two
  pictures may show the same things: the hero shows the whole flow, a scene zooms into one part
  of it or shows something the hero cannot (who it is for, what install looks like, a result).

`readme.py check` reads the plan first; fix what it says about the plan before going on.

## 4. Identity

The hero and the scenes share one palette, the skill's fonts and one backdrop, the one in the
plan's `"backdrop"` (`"none"` or `"<kind> <motion>"`, pasted from `kit.py backdrop`). Take colours and
mark from the repository's identity as `references/hero.md` says. Jano draws no characters or
mascots: what moves in a scene is the thing the section is about. When the user brings a
character of their own, it is drawn into the stage like any other object.

Then choose the asset families, before drawing anything: read `references/assets.md`. For each
category the pictures will need (icons, objects, logos, flags, files), describe the mark and
the hero (fill, stroke weight, corners, grid), run `assets.py suggest <category> ... --repo
<name>`, look at `assets.py preview <category>` for the families that fit, and record one with
`assets.py choose <repo> <category> <family> --why "..."`. Every asset of that category comes
from that family; `readme.py check` refuses a picture that mixes families.

## 5. The hero

Follow `references/hero.md`. When `assets/hero.src.svg` already exists and still says what the
repository is, keep it: rebuild it, and change it only when the plan or the judges say so.
Every build of the hero also writes the repository's social preview from that same hero, in
`assets/social-preview/`: an SVG and the PNG GitHub takes, dark and light.

## 6. The scenes: `assets/readme/<name>.src.svg`

Read `references/scenes.md`, then `references/motion.md` and the devices in
`references/pictures.md`. A scene is 1280×448: a small eyebrow with the section's name, a
headline that states what the section claims, an optional line under it, and a picture that
shows it, alive. Build them all at once (leave the hero out when only its built files exist):

```
uv run <this skill>/scripts/build.py assets/hero.src.svg assets/readme/*.src.svg
```

Read `loop.png` and `look.png` of each, as `references/hero.md` says for the hero, until each
builds clean and its pictures show what its claim says. Interface parts come from
`scripts/kit.py`, icons and other assets from `scripts/assets.py` in the chosen family, and
every one says what it means in `data-icon` (`references/scenes.md`, Parts, icons and assets).

## 7. The text

Read `references/writing.md`, then write `README.md` section by section in the order of the
plan. The scene goes right under its heading, as a `<picture>` with both themes; the text under
it says what the picture showed and what it could not. Every translation (`README.<lang>.md`)
gets the same sections, pictures and alerts in the same order; its scenes speak its language,
from their own sources in `assets/<lang>/readme/<name>.src.svg` with the same names. Then:

```
uv run <this skill>/scripts/readme.py check <repo>
```

Fix every error by changing the plan, the text or a picture. It will still say that the judges
are missing; that is the next step.

## 8. The judges

You know the repository, so you cannot read its README as a stranger does. Run
`readme.py judge <repo>`. It writes a folder the judges see and nothing else:

- **blind/**: each scene as a PNG with its eyebrow, title and sub removed, eight moments of its
  loop and its finished frame. The picture has to say its claim without a word of the text block.
  `icons.png` holds every declared icon, cut out at the size a README shows it; an icon the
  judge misreads or is unsure of is rebuilt, never removed.
- **reader/**: the README with every picture as a PNG beside it.
- **packets.json**: the three prompts and the fingerprint (`sha`) of every item;
  **claims.json**: what each item was meant to say, for the grader only.

Give the blind prompt to one fresh agent and the reader prompt to another: agents that have not
seen the repository, the plan or this skill, told to open nothing outside their folder. Give the
grade prompt, `claims.json` and both answers to a third. Record each verdict in
`assets/readme/judges.json` under its id, with the `sha` from `packets.json`. A failed picture is
fixed by changing the picture, never by adding words to it; a failed section, by changing its
text or its picture. Judge again what you changed. Without a way to start agents, tell the user
that the judges did not run; never record a verdict you wrote yourself.

`readme.py check` passes only when every item has a passing verdict on its current files.

## 9. Report

Tell the user, briefly: the audience and the answers to step 2; the sections, with what moved
to `docs/`; each scene and its claim; what the judges said, and what you changed after; any
warning left and why; the preview pages; the social preview, and that they upload
the PNG of the theme they prefer from `assets/social-preview/` in Settings → General → Social
preview, since GitHub has no API for it. Leave `assets/readme/plan.json` and the sources next to
their outputs, and do not commit.
