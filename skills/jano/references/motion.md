# Motion: the rules, where they come from, and what the build measures

These are the practices of people who animate SVG and interfaces for a living, turned into rules
for a README hero. Each one names its source (listed at the end). The last section lists what the
build measures, so you know which rules are checked for you and which you check with your eyes.

## Plan it before you write it

1. **Write a timing chart first.** One line per moving part, with where it starts and stops in
   the loop, as a comment above the keyframes. Parts that follow each other, overlap or run in
   parallel are then visible before any keyframe exists. [timing-charts]

   ```
   /* 8 s  cursor  |--go--|=====rest=====|--home--|
            button         |press|
            result               |-in-|====shown====|out| */
   ```

2. **One story, one duration.** Write each keyframe set against the whole loop and give every part
   the same `animation-duration`. Shift a part with a negative `animation-delay` of
   `start - duration`: it shows the right phase from the first frame and never waits. Two
   durations that are not multiples drift apart within a minute. The same negative delay on every
   part shifts the whole story, which is how you choose the moment the first frame shows.
   Ambient loops (walking dashes, a pulse, a caret) are not part of the story and keep their own
   short durations. [field-guide §6.3]

3. **Author the finished frame.** Draw every element in the state it has when the story is
   complete, at full opacity and in its final place, and let keyframes hide or move it earlier in
   the loop. People who turn motion off (and the first paint) then see a whole picture, never an
   empty stage. The two exceptions carry `opacity="0"` as an attribute, which a running animation
   overrides: what exists only in transit (a parcel), and what belongs to an earlier moment (the
   "before" of a before and after). [field-guide §6.2] [svgweave]

## Staging: where the eye goes

4. **One thing leads, in three layers.** The lead is what travels through the flow: large, in
   the accent, the only thing that crosses the stage. Followers answer it in turn (a counter, a
   row that lights, a bar that fills). The ambient layer never stops and never asks to be looked
   at (the backdrop, the strip, walking dashes, a caret). A poster where only two things move
   looks switched off; one where eight things lead at once has nowhere for the eye to land.
   [field-guide §7] [12-principles]
5. **A follower starts after its leader is mostly done** (about 60% through), never at the same
   instant. That is what makes one thing read as the cause of the next. [12-principles]
6. **Ambient motion stays low**: a drift of a few pixels, a pulse between 0.55 and 1 opacity, a
   period of 3 s or more. Motion that is seen all day is subtle. [nng]
7. **Motion carries information.** A name with confetti is a business card. A parcel that crosses
   from the caller to the server is an explanation. If a movement can be removed without losing
   meaning, remove it. [field-guide §1]

## Time and easing

8. **A change takes 0.2 to 0.5 s; a journey takes longer the farther it goes.** Interface
   research puts a single change at 100-500 ms and says too long is the more common mistake.
   A parcel crossing 200 px takes about a second; one crossing the canvas, two or three. Nothing
   bounces. [nng] [material] [carbon] [field-guide §7]
9. **Hold what must be read.** After something arrives it rests at least a second; a state with
   a label rests three or more. A viewer needs about a second to find a thing and more to read
   it. [field-guide §7]
10. **Ease by role.** Arriving: decelerate, `cubic-bezier(0,0,.2,1)`. Leaving: accelerate,
    `cubic-bezier(.4,0,1,1)`. Moving from one place to another in view:
    `cubic-bezier(.4,0,.2,1)`. `linear` only for what never stops: a conveyor, a ticker, a spin,
    walking dashes. Easing applies between each pair of keyframes, and
    `animation-timing-function` inside a keyframe sets it for the stretch that follows.
    [material] [carbon] [svgweave]
11. **The loop length follows the story.** Three to five beats fit in 6 to 12 s. A loop nobody
    sees the end of explains nothing. [field-guide §7]

## Closing the loop

12. **The first and last keyframes are the same state** (`0%,100%{...}`), or the reset cannot be
    seen. The ways a reset hides: the content repeats and travels exactly one period; the thing is
    at opacity 0 at both ends; it starts and ends outside the canvas or its clip; it turns whole
    turns. [svgweave] [field-guide §6.9]
13. **Things leave by finishing**, never by rewinding: a parcel fades on arrival, a result fades
    while the cursor goes home. A drawing that visibly un-draws itself reads as a video
    restarting. A flow that fills something up (a list, a store, a page) empties by handing over:
    each result goes just before the next one lands in its place, so no moment shows the whole
    picture blank.
14. **Walking dashes move by one dash period.** `stroke-dashoffset` travels the sum of
    `stroke-dasharray` (twice the sum when the list has an odd count), or a multiple.

## What stays smooth

15. **Animate `transform` and `opacity`.** The browser moves and fades finished layers without
    redrawing them. Geometry (`x`, `width`, `r`, `d`) forces layout on every frame and does not
    animate in every browser; colours, strokes and filters are repainted on every frame.
    To change a colour, cross-fade two layers. [web.dev] [using-svg] [cssvg]
16. **`stroke-dashoffset` is the accepted exception**, for a few thin connector lines. It
    repaints, so keep those lines few and short. [cssvg]
17. **Give scale and rotation a pivot**: `transform-box:fill-box;transform-origin:center` (or
    `0 50%` to grow from the left). Without it an SVG element turns around the corner of the
    canvas. A `<g>` pivots on the union of its children, so adding a child moves the pivot.
    [svgweave]
18. **An animated element carries no `transform` attribute of its own**: the animation replaces
    it and the element jumps to the origin. Position it with a parent `<g>`.
19. **Keep still what is expensive**: filters, blurs, masks with gradients, large translucent
    shapes. Prefer a clip to a mask and a solid shape to a translucent one where either works.
    Never animate something that has a filter. [using-svg]
20. **Reuse shapes with `<use>`** and group what moves together under one `<g>`, in the order it
    is drawn, with a comment per part. Fewer points and fewer nodes are a smaller file and a
    smoother loop. [smashing-optimising]

## Safety

21. **No flashing.** Nothing goes from dark to light and back more than three times a second;
    large areas do not blink at all. A pulse slower than once a second reads as alive, a faster
    one as an alarm. [wcag-2.3.1]
22. **Reduced motion gets the whole picture.** The build adds
    `@media (prefers-reduced-motion:reduce){*{animation:none!important}}`; rule 3 is what makes
    the result complete. SMIL (`<animate>`) ignores that rule, so use CSS. [wcag-2.2.2] [svgweave]

## Text

23. **The hero shows; the README tells.** No paragraph on the canvas. A label names a thing in a
    few words. If a scene needs a sentence to be understood, it is not showing enough: add the
    motion, not the caption. [field-guide §5]
24. **Text that travels becomes outlines** (the build does it), because live text snaps to whole
    pixels and crawls. Typing is done by sliding a cover off still text in `steps()`, one step
    per character. [field-guide §6.1, §6.4]

## What GitHub allows

A README image is a restricted document. CSS `@keyframes` in a `<style>` block, inline
`style="animation-delay:..."`, `<use>`, `<clipPath>`, `<mask>`, `<pattern>`, gradients and
`prefers-reduced-motion` all work. Scripts, external fonts, stylesheets and images, anything
fetched from the network, and hover or click do not. [field-guide §2]

## What the build measures

Errors stop the build. Warnings are printed with the fix.

| Measured | Limit |
|---|---|
| `id="name"`, `id="tagline"`, `id="stage"` exist; name, key phrase and description are not animated | error |
| `id="about"`, `id="backdrop"` exist (`#facts` and `#ticker` are optional) | warning |
| Name size | 26-64 px, at most 45% of the canvas width |
| Logo (when there is one), shorter side | 32-160 px, within 64 px of the name |
| Key phrase (`#tagline`) | 38-68 px, the largest text on the canvas, 10 words or fewer |
| Description (`#about`) | 18-26 px, 8 to 24 words |
| Highlights (`#facts`) | at most 4 figures of 24 px or more; features take turns instead of standing as a block |
| Strip (`#ticker`), when there is one | text that travels in it |
| Background (`#backdrop`) | something in it is animated |
| Picture (`#stage`), what can be seen of it | 34% of the canvas or more |
| Text block against text block + picture (words in the picture count as picture) | reported; a warning under 25% or over 55%, and when the two overlap |
| Parts of the picture | 24 or more; one 140 px or more on its shorter side; 6 or more of 48 px or less |
| Things that move in the picture | 5 or more |
| Text size | 13 px or more, and at most half of the lines under 16 px; 7 sizes or fewer |
| Text and the canvas | off the canvas: error; closer than 24 px to its edge: warning |
| Text and its box | out of the box, or closer to its sides than half the text's size in a pill (8 px at least) or its full size in a panel (half above and below): error |
| Shapes and icons in a box | out of the box (most of it inside): error; 1 to 8 px from an edge (a share of a small box): error; flush is fine |
| Characters the fonts lack (⚠, ✓, ★) | error: counted 1.25 em wide, and drawn in another font on each machine |
| Text over text (two texts that take turns by fading are exempt) | error |
| Contrast of text on what is behind it, both themes | 4.5, or 3 for large text |
| Words standing still in the picture | 48 in all, 10 in one line |
| Strokes | 1 px or more |
| Animated properties | `transform`, `opacity`, `stroke-dashoffset`, `offset-distance`; geometry: error |
| Loop closes: equal ends, a repeat, hidden ends or whole turns | travel that jumps back in view: error |
| Dash travel | a multiple of the dash period: error |
| Animated element with a `transform` attribute | error |
| Scale or rotation without `transform-origin` | warning |
| Travel, scale, turn, fade too small to see | 6 px, 3%, 2 degrees, 0.12 |
| Speed | 700 px/s; 130 px/s for text |
| A move shorter than 100 ms | warning |
| Flashing | more than 3 a second: error; more than 1: warning |
| Loop duration | 0.4-60 s |
| Stories with steps on different durations | warning |
| Something in the stage travels 40 px or changes in steps | warning |
| The largest thing that travels | 20 px or more on its shorter side (draw it at 24 or more) |
| A connector with walking dashes | 2 px or more, contrast 3 against the background in both themes |
| Something that exists only in transit, visible when motion is off | warning: give it `opacity="0"` |
| SMIL, positive delays, filters on animated elements | warning |
| File size | 200 KB |

Speed along an `offset-path` is not measured; keep it under the limit yourself.

What it cannot measure, and you check in the pictures: whether the picture says what the
repository does, whether it shows a real example or only two shapes that stand for one, whether
text and picture weigh the same to the eye, whether a step is missing, whether two shapes touch by accident, whether
something that travels passes over a label, whether a panel sits empty for most of the loop,
whether the finished frame tells the story, whether panels and bars stand out from the
background in both themes (the blurred picture shows it).

## Sources

- [field-guide] Chan Meng, *Animated SVG Project Cards for a GitHub README: A Field Guide* (2026). https://chanmeng.org/blog/animated-svg-project-cards
- [timing-charts] Smashing Magazine, *Timing Charts: A Blueprint For SMIL Animations* (2026). https://www.smashingmagazine.com/2026/08/timing-charts-blueprint-smil-animations/
- [smashing-optimising] Andy Clarke, *Smashing Animations Part 4: Optimising SVGs* (2025). https://www.smashingmagazine.com/2025/06/smashing-animations-part-4-optimising-svgs/
- [using-svg] Amelia Bellamy-Royds, Kurt Cagle, Dudley Storey, *Using SVG with CSS3 and HTML5*, "Planning for Performance". https://oreillymedia.github.io/Using_SVG/extras/ch19-performance.html
- [web.dev] *How to create high-performance CSS animations*. https://web.dev/articles/animations-guide
- [cssvg] *SVG Animation Performance: How to Keep Animations at 60fps* (2026). https://cssvg.com/blog/svg-animation-performance
- [svgweave] *CSS @keyframes for SVG: a practical guide*. https://svgweave.com/blog/css-keyframes-svg-guide
- [nng] Nielsen Norman Group, *Executing UX Animations: Duration and Motion Characteristics*. https://www.nngroup.com/articles/animation-duration/
- [material] Material Design, *Duration & easing*. https://m1.material.io/motion/duration-easing.html
- [carbon] IBM Carbon Design System, *Motion*. https://carbondesignsystem.com/elements/motion/overview/
- [12-principles] *The 12 Principles of Animation Adapted to UI* (after Thomas and Johnston, *The Illusion of Life*). https://uiuxatlas.com/lessons/motion/the-12-principles-of-animation-adapted-to-ui/
- [wcag-2.3.1] W3C, *Understanding SC 2.3.1: Three Flashes or Below Threshold*. https://www.w3.org/WAI/WCAG21/Understanding/three-flashes-or-below-threshold.html
- [wcag-2.2.2] W3C, *Understanding SC 2.2.2: Pause, Stop, Hide*. https://www.w3.org/WAI/WCAG21/Understanding/pause-stop-hide
