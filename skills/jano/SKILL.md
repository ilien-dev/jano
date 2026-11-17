---
name: jano
description: "Draw a repository its README hero: a looping animated SVG, in dark and light, that shows what the project does before a word of the README is read."
disable-model-invocation: true
---

# jano

Draw this repository an animated hero for the top of its README. The hero has one job: a person
who has read nothing yet looks at it and knows what this repository is and what it does. The
hero is the whole job: do not rewrite the README's title, text, badges or links, and do not
commit.

## 1. Learn the repo

Read the README, docs and code until you can write down four things.

**The sentence.** Who uses it and at what moment, what was slow, risky, tedious or impossible for
them before, and what they have after, joined into one sentence with no word of the trade in it:
no protocol, format, language or framework name, except the ones that person would say
themselves ("a Kindle book", "a PDF").

**The flow.** What happens when it is used, as three to five steps with their real names from the
repo: what goes in, what the tool does to it, what comes out.
`a Kindle book with a lock -> Anzu opens it -> an EPUB any reader takes`. This is what the hero
will show, so it has to be true: follow it in the code, do not guess it from the name.

**The kind.** How a person meets it: a screen, a terminal, a call from their own code, something
that works unseen inside another tool, a set of files. The kind decides the picture (step 3).

**The proof.** The number, before/after or real output that makes the sentence believable, said
the way that person would say it ("9 times out of 9", "half the size"). Use only facts the repo
backs (benchmarks, tests, real output). A hero with an invented number is worse than no hero.
When the repo measures nothing, or marks its numbers as old or as targets, the proof is its own
sample output and the hero carries no figure. In the hero the proof is one small figure beside
the step it proves, never a row of numbers.

Look for an existing identity (logo, wordmark, `DESIGN.md`, brand folder, site, design tokens,
badge colors) and reuse its colors, mark and rules. The accent is the one the identity declares;
when it declares none, take it from the mark. If there is no identity, pick one accent that suits
the subject; everything else is neutral. When the product has one theme only, derive the other:
the same hues, background and ink swapped, the accent darkened or lightened until text in it
passes contrast. The fonts are the skill's in every hero, whatever the brand uses; the one
exception is a wordmark the repo ships as a file, which is used as shapes.

When the repo already has a tagline that says this in plain words, keep it as the tagline. A
brand rule that cannot hold at hero size (interface text of 11 px) gives way to the sizes below;
its rules on color and on the mark always hold.

The hero speaks the language of the main README. Sample content may be shortened; it is never
something the tool would not produce, and it names no real third party (`example.com`, not a
real shop).

## 2. Logo: `assets/logo.svg`

If the repo has a mark, use it as it is, whatever its shape or detail: copy it to
`assets/logo.svg` (the variant made for light backgrounds, when there are two). From a lockup,
take the symbol and leave the wordmark out. A mark that exists only as a raster (`.ico`, `.png`)
is traced or redrawn as a faithful vector, never replaced with a new idea. Otherwise draw a
160×160 mark from the name, from what the tool does, or both: two or three thick shapes, ink plus
the accent, on a rounded square of the dark background. It has to survive 16 px, so no thin
strokes, no text, no detail.

## 3. Hero: `assets/hero.src.svg`

What is standard is the quality bar, never the composition. Two heroes made with this skill share
fonts and care and look nothing alike, because the tools are not alike.

### The four parts

Every hero has these, marked with these ids so the build can measure them:

```
<g id="logo">...</g>            the mark, drawn inline, its colors as palette roles so it holds in both themes
<text id="name">...</text>      the repository name in class b (a <g> of shapes when the repo ships a wordmark file)
<text id="tagline">...</text>   your sentence, shortened to one line of 12 words or fewer
<g id="stage">...</g>           the picture of the repository doing its job
```

**Logo and name are what the eye lands on first, and they do not shout.** They sit together
(within 64 px), still, with clear space around them. The name is the largest text on the canvas,
between 44 and 96 px; the logo is between 56 and 220 px on its shorter side. A name that fills the
canvas leaves no room for the picture, and a picture with a name lost in a corner belongs to
nobody. A mark too heavy to type is spliced in by a small script; keep the part you write by hand
as its own file next to the source.

**The stage explains.** It takes at least 30% of the canvas and usually more than half. Cover the
name and the tagline: the stage alone still says what the repository does.

### The picture

It comes from the kind of repository and the flow you wrote in step 1:

| The repository is | The stage shows |
|---|---|
| an app with a screen | that screen as a skeleton in its real layout and colours, with the one flow a person opens it for playing in it |
| a command-line tool | a small terminal with the one real command, and beside it what that command does in the world |
| a service, API or backend | one request followed through the flow: who calls, the steps inside, what it reaches, what comes back |
| a library or SDK | the shortest real call, and what those lines produce |
| a converter or pipeline | recognisable things going in one side and coming out the other, changed in plain sight |
| a plugin, hook or agent tool | the host it lives in, with the plugin acting at its place and the host showing the difference |
| a collection of files | the things in it, grouped as the repo groups them, and one being picked |

**Read the section for your kind in `references/pictures.md` before you draw.** It says what to
read in the repo, what to draw, what moves and the traps of that kind, and it has devices that
already pass the build: a connector with direction, a parcel between steps, a conveyor, a
cursor on a skeleton screen, a terminal that types.

Whatever the kind:

- **Every step of the flow is on the canvas the whole time**, in reading order, as an object a
  person recognises: a window, a box, a slot. What a step holds may arrive on its turn; the step
  itself never appears from nothing. Motion is what goes from one step to the next: a parcel, a
  cursor, a highlight.
- **Few things, drawn large.** A README shows the hero at two thirds of its size. Labels that
  name a step are 18 px or more and most text is 16 or more; what travels through the flow is
  24 px or more; a connector is 2 px or more and ends in an arrowhead. Three panels with one real
  line each say more than six panels of small print.
- **The picture works with every word blurred.** Shapes, direction and color say what goes in,
  what changes and what comes out; words only name things. The moment of change is the most
  interesting thing on the canvas, so it happens in plain sight.
- **Every word is one the viewer already knows.** A label names a thing in a few words. A real
  command, file name or term of the trade appears as texture, never as the explanation. No
  sentences besides the tagline: the README says the rest.
- **It looks like this product.** Its tokens, its screen, its mark. Sample content (a chat, a
  page, a list) is real content from the repo, large enough to recognise and short enough to
  take in while it passes.
- **Let the picture decide the layout**: full-bleed with the identity over a quiet corner,
  centered, stacked, split, one big object or many small ones. If you catch yourself drawing a
  headline on the left, a row of numbers under it, two cards on the right and a strip along the
  bottom, stop: that is a template, and it is the result this skill exists to avoid.

Before you build, write down what a person would say the repository does after seeing your stage
with the name and the tagline covered. When it does not match your sentence, draw a different
picture.

### Format

1280×640 (`viewBox="0 0 1280 640"`, `role="img"`, `aria-label` that tells the flow). The file
starts with a palette comment, and colors are written as `$role`; the build makes the dark and
light files from it:

```
<!--palette
bg     #0F1115 #F0F5FB
accent #4FD1C5 #0B7A70
-->
<svg ...><style>@keyframes ...</style> <rect fill="$bg" .../> ...
```

Roles are `name dark light`, in lowercase letters, digits and `_`; name your own, and repeat the
value for a color that is the same in both themes. Text uses one class per element: `s` (Space
Grotesk), `b` (Space Grotesk Bold) or `m` (JetBrains Mono, one weight). The build embeds the fonts and the reduced-motion rule, so write
neither. GitHub shows the file as an image at about 65% of its size: CSS only, no script, no
external file, no `<image>`, nothing under 13 px. Draw the logo inline.

### Motion

The hero is a place that is always running, never a video that starts and ends. **Read
`references/motion.md` before you write keyframes**: the rules, their sources, and what the build
measures. The ones that shape the drawing:

- **One thing leads**: what travels through the flow. Two or three things move at a time; the
  rest is still or nearly still.
- **A flow is a cycle of three to five beats** on one duration of 6 to 12 s. Each part takes its
  place in it with a negative `animation-delay` (in its class or inline), so the first frame is
  already mid-story. Ambient loops (walking dashes, a pulse, a caret) keep their own short
  durations.
- **The loop closes where it began.** First and last keyframes are equal, or the reset cannot be
  seen: content that repeats and travels exactly one period, a thing at opacity 0 at both ends or
  outside its clip. Things leave by finishing (a parcel fades on arrival), never by rewinding.
- **Draw the finished frame, then animate towards it.** With motion off, every step and its
  result are on the canvas, and that frame is what `look.png` shows. What exists only in transit
  (a parcel, a spark) carries `opacity="0"` as an attribute, which the animation overrides.
- **No moment is empty.** A result leaves just before the next one arrives in its place; results
  never clear all at once.
- **A change takes 0.2 to 0.5 s, and what must be read rests a second or more.** Ease arrivals
  out and departures in; `linear` is for what never stops (a conveyor, walking dashes).
- **Animate `transform` and `opacity`**, plus `stroke-dashoffset` for connector lines. Scale and
  rotation need `transform-box:fill-box;transform-origin:center`. An animated element has no
  `transform` attribute of its own: position it with a parent `<g>`.
- **Name, tagline and labels stay still.** Text that travels moves at a constant speed inside a
  `<g>`, 10-30 px/s for lines to read in passing, and the build turns it into outlines.

## 4. Build, measure, look

```
uv run <this skill>/scripts/build.py assets/hero.src.svg
```

Without `uv`: `pip install fonttools brotli`, then run it with `python`.

It writes `assets/hero-dark.svg` and `assets/hero-light.svg` and prints four things. Use all four.

1. **Errors and warnings**, each with its fix. They are measured on the canvas with the real
   fonts: text out of its box or over other text, sizes, contrast, loops that jump, motion too
   fast or too small. Fix every one by changing the drawing. When a warning is wrong for this
   hero, leave it and tell the user which one and why.
2. **`measured:`**, the figures of this hero: sizes of name, logo and tagline, the share of the
   canvas the picture takes, words, loop lengths, top speed.
3. **`pictures`**, two PNG files. Read both, every build:
   - `loop.png`: the loop stopped at eight moments. Follow the thing that leads from frame to
     frame: does it go through every step, in order? Is any frame empty or crowded? Does the last
     frame lead back into the first?
   - `look.png`: the finished frame (motion off) in both themes at README width, on a phone and
     blurred. Is the name the first thing you see? Is every step there with its result, and
     nothing left over from an earlier moment? Can you read the labels at this size? Does the
     blurred one still show what goes in and what comes out (when it looks empty, the shapes are too
     faint against the background)? Do shapes touch or overlap by
     accident, does anything that travels pass over a label? Did the light theme come out weak?
4. **`preview`**, a page with both files playing, for the user or a browser tool.

When the build says `no pictures`, open the pages it names with a browser tool; a hero nobody has
looked at is not finished. Repeat until the build is clean and the pictures show the flow. Keep
the source next to the two outputs.

## 5. Put it in the README

Add this as the first thing in `README.md`, and in each translated README. If a hero or banner
image is already there, replace it and leave its old files where they are. Touch nothing else.

```html
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <img src="assets/hero-light.svg" alt="{what the hero shows: the flow, with its figures}" width="100%">
  </picture>
</p>
```
