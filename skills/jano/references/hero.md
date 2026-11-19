# The hero

The hero is the picture at the very top of the README: a poster that moves. A person who has read
nothing yet looks at it and knows the name of the tool, what it is for, what is worth knowing
about it, and sees it doing its job. It uses the notes of step 1 in SKILL.md: the sentence, the
flow, the kind, the audience, the highlights, the key phrase, the strip and the brief.

## Options

When the user asks for options or alternatives, draw that many heroes to choose from (four when
no number is given). Step 1 of SKILL.md and the logo are done once, and every option shares that text block. Each
option is its own idea of the picture, not a recolour, and at least one sets text and picture
in another arrangement. Write them to `assets/options/a/hero.src.svg`, `b`, ... and build them
together with `build.py assets/options/*/hero.src.svg`, which adds a page that shows them side
by side; then look at each one as "Build, measure, look" says. When you can start agents, give each option its
own, with this file and your notes from step 1 of SKILL.md. Leave the README alone and show the user that
page: they keep one, or name what to take from several. Write the result as
`assets/hero.src.svg`, build it, and go on. Leave `assets/options/` to the user.

## Logo: `assets/logo.svg`

If the repo has a mark, use it as it is, whatever its shape or detail: copy it to
`assets/logo.svg` (the variant made for light backgrounds, when there are two). From a lockup,
take the symbol and leave the wordmark out. A mark that exists only as a raster (`.ico`, `.png`)
is traced or redrawn as a faithful vector, never replaced with a new idea.

A repository with no mark gets none: the name stands alone in the hero and this step is skipped.
Draw a mark only when the user asks for one: 160×160, from the name, from what the tool does, or
both, two or three thick shapes, ink plus the accent, on a rounded square of the dark
background. It has to survive 16 px, so no thin strokes, no text, no detail.

## Hero: `assets/hero.src.svg`

The hero is a poster. A poster has a text block that can be read in three seconds and a picture
that makes a person stay, and neither wins: a canvas that is all picture with a name lost in a
corner belongs to nobody, and a headline beside two big shapes explains nothing. What is standard
is the anatomy and the quality bar. The picture is never standard: two heroes made with this
skill share fonts, anatomy and care, and their pictures look nothing alike, because the tools are
not alike.

### The anatomy

Every hero has these parts, marked with these ids so the build can measure them:

```
<g id="backdrop">...</g>        a quiet pattern over the whole canvas, still or moving (left out when the backdrop is none)
<g id="logo">...</g>            the mark, drawn inline, its colors as palette roles (left out when the repo has none)
<text id="name">...</text>      the repository name in class b (a <g> of shapes when the repo ships a wordmark file)
<text id="tagline">...</text>   the key phrase, one or two lines; the second may be in the accent
<text id="about">...</text>     the description, one or two lines
<g id="facts">...</g>           the highlights: 1-4 figures with a label each, or 3-5 features taking turns (left out when nothing passes)
<g id="ticker">...</g>          a strip along the bottom edge where the facts of the strip run without stopping (left out when step 1 of SKILL.md kept none)
<g id="stage">...</g>           the picture of the repository doing its job
```

**Text and picture share the canvas, and the picture gets the larger part.** Logo, name, key
phrase, description and figures are one block, read from top to bottom, on one side of the canvas
(usually the left, or across the top when the picture is wide and low). The picture has the other
side to itself and may run off the edges of the canvas. They never overlap.

How much each takes follows from two needs, never from a quota. The text block needs a column
wide enough for the key phrase on two lines and the description at 40 to 60 characters a line,
which is 440 to 560 px; narrower and it breaks into a ragged stack, wider and the lines grow too
long to take in at a glance. The picture needs everything else, because it is shown at two
thirds of its size and its detail has to survive that. That usually lands near 40 / 60, between
35 / 65 and 45 / 55. A picture that is one tall object (a phone, a page) can give the text more;
a wide flow with many stations can take more and put the text block across the top. Only the
text block counts as text here: words inside the stage (a terminal's output, a reply, a label on
a card) are part of the picture. The build reports the two as `text / picture` and speaks up
only at the extremes; judge the balance in `look.png`, by eye: when you squint, neither side
disappears.

| Part | Size | Rule |
|---|---|---|
| logo + name | name 26-64 px, logo 32-160 px, within 64 px of each other | Together at the top of the block, still. They sign the poster; they do not lead it. |
| key phrase | 38-68 px, bold | The largest text on the canvas and the first thing read. |
| description | 18-26 px | Under the key phrase, in the body color. |
| highlights: figures | number 24-40 px and smaller than the key phrase, label 13-16 px | In a row. The strongest first, in the accent; a thin bar or mark under a number may show its proportion. One line under the row may say what they measure. One figure alone is fine, larger. |
| highlights: features | 18-24 px, with a small mark or icon | One at a time in one place, each resting 2 s or more, taking turns by sliding up or fading (device I); or a short list where a highlight walks down, lighting one at a time. Never more than five. |
| strip | 30-44 px tall, text 14-16 px in mono | Text that travels at 40-110 px/s behind a clip, written twice or more so the loop cannot be seen. Names in ink, values in the accent. |
| backdrop | whole canvas | Optional. A pattern that belongs to the subject (`kit.py backdrop`, or the brand's own texture), barely darker or lighter than the background, still or moving 4-10 px/s. Never a second picture. |

**The backdrop is chosen, not assumed.** A dot grid on every hero makes every README look alike,
so dots are the fallback, never the habit. Decide three things from the repository: whether there
is a backdrop at all (none, when the picture carries itself or the brand is plain), whether it
moves (a still pattern is fine; motion is for tools about flow, time or signals), and which
pattern fits the subject: `kit.py list` says what each one suits (grid for plans and maps, waves
for sound or streams, scan lines for terminals and text, rings for networks, chevrons for
pipelines and code...). When nothing fits, take the pick for this repository,
`kit.py backdrop --kind any --repo <name>`. Propose your choice to the user with its reason (in the
full run it is a question of step 2 and goes in the plan as `"backdrop"`; when only the hero was
asked for, ask it then). `kit.py backdrop --kind <kind> --motion <drift|slide|rise|still> --h 640`
prints the `<g id="backdrop">` and its keyframes; the scenes take the same one with `--h 448`. The
brand's own texture, drawn by hand, carries `data-backdrop="custom <motion>"` and the plan says the same.

The text block is still: nothing in it travels or fades, so it can be read at any moment. Inside
it only small things live (the mark moving within itself, a sheen on a figure's bar), and the
features, which take turns in their own place.

### The picture

**The stage explains.** Cover the text block: the stage alone still says what the repository
does. It comes from the kind of repository and the flow you wrote in step 1 of SKILL.md:

| The repository is | The stage shows |
|---|---|
| an app with a screen | that screen as a skeleton in its real layout and colours, where what a person opens it for changes in plain sight: the text before and after, the list that fills, the file that comes out. A cursor may lead the eye; clicks on a toolbar alone show nothing |
| a command-line tool | a small terminal with the one real command, and beside it what that command does in the world |
| a service, API or backend | one request followed through the flow: who calls, the steps inside, what it reaches, what comes back |
| a library or SDK | the shortest real call, and what those lines produce |
| a converter or pipeline | recognisable things going in one side and coming out the other, changed in plain sight |
| a plugin, hook or agent tool | the host it lives in, with the plugin acting at its place and the host showing the difference |
| a collection of files | the things in it, grouped as the repo groups them, and one being picked |

**Read the section for your kind in `references/pictures.md` before you draw.** It says what to
read in the repo, what to draw, what moves and the traps of that kind, and it has devices that
already pass the build: a connector with direction, a parcel between steps, a conveyor, a
cursor on a skeleton screen, a terminal that types, a strip of running text, a backdrop.

Whatever the kind:

- **Show an example, not a symbol of one.** The stage holds a real case from the repo with its
  content: the actual reply, the actual command and its output, the actual page, row or file,
  shortened. Two bars, two boxes or one big icon say that something is larger than something
  else and nothing about what the tool does; when a comparison is the point, it is drawn on the
  real things (the long reply and the short one, each with its count), never instead of them.
- **Three sizes of thing.** One or two large objects anchor the stage (a window, a page, a
  device, 140 px or more on the shorter side). Inside and around them are medium ones (cards,
  rows, panels) and many small ones (chips, counters, ticks, cursors, badges, skeleton lines).
  The large ones give the picture its shape from across the room; the small ones are what a
  person finds on a second look. Only large shapes read as empty; only small ones read as noise.
- **Every step of the flow is on the canvas the whole time**, in reading order, as an object a
  person recognises. What a step holds may arrive on its turn; the step itself never appears
  from nothing. Motion is what goes from one step to the next: a parcel, a cursor, a highlight.
- **It is alive in layers.** One thing leads (what travels through the flow). Around it, things
  follow (a counter that ticks, a row that lights, a bar that fills), and under it all the
  ambient layer never stops (the backdrop, the strip if any, walking dashes, a caret). Five or more
  things move in the stage, and no region of it sits still for the whole loop.
- **Readable at two thirds.** A README shows the hero at 65% of its size. Labels that name a
  step are 16 px or more; sample content is 14 to 16; nothing is under 13; what travels through
  the flow is 24 px or more; a connector is 2 px or more and ends in an arrowhead.
- **The picture works with every word blurred.** Shapes, direction and color say what goes in,
  what changes and what comes out. The moment of change is the most interesting thing on the
  canvas, so it happens in plain sight.
- **Every word is one the viewer already knows.** A label names a thing in a few words. No
  sentences in the stage besides the sample content itself: the text block says it, and the
  README says the rest. The stage holds about 48 words standing still, 10 to a line.
- **It looks like this product.** Its tokens, its screen, its mark.

Before you build, do two things. Write down what a person would say the repository does after
seeing your stage with the text block covered; when it does not match your sentence, draw a
different picture. Then cover the stage: the text block alone gives the name, what it is for and
why to believe it.

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

After the palette goes the brief from step 1 of SKILL.md, as a `<!--brief ... -->` comment in plain
lines; the preview page shows it and the outputs leave it out.

Roles are `name dark light`, in lowercase letters, digits and `_`; name your own, and repeat the
value for a color that is the same in both themes. Text uses one class per element: `s` (Space
Grotesk), `b` (Space Grotesk Bold) or `m` (JetBrains Mono, one weight). The build embeds the fonts and the reduced-motion rule, so write
neither. GitHub shows the file as an image at about 65% of its size: CSS only, no script, no
external file, no `<image>`, nothing under 13 px. Draw the logo inline.

### Motion

The hero is a place that is always running, never a video that starts and ends. **Read
`references/motion.md` before you write keyframes**: the rules, their sources, and what the build
measures. The ones that shape the drawing:

- **One thing leads**: what travels through the flow. Followers answer it one after another,
  and the ambient layer (backdrop, strip, dashes) stays low and constant. Many things move, and
  the eye still knows where to go, because only the lead is large, in the accent and travelling.
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
  `transform` attribute of its own: position it with a parent `<g>`, and keep its keyframes
  relative to that place (the build measures an element where its parent puts it).
- **The text block and the labels stay still.** Text that travels moves at a constant speed
  inside a `<g>`: 10-30 px/s for lines read in passing, 40-110 px/s for the strip. The build
  turns it into outlines.

## Build, measure, look

```
uv run <this skill>/scripts/build.py assets/hero.src.svg
```

Without `uv`: `pip install fonttools brotli`, then run it with `python`.

It writes `assets/hero-dark.svg`, `assets/hero-light.svg` and the social preview (below), and
prints four things. Use all four.

1. **Errors and warnings**, each with its fix. They are measured on the canvas with the real
   fonts: text out of its box or over other text, sizes, contrast, loops that jump, motion too
   fast or too small. Fix every one by changing the drawing. When a warning is wrong for this
   hero, leave it and tell the user which one and why.
2. **`measured:`**, the figures of this hero: sizes of name, logo and key phrase, the share of
   the canvas the picture takes, how many parts it has and how many move, text against picture,
   words, loop lengths, top speed.
3. **`pictures`**, two PNG files. Read both, every build:
   - `loop.png`: the loop stopped at eight moments. Follow the thing that leads from frame to
     frame: does it go through every step, in order? Is any frame empty or crowded? Does the last
     frame lead back into the first?
   - `look.png`: the finished frame (motion off) in both themes at README width, on a phone and
     blurred. Is the key phrase the first thing you read, and does the picture hold you next? Do
     text and picture weigh the same, or does one swallow the other? Is any part of the stage a
     large empty shape? Is every step there with its result, and nothing left over from an
     earlier moment? Can you read the labels at this size? Does the
     blurred one still show what goes in and what comes out (when it looks empty, the shapes are too
     faint against the background)? Do shapes touch or overlap by
     accident, does anything that travels pass over a label? Did the light theme come out weak?
4. **`preview`**, a page with both files playing, for the user or a browser tool.

When the build says `no pictures`, open the pages it names with a browser tool; a hero nobody has
looked at is not finished. Repeat until the build is clean and the pictures show the flow. Keep
the source next to the two outputs.

Then a cold read, once. You know the repo, so you cannot see the hero as a stranger does. When
you can start a fresh agent, give it only `look.png` and ask what the tool does and for whom.
When its answer misses your sentence, change the picture, not the words, and build again.
Without a fresh agent, cover the text block in `look.png` and answer the same question yourself.


## Put it in the README

The hero is the first thing in `README.md` and in each translated README. If a hero or banner
image is already there, replace it and leave its old files where they are. When only the hero
was asked for, touch nothing else.

```html
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <img src="assets/hero-light.svg" alt="{what the hero shows: the flow, with its figures}" width="100%">
  </picture>
</p>
```

## The social preview

Every build of `assets/hero.src.svg` also writes the card GitHub shows when the repository is
shared, so the two never drift apart. All of it goes in `assets/social-preview/`, one pair per
theme, so the user can choose:

- `social-preview-dark.svg` and `social-preview-light.svg`: the finished frame of the hero in
  that theme, still, scaled into the safe area of GitHub's template (80 px from every edge,
  where other sites crop) on the hero's background. They are the vectors the cards are made from.
- `social-preview-dark.png` and `social-preview-light.png`: each SVG shot at 1280×640,
  lossless, the size GitHub's template asks for and the format its setting takes (PNG, JPG or
  GIF under 1 MB).

Keep the folder next to the hero, and never edit its files: change the hero and build again.
The PNG files need the same browser as the pictures; with `--no-pictures` only the SVG files
are written. Look at both PNG files once: is the key phrase still the first thing you read at a
glance? GitHub takes one card and has no API for it, so the user uploads the one they choose by
hand: **Settings → General → Social preview → Edit → Upload an image**. `readme.py check` fails
when any of the four was built from another version of the hero.

Then tell the user, briefly: the brief (the sentence, the input and output with their files, the
source of each claim, what was left out as unfinished), whether the hero has a strip and why,
what the cold read said, any warning left and why, the preview page, and the social preview
with where to upload it.
