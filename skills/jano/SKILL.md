---
name: jano
description: Draw a repository its README hero: a looping animated SVG, in dark and light, that shows what the project does.
disable-model-invocation: true
---

# jano

Draw this repository an animated hero for the top of its README. The hero is the whole job: do
not rewrite the README's title, text, badges or links, and do not commit.

## 1. Learn the repo

Read the README, docs and code until you can say what the tool does in one sentence and name its
**one proof**: the number, before/after, pipeline or output that makes someone get it at a glance.
Use only facts the repo backs (benchmarks, tests, real output). A hero with an invented number is
worse than no hero.

Look for an existing identity (logo, `DESIGN.md`, brand folder, site, badge colors) and reuse its
colors and mark. If there is none, pick one accent that suits the subject; everything else is neutral.

## 2. Logo: `assets/logo.svg`

If the repo has a mark, use it as it is (copy it to `assets/logo.svg` if it lives elsewhere), and
take the accent from it. Otherwise draw a 160×160 mark from the name, from what the tool does, or
both: two or three thick shapes, ink plus the accent, on a rounded square of the dark background.
It has to survive 16 px, so no thin strokes, no text, no detail.

## 3. Hero: `assets/hero.src.svg`

What is standard is the quality bar, never the composition. Two heroes made
with this skill should share fonts and care, and look nothing alike, because the tools are not alike.

Start from one question: **what picture would make a stranger understand this tool without reading?**
Draw that, alive, and give it most of the canvas. Then place the logo, the name and one line saying
what the thing is wherever the picture leaves room. Those are the only required parts. Figures,
chips, captions or a ticker go in only when this repo has something worth putting there.

The picture comes from the repo, so go and look at it first:

- An app with a UI: a simplified version of its real screen, in use. Read the components,
  screenshots and design tokens, keep the real layout, labels and colors, and animate what a user
  would see happen. It does not have to be exact; it has to be recognisable.
- A CLI or agent tool: its real commands and real output, working.
- A library, converter or pipeline: the thing it transforms, going in one way and out another.
- Something else: whatever its subject looks like (a document, a network, a waveform, a diff, a map).

Let that picture decide the layout: full-bleed with the title over it, centered, stacked, split,
one big object or many small ones. If you catch yourself drawing a headline on the left, a row of
numbers under it, two cards on the right and a strip along the bottom, stop: that is a template,
and it is the result this skill exists to avoid.

Format. 1280×640 (`viewBox="0 0 1280 640"`, `role="img"`, `aria-label`). The file starts with a
palette comment, and colors are written as `$role`; the build makes the dark and light files from it:

```
<!--palette
bg     #0F1115 #F0F5FB
accent #4FD1C5 #0B7A70
-->
<svg ...><style>@keyframes ...</style> <rect fill="$bg" .../> ...
```

Roles are `name dark light`. `bg panel ink body muted accent` get contrast-checked; add any others.
Text uses the classes `s` (Space Grotesk), `b` (bold) and `m` (JetBrains Mono). The build embeds
the fonts and the reduced-motion rule, so write neither.

Motion. The hero must look like a place that is always running, never like a video that starts
and ends:

- Every animation is `infinite` and closes on itself. Either travel linearly by exactly one period
  of repeated content (content drawn twice and scrolled, a pattern drifting one tile, items on a
  conveyor, lines moving under a fading mask), or swing between two states with `ease-in-out`
  where 0% and 100% are equal (breathing, pulse, sheen, cursor).
- No intro, no outro, no scene that builds up and resets, nothing that waits for its turn. To
  stagger things use negative `animation-delay`, so the first frame is already mid-motion.
- Something moves everywhere you look, but one thing leads: the picture of the tool. The rest
  stays low in amplitude, or it becomes noise.
- Moving text. Text may scroll, slide or ride along at a constant speed; the build turns any
  text inside a transform-animated element into outlines, because live text lands on whole
  pixels and crawls in small jumps while outlines glide. For that to work:
  - give the text a class `s`, `b` or `m`, and animate a wrapping `<g>`, not each line;
  - travel with `linear` and nothing else: no `steps()`, no easing, no stop-and-go;
  - keep it readable while it moves: about 10-30 px/s for lines someone should read in
    passing, 80-120 px/s for a ticker, and at least 13 px tall;
  - fade the edges where it enters and leaves with a gradient mask, never a hard clip;
  - one period of the repeated content must equal the travel exactly, or the loop jumps.
- The headline, name and tagline stay still. Pulsing text never drops below 0.55 opacity.
  Nothing under 13 px: GitHub shows the hero at about 65%.
- Motion too small to read as motion looks like a glitch: under about 6 px of travel or 3% of
  scale, make it larger or remove it.
- Animate only `transform` and `opacity`, which is what stays smooth. For scale or rotation add
  `transform-box:fill-box;transform-origin:center`.
- GitHub shows the file as an image: CSS only, no script, no external file, no `<image>`. Draw the
  logo inline. An animated element loses its own `transform` attribute, so position it with a
  parent `<g>`.

## 4. Build and look

```
uv run <this skill>/scripts/build.py assets/hero.src.svg
```

Without `uv`: `pip install fonttools brotli`, then run it with `python`.

It writes `assets/hero-dark.svg` and `assets/hero-light.svg`, prints errors and warnings, and
writes a preview page (both themes, README and phone width, the logo small). Fix what it reports,
then open the preview and look, with a browser tool if you have one, and correct overlaps, text
that runs out of its box, a loop that jumps, or a light theme that came out weak. Keep the
source next to the two outputs.

## 5. Put it in the README

Add this as the first thing in `README.md`, and in each translated README. If a hero or banner
image is already there, replace it. Touch nothing else.

```html
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <img src="assets/hero-light.svg" alt="{what the hero shows, with its figures}" width="100%">
  </picture>
</p>
```
