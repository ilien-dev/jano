---
name: jano
description: "Draw a repository its README hero: a looping animated SVG, in dark and light, that shows anyone, technical or not, what the project is for."
disable-model-invocation: true
---

# jano

Draw this repository an animated hero for the top of its README. The hero is the whole job: do
not rewrite the README's title, text, badges or links, and do not commit.

## 1. Learn the repo

Read the README, docs and code until you can answer three things in the words of someone who has
never opened a terminal:

- who uses it, and at what moment;
- what was slow, risky, tedious or impossible for them before;
- what they have after.

Join the answers into **one sentence** with no word of the trade in it: no protocol, format,
language or framework name, except the ones that person would say themselves ("a Kindle book",
"a PDF"). That sentence is the script of the hero.

Then find its **one proof**: the number, before/after or real output that makes the sentence
believable, said the way that person would say it ("9 times out of 9", "half the size"). Use only
facts the repo backs (benchmarks, tests, real output). A hero with an invented number is worse
than no hero. When the repo measures nothing, the proof is its own sample output and the hero
carries no figure.

Look for an existing identity (logo, `DESIGN.md`, brand folder, site, badge colors) and reuse its
colors and mark. The accent is the one the identity declares; when it declares none, take it from
the mark. If there is no identity, pick one accent that suits the subject; everything else is
neutral. The fonts are the skill's in every hero, whatever the brand uses.

## 2. Logo: `assets/logo.svg`

If the repo has a mark, use it as it is, whatever its shape or detail: copy it to
`assets/logo.svg` (the variant made for light backgrounds, when there are two). Otherwise draw a 160×160 mark from the name, from what the tool does, or
both: two or three thick shapes, ink plus the accent, on a rounded square of the dark background.
It has to survive 16 px, so no thin strokes, no text, no detail.

## 3. Hero: `assets/hero.src.svg`

What is standard is the quality bar, never the composition. Two heroes made
with this skill should share fonts and care, and look nothing alike, because the tools are not alike.

The viewer is anyone: a person who arrived from a link and may not program. After five seconds
of looking, they can tell a friend what this is for. People who know the subject read the rest of
the README; the hero is for everyone else.

Start from one question: **what picture tells your sentence to that person without reading?**
Draw that, alive, and give it most of the canvas. Then place the logo, the name and your sentence,
shortened to one line, wherever the picture leaves room. Those are the only required parts.
Figures, chips, captions or a ticker go in only when this repo has something worth putting there.

Pick the form that tells the sentence best. The picture comes from the repo, so go and look at it
first:

- **Demo.** The product in use, simplified. For anything with a screen a person would recognise.
  Read the components, screenshots and design tokens, keep the real layout, labels and colors,
  and animate what a user would see happen. It is a portrait, so it has to be recognisable, and
  it does not have to be exact.
- **Journey.** A recognisable thing (a book, a page, a photo, a message) goes in one side and
  comes out the other changed. For converters, pipelines and anything that transforms.
- **Before and after.** The same thing without the tool and with it, side by side or taking
  turns. For tools that fix, clean, check or shorten.
- **Scene.** The situation where the tool matters, with the tool as one of the actors. For tools
  that work behind something else (a server, a plugin, a hook, an agent tool), whose real surface
  is a terminal or nothing at all. Draw who and what is involved as simple objects (the
  assistant, the web, a document, a person) and show what travels between them.
- **Measure.** A quantity drawn against something familiar, so the difference shows before the
  number is read. For tools whose whole point is faster, smaller, cheaper or more.

Combine two when one alone leaves the sentence half told, and draw something else when the
subject has its own shape (a network, a waveform, a map).

Where the tool runs sets the stage. The subject is always what the person gets. A terminal tool
can show its terminal, small and recognisable, with one real command in it; the meaning is
carried by the objects around it and by labels in plain words, because real output explains
nothing to someone who cannot read it.

Every word on the canvas is one the viewer already knows. A real command, file name or term of
the trade appears as texture, never as the explanation.

The picture works with every word blurred: shapes, direction and color say what goes in, what
changes and what comes out, and words only name things. Sample content inside the picture (a
chat, a page, a list) is large enough to recognise and short enough to take in while it passes.
The moment of change is the most interesting thing on the canvas, so it happens in plain sight;
the logo sits beside it, never over it.

A story with steps (first this, then that) is drawn with all its steps on the canvas at once,
joined by things that travel from one to the next.

Before you build, write down what that viewer would say the tool does after seeing your picture
with the tagline covered. When it does not match your sentence, draw a different picture.

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
writes a preview page (both themes, README and phone width, the logo small) to the system temp
folder, at the path it prints. Fix what it reports, then open the preview and look, with a
browser tool if you have one, and correct overlaps, shapes that touch by accident, text that
runs out of its box or sits closer than 16 px to its edge, a loop that jumps, or a light theme
that came out weak. Keep the source next to the two outputs.

## 5. Put it in the README

Add this as the first thing in `README.md`, and in each translated README. If a hero or banner
image is already there, replace it and leave its old files where they are. Touch nothing else.

```html
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <img src="assets/hero-light.svg" alt="{what the hero shows, with its figures}" width="100%">
  </picture>
</p>
```
