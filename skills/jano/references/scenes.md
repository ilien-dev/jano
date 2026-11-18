# Scenes: a picture over each section that needs one

A scene sits right under a section's heading and explains that section before its text is read.
It is the hero's little sibling: the same palette, fonts, backdrop and care, on a shorter canvas,
with one job. Where the hero says what the whole repository is, a scene says one thing about it:
what you get, how one step works, what install looks like, who it is for.

Read `motion.md` and the devices in `pictures.md` before drawing: what they say about the hero
holds for scenes, with the differences below.

## The anatomy

1280×448 (`viewBox="0 0 1280 448"`), `role="img"`, an `aria-label` that tells what happens in
it, the palette comment first, the same classes `s`, `b`, `m`. The file is
`assets/readme/<name>.src.svg`; the build writes `<name>-dark.svg` and `<name>-light.svg` beside it.

```
<g id="backdrop">...</g>   the hero's backdrop, the same pattern and drift: the README reads as one piece
<text id="eyebrow">        the section's name, 13-18 px, mono or bold, in the accent, letter-spaced (optional)
<text id="title">          what the section claims, 34-56 px bold, 8 words or fewer: the largest text on the scene
<text id="sub">            one line under it, 16-24 px, 3 to 18 words (optional)
<g id="stage">...</g>      the picture: at least 45% of the canvas
```

The text block sits top left (eyebrow near y 56, title near y 108, sub near y 146) and the
picture takes the rest: the right side and the band under the text. A wide scene may put the
text block in a column on the left and give the picture everything right of it. Text and picture
never overlap, and the title is not a heading repeated: it is the claim ("Three commands, then
it runs", not "Install").

## What a scene shows, by role

A scene shows **one** thing, and never what another picture already shows. `readme.py check`
compares what each picture draws (its words and large shapes, and "shows" in the plan) and
refuses two that share half of it. The hero shows the whole flow; so a scene zooms into one part
of it, or shows what the hero has no room for.

| Role | The scene shows |
|---|---|
| demo | a real case, larger than the hero can show it: the actual input and the actual output side by side, and the moment one becomes the other |
| features | the features as places on one stage (the parts of a window, rooms of a house, stops on a path), lit one at a time, with a card that names the lit one in a few words |
| how | the inside of the step the hero passes over fastest, or the steps as stations on a path that what travels passes through, each doing its part as it arrives |
| audience | two to four people in their situation, each with what they get from it |
| install | a terminal that types the real commands, and beside it what each command sets up, ending with the tool ready |
| use | the first real use: what the person types or clicks, and what comes back |
| results | the measured numbers drawn on the real things they measure, counting up, each with where it comes from |
| compare | the same task on two lanes, the alternative and this tool, honestly |
| privacy | where the data goes: the person's machine as a place, data that stays inside its walls |
| about | the name and what it means, drawn from the mark |

Roles that are read rather than looked at (reference, FAQ, limits, licence, contributing,
develop) take no scene.

## What the cold read taught

- **Name things by their real names.** A page drawn as lines is "a document"; a page labelled
  `CLAUDE.md` is the file the section is about. Put the real name on every object a stranger has
  to recognise: the file, the command, the stage, the verdict.
- **Show the cause, and let it rest.** When one thing makes another happen (a right answer moves
  a mistake up, a check turns a card green), the cause is on the canvas while the effect happens
  and stays a second or more. A cause that flies past between two frames is never seen.
- **No tiny pictograms.** Scissors, an eye, a gear drawn in thin lines under 40 px turn into
  something else at README width (a pair of scissors became an arrow with two balls). Name the
  thing in a word, or draw it 48 px or more with filled shapes; the build warns about the rest.
- **Draw only what exists.** A command, flag or label on a scene is one the repository really has;
  `readme.py check` refuses a picture that shows `<name> <word>` when no Markdown file of the
  repository mentions it.
- **Leave out what only the README explains.** A count or a label that needs a sentence to make
  sense ("4 of 6 talks") confuses more than it shows; draw it, or leave it to the text.

## Alive, like a small game

A scene is a place where something is always happening, not a diagram with a dot on it. Plan it
as a story of three to six beats on one cycle of 8 to 24 s: something arrives, the
section's thing happens to it, the result appears, a card or a counter answers, and the place resets without
a visible jump. One thing leads (what travels through the flow), followers answer it, the backdrop
and small details never stop. Steps of a story may be held keyframes or `steps()` timing, as in
a sprite: what changes in steps changes in clear, readable jumps, and rests a second or more.

The rules of `motion.md` hold: the text block is still, loops close, the finished frame with
motion off shows the whole story at its end state, and nothing flashes.

## A real screenshot, only when it explains more

The scenes are drawn. When the project has a screen and the user agreed in step 2 (the plan has
`"captures_agreed": true`), one scene may hold a real screenshot instead of a skeleton, where a
drawing would explain less: a demo of an app the reader will use. It is still a scene: the same
title, backdrop and motion around it.

Take it from the running app (start its dev server and shoot the page with a browser tool), crop
it to the part the section is about, save it as WebP or JPEG, and embed it in a drawn frame (a
window, a phone) as `<image href="data:image/webp;base64,..." width=".." height=".."/>`. Animate
what is drawn on top of it: a cursor, a ring on what changes, a label that points. Keep it under
400 KB; the build warns past that. In the plan, the scene's `"type"` is `"capture"`.

## Build and look

```
uv run <this skill>/scripts/build.py assets/readme/*.src.svg
```

The build checks a scene as it checks the hero (sizes, overflow, contrast, loops), with the
scene's anatomy and canvas. Read `loop.png` and `look.png` of every scene: does the picture alone
say the claim of the plan? Is it a different picture from the hero and from every other scene?
Is the cause of each change on the canvas when it happens?
