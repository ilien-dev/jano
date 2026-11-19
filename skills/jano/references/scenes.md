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
<g id="backdrop">...</g>   the hero's backdrop, the same pattern and motion (or none, when the plan says none)
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
- **Icons say what they mean, and are read cold.** See Parts, icons and assets, below.
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

## Parts, icons and assets

A scene is built from three kinds of pieces, in this order of preference:

- **Kit parts** (`scripts/kit.py`): window, terminal, card, chip, button, cursor, file, code,
  progress, toggle, badge, note, skeleton, device, backdrop. They are Jano's own, drawn the same
  way every time, sized to their real text and coloured by palette role. Use them for every
  interface element instead of drawing one by hand. Text in a box comes from one of them: `card
  --text` wraps a quote or a paragraph inside the card's padding and grows the card to fit, and
  `note` sizes a callout to its text with room for an icon on its left.
- **Library assets** (`scripts/assets.py`, `references/assets.md`): icons, objects, brand logos,
  flags and file icons from known sets, one family per category, the one the plan chose.
- **Your own drawing**, for what neither has: the subject of the scene itself.

**Everything in a box stays inside it, with room.** Text keeps half its size from the sides of a
pill and its full size from the sides of a panel (half above and below); a shape or an icon keeps
8 px from every edge (a share of the box when the box is small), or sits flush against it on
purpose. What moves is measured in its finished place. The build refuses text or shapes that run
out of their box or almost touch its edge. A character the fonts lack (⚠, ✓, ★) is refused too:
each machine draws it in another font and at another width, so it overflows where you cannot see
it. Draw it as an icon from the chosen family, beside the text.

Small icons carry a lot in a scene (cut, redo, a lock, an eye), and a home-made one at 24 px
easily turns into something else at README width: scissors drawn from scratch read as an arrow
with two balls, a circular arrow as a ring with a tail. So an icon starts from a known one and
is checked like everything else.

- **Start from the chosen family.** `assets.py search <repo> icons <words>` finds an icon by what
  it should mean; `assets.py get <repo> icons <name> "<what it means>" --x --y --size --color`
  prints the `<g>` to paste. It carries `data-asset` and `data-icon`.
- **Draw your own only when the family has nothing that fits**, in the family's manner: its
  grid, its stroke, its caps, few strokes, the thing's outline rather than its detail.
- **Every icon says what it means:** its `<g>` carries `data-icon="what it means"`. The build
  warns about a small drawing of thin strokes that does not, and about an icon under 24 px or
  with strokes under 2 px.
- **It is read cold.** `readme.py judge` cuts each declared icon out of its finished frame at the
  size a README shows it and the blind judge says what it sees. An icon that is misread is
  rebuilt (another icon from the set, larger, or a clearer drawing), never just removed: the
  icon is there because the scene needs it.

**The cursor turns into a pointer.** A cursor shows what a person would see: an arrow while it
moves, a pointing hand over something clickable (a button, a link, an option, a toggle), a text
bar over a field being typed in. Mark clickable parts with `data-clickable="true"` (kit buttons
and toggles already are) and use `kit.py cursor-swap` with the moments the cursor hovers them;
the build warns about an arrow that crosses a clickable part and never changes. The cursor's
style is free: draw your own in the scene's manner, keeping `data-kit="cursor"` and
`data-cursor="arrow|pointer|text"`.

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
