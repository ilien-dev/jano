# The picture, by kind of repository

The stage shows the repository doing its job. Find your kind below, read in the repo what that
section names, and draw that. A repository that is two kinds (a CLI that starts a web app) is
drawn as the one a person meets first, with the other as a step in the flow.

Whatever the kind, the picture is built from the flow you wrote in step 1: what goes in, the steps
it passes through, what comes out. Every step is on the canvas the whole time, in reading order
(left to right, or top to bottom), and motion is what goes from one step to the next.

The stage has about 60% of the canvas, beside or under the text block. Fill it in three sizes:
one or two large objects that hold the scene, medium ones inside them, and small details that
carry real content (a count on a card, a chip with a real word, a badge, a progress tick). The
two failures to avoid are the same in every kind: two big shapes with a label each, which say
nothing, and a crowd of equal small things, which says nothing either.

## An app with a screen (web, mobile, desktop, extension popup)

**Read:** the main view's component and its styles, the design tokens (`tokens.css`,
`globals.css`, a Tailwind or theme config), screenshots in the README or docs, the strings of the
interface.

**Draw:** that screen as a skeleton. Keep what makes it recognisable: the real layout (sidebar,
header, list, canvas, player), the real colours, the real corner radius, one or two real labels.
Replace the rest with blocks: a line of text becomes a rounded bar, an avatar a circle, an image
a tinted rectangle. A phone app sits in a phone outline, a desktop app in a window with its title
bar, an extension in the corner of a page.

**Move:** the one flow a person opens the app for, as a cycle of three to five beats. A cursor
(or a tap ring on a phone) goes to the control, the control reacts, the result appears where the
app would show it, and the cycle closes while the cursor returns. Only the parts that take part in
that flow move.

The result is real content, large enough to read: the paragraph before and after, the rows that
fill, the file that comes out. It is what the viewer remembers; the cursor only leads to it.

**Traps:** drawing every panel of the app (keep the one flow); a screenshot traced in full detail
(it turns to noise at README width); a generic dashboard that could be any product; a cursor
clicking through menus and toolbars while the content stays the same (it shows the interface,
not what the app does).

## A command-line tool

**Read:** the README's usage section, the `--help` text, the argument parser, a test that shows
real output.

**Draw:** two things side by side. A terminal window, small and recognisable, with the one real
command a person types first and two to four lines of its real output, shortened. And, larger,
what that command does in the world, drawn as objects: the files it writes, the folder it tidies,
the server it starts, the report it prints. The terminal says "you type this"; the objects say
"and this happens".

**Move:** the command is typed (device F), the output lines appear in order, and each line sets
off its effect on the objects: a file appears, a bar fills, a parcel leaves for the server.

**Traps:** a terminal full of output and nothing else (a person who cannot read the output learns
nothing); invented commands or flags; more than one command.

## A service, API, server or backend

**Read:** the entry point and its routes or handlers, the architecture section of the docs, the
config that names what it talks to (database, queue, other services), a sequence in the tests.

**Draw:** the flow as a diagram with real names. On one side who calls it (an app, a browser,
another service, a schedule). In the middle the service, as a box that shows its inner steps when
they are the point (check, queue, store, answer). On the other side what it reaches (a database,
a model, the web, a device). Each box is a simple object a person recognises, with a label of one
to three words.

**Move:** one request, followed from end to end. A parcel leaves the caller, crosses to the
service, each inner step lights as the parcel passes it, something goes on to what it reaches, and
an answer comes back changed: a different colour, a tick, a smaller size. Connectors carry quiet
moving dashes (device A) all the time, so the direction reads even between parcels.

**Traps:** a box-and-arrow chart where nothing travels; more than six boxes; arrows that cross;
protocol names as the only labels.

## A library, SDK or framework

**Read:** the quick start, the first example in the docs, the public functions most used in the
tests.

**Draw:** the shortest real call, three to six lines of code in a small editor, beside what those
lines produce: the chart drawn, the form validated, the request retried, the shape of the data
before and after. The code is texture that says "you write this much"; the result is the picture.

**Move:** a highlight walks down the lines of code, and each line produces its part of the result.

**Traps:** a wall of code; a list of features; the result missing because "it depends on the
user".

## A converter, pipeline or data tool

**Read:** the input and output formats, one sample file of each, the stages in the code.

**Draw:** a journey. Recognisable things come in on one side (books, photos, rows, logs), pass
through the tool in the middle, and leave on the other side visibly changed. When there are
stages, each stage is a station on the way.

**Move:** a conveyor (device C): things arrive at a constant pace, change at the tool, and leave.
The moment of change happens in plain sight.

**Traps:** input and output that look the same; the tool drawn as an unexplained box.

## A plugin, hook, extension or tool for an agent

**Read:** where it attaches (the manifest, the hook names, the host's config), what triggers it,
what it changes in the host.

**Draw:** a scene. The host it lives in (an editor, a browser, a chat with an assistant, a build)
drawn as a skeleton, and the plugin as one actor inside it, in the accent colour, at the exact
place where it acts.

**Move:** the trigger happens in the host, the plugin acts, the host shows the difference. When
the difference is the point, show the same moment without it and with it, side by side or taking
turns.

When the host shows nothing of it (a skill that works inside a chat and has no surface of its
own), draw its flow as a journey instead, with what the person hands the assistant as the first
step and what they get back as the last.

**Traps:** the plugin alone, with no host; the host drawn in such detail that the plugin is lost.

## A tool whose point is a number (faster, smaller, cheaper, more)

**Draw:** the kind above that fits the tool, with the quantity shown on the real things: the
long output and the short one, each with its count; the slow run and the fast one, each with its
clock. The measured figures go in the text block (`#facts`), where they are read. Two bars alone
are never the picture: they say how much and nothing about of what.

**Move:** both run, one finishes first; or one stack grows while the other stays small.

## A collection (list, dataset, templates, docs, examples)

**Read:** how it is organised (sections, categories, counts) and three real entries.

**Draw:** the things in it, as a shelf, a grid or a set of cards, grouped as the repository groups
them, with real names on a few. A hand, a cursor or a search box picks one, and it opens.

**Move:** the shelf drifts slowly; one item at a time is picked and shown larger.

---

# Devices

Small pieces that pass the build's checks as written. Colours are palette roles; change sizes,
positions and timing to suit your picture. One story runs on **one duration**, and each part gets
its place in it from a negative `animation-delay` (`start - duration`).

### A. A connector that shows direction

Dashes that walk along a line. The offset moves by exactly one dash period (8 + 16 = 24), or the
line jumps. The line is 2 px or more and clearly visible on the background, and it ends in a still
arrowhead, so the direction also reads when nothing moves.

```svg
<style>
@keyframes flow{to{stroke-dashoffset:-24}}
.flow{animation:flow 1.2s linear infinite}
</style>
<path class="flow" d="M320 320H512" fill="none" stroke="$muted" stroke-width="2" stroke-dasharray="8 16"/>
<path d="M510 312l10 8-10 8" fill="none" stroke="$muted" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
```

### B. A parcel that goes from one step to the next

It fades in at the start, travels, and fades out on arrival, so nothing snaps back. It exists only
in transit, so it carries `opacity="0"` as an attribute: the animation overrides it while it runs,
and with motion off the parcel is not left frozen on the line. Make it 24 px or more: it is the
lead, and a README shows it at two thirds of that. The keyframes
are written once, for a 6 s story where each crossing takes about a second; the second parcel
starts 2 s later (`2 - 6 = -4s`). The box it reaches lights up as it lands.

```svg
<style>
@keyframes hop{0%{transform:translateX(0);opacity:0}3%{opacity:1}19%{transform:translateX(200px);opacity:1}23%,100%{transform:translateX(200px);opacity:0}}
@keyframes lit{0%,17%{opacity:.4}23%,45%{opacity:1}60%,100%{opacity:.4}}
.hop{animation:hop 6s cubic-bezier(.4,0,.2,1) infinite}
.lit{animation:lit 6s ease-in-out infinite}
</style>
<g transform="translate(320 306)"><rect class="hop" opacity="0" width="28" height="28" rx="6" fill="$accent"/></g>
<rect class="lit" x="548" y="270" width="120" height="100" rx="14" fill="$panel" stroke="$accent" stroke-width="2"/>
<g transform="translate(668 306)"><rect class="hop" opacity="0" style="animation-delay:-4s" width="28" height="28" rx="6" fill="$accent"/></g>
```

### C. A conveyor

The same thing drawn at a regular spacing, moved by exactly one spacing, behind a clip. Draw one
more item than fits, so the row is full at both ends of the move.

```svg
<style>
@keyframes belt{to{transform:translateX(96px)}}
.belt{animation:belt 3s linear infinite}
</style>
<defs>
<g id="doc"><rect width="48" height="60" rx="8" fill="$panel"/><rect x="10" y="14" width="28" height="4" rx="2" fill="$muted"/><rect x="10" y="26" width="20" height="4" rx="2" fill="$muted"/></g>
<clipPath id="lane"><rect x="80" y="280" width="384" height="80"/></clipPath>
</defs>
<g clip-path="url(#lane)"><g class="belt">
<use href="#doc" x="-80" y="290"/><use href="#doc" x="16" y="290"/><use href="#doc" x="112" y="290"/><use href="#doc" x="208" y="290"/><use href="#doc" x="304" y="290"/><use href="#doc" x="400" y="290"/>
</g></g>
```

### D. Two states that take turns (before and after)

Two drawings in the same place, cross-faded with holds. Both are written at full opacity, so the
picture is complete when motion is off: put the "after" state last, it is the one that stays.

```svg
<style>
@keyframes first{0%,40%{opacity:1}48%,92%{opacity:0}100%{opacity:1}}
@keyframes second{0%,40%{opacity:0}48%,92%{opacity:1}100%{opacity:0}}
.first{animation:first 8s ease-in-out infinite}
.second{animation:second 8s ease-in-out infinite}
</style>
<g class="first"><rect x="760" y="270" width="160" height="100" rx="14" fill="$panel"/><rect x="780" y="296" width="120" height="8" rx="4" fill="$muted"/><rect x="780" y="316" width="96" height="8" rx="4" fill="$muted"/><rect x="780" y="336" width="110" height="8" rx="4" fill="$muted"/></g>
<g class="second"><rect x="760" y="270" width="160" height="100" rx="14" fill="$panel"/><rect x="780" y="316" width="72" height="8" rx="4" fill="$accent"/></g>
```

### E. A screen as a skeleton, with a cursor that uses it

The cursor goes to the button and rests, the button dips, the result rises into place, and the
cycle closes while the cursor goes home. Every part shares the 8 s duration. The cursor is drawn
large (35 px tall): it is what the eye follows. A result that fades out to close the cycle leaves
its place empty for a moment; when several results do it at once the screen goes blank, so let
each one go just before the next arrives, never all together.

```svg
<style>
@keyframes cursor{0%,8%{transform:translate(0,0)}26%,62%{transform:translate(-150px,-70px)}84%,100%{transform:translate(0,0)}}
@keyframes press{0%,27%{transform:scale(1)}30%{transform:scale(.92)}34%,100%{transform:scale(1)}}
@keyframes arrive{0%,32%{opacity:0;transform:translateY(14px)}40%,84%{opacity:1;transform:translateY(0)}92%,100%{opacity:0;transform:translateY(14px)}}
.cursor{animation:cursor 8s cubic-bezier(.4,0,.2,1) infinite}
.press{animation:press 8s ease-out infinite;transform-box:fill-box;transform-origin:center}
.arrive{animation:arrive 8s cubic-bezier(0,0,.2,1) infinite}
</style>
<rect x="700" y="150" width="480" height="340" rx="18" fill="$panel"/>
<rect x="700" y="150" width="120" height="340" rx="18" fill="$line"/>
<rect x="720" y="180" width="80" height="10" rx="5" fill="$muted"/><rect x="720" y="206" width="60" height="10" rx="5" fill="$muted"/>
<rect class="press" x="848" y="180" width="110" height="36" rx="10" fill="$accent"/>
<g class="arrive"><rect x="848" y="244" width="300" height="64" rx="12" fill="$bg"/><rect x="866" y="262" width="150" height="10" rx="5" fill="$ink"/><rect x="866" y="282" width="210" height="8" rx="4" fill="$muted"/></g>
<g transform="translate(1060 276)"><path class="cursor" d="M0 0l0 35 10-8 6 16 6-3-6-14 13 0z" fill="$ink" stroke="$bg" stroke-width="2"/></g>
```

### F. A terminal that types its command

The text does not animate. A cover in the terminal's colour slides off it one character at a time
(`steps`, one step per character: 18 characters of 16 px mono are 18 x 9.6 = 173 px), rests, and
slides back as the cycle closes. The cover is drawn where it rests, off the text, and the
keyframes bring it back over the command: with motion off the command is there to read. Anything
revealed by a cover is drawn this way. The output appears once the command is typed. The caret blinks
with `steps(1,end)` between equal first and last keyframes.

```svg
<style>
@keyframes type{0%,6%{transform:translateX(-173px);animation-timing-function:steps(18,end)}28%,90%{transform:translateX(0);animation-timing-function:steps(18,end)}100%{transform:translateX(-173px)}}
@keyframes out{0%,32%{opacity:0}36%,90%{opacity:1}96%,100%{opacity:0}}
@keyframes caret{0%,100%{opacity:1}50%{opacity:0}}
.type{animation:type 8s linear infinite}
.out{animation:out 8s ease-out infinite}
.caret{animation:caret 1.1s steps(1,end) infinite}
</style>
<defs><clipPath id="row"><rect x="112" y="296" width="300" height="28"/></clipPath></defs>
<rect x="80" y="240" width="380" height="180" rx="14" fill="$panel"/>
<circle cx="104" cy="262" r="5" fill="$muted"/><circle cx="122" cy="262" r="5" fill="$muted"/><circle cx="140" cy="262" r="5" fill="$muted"/>
<text class="m" x="100" y="316" font-size="16" fill="$accent">$</text>
<text class="m" x="120" y="316" font-size="16" fill="$ink">tool build ./site</text>
<g clip-path="url(#row)"><rect class="type" x="293" y="298" width="290" height="26" fill="$panel"/></g>
<rect class="caret" x="100" y="340" width="9" height="18" fill="$accent"/>
<text class="m out" x="120" y="355" font-size="14" fill="$body">12 pages written</text>
<text class="m out" style="animation-delay:-7.6s" x="120" y="381" font-size="14" fill="$body">ready in 0.4 s</text>
```

### G. A measure

A detail for inside a card or under a figure, never the whole picture. Two bars that fill from
the left to their real proportion and rest. `transform-origin:0 50%`
makes them grow from their left end.

```svg
<style>
@keyframes fill{0%,6%{transform:scaleX(.04)}40%,92%{transform:scaleX(1)}100%{transform:scaleX(.04)}}
.fill{animation:fill 8s cubic-bezier(.4,0,.2,1) infinite;transform-box:fill-box;transform-origin:0 50%}
</style>
<rect class="fill" x="700" y="520" width="420" height="18" rx="9" fill="$muted"/>
<rect class="fill" x="700" y="552" width="140" height="18" rx="9" fill="$accent"/>
```

### H. A strip of running text and a backdrop that drifts

The backdrop every hero has, and the strip when step 1 kept one. The strip is the same line written three times, one period
apart, moved by exactly one period behind a clip: here 80 characters of 14 px mono, 80 x 8.4 =
672 px, in 12 s (56 px/s). Pad the line with spaces to the length you want (`xml:space`). The
backdrop is a pattern on a rectangle one tile larger than the canvas, moved by one tile.

```svg
<style>
@keyframes tick{to{transform:translateX(-672px)}}
@keyframes drift{to{transform:translate(24px,24px)}}
.tick{animation:tick 12s linear infinite}
.drift{animation:drift 4s linear infinite}
</style>
<defs>
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="12" cy="12" r="1.5" fill="$line"/></pattern>
<clipPath id="band"><rect x="0" y="596" width="1280" height="44"/></clipPath>
</defs>
<rect class="drift" x="-24" y="-24" width="1328" height="688" fill="url(#grid)"/>
<rect x="0" y="596" width="1280" height="44" fill="$panel"/>
<g clip-path="url(#band)"><g class="tick" fill="$body">
<text x="24" y="623" class="m" font-size="14" xml:space="preserve">reads <tspan fill="$accent">12 formats</tspan>      runs <tspan fill="$accent">offline</tspan>      one file to install      MIT licence      </text>
<text x="696" y="623" class="m" font-size="14" xml:space="preserve">reads <tspan fill="$accent">12 formats</tspan>      runs <tspan fill="$accent">offline</tspan>      one file to install      MIT licence      </text>
<text x="1368" y="623" class="m" font-size="14" xml:space="preserve">reads <tspan fill="$accent">12 formats</tspan>      runs <tspan fill="$accent">offline</tspan>      one file to install      MIT licence      </text>
</g></g>
```

In a hero the backdrop rectangle goes inside `<g id="backdrop">`, right after the background, and
the strip inside `<g id="ticker">`. Give the strip's `<g>` or `<text>` a `fill` of its own even
when every word is coloured by a `<tspan>`: the build reads the colour of a line from the text,
not from its spans.

### I. Features that take turns

For the highlights when no number sells the tool: three to five features in one place, one shown
at a time. Each slides up into place, rests, and leaves upwards as the next arrives,
the next rising in as it rises out, so the place is never empty. All share one duration (here
4 features x 3 s = 12 s, the same as the story or a multiple of it, or the build sees two stories
that drift) and each is shifted by a quarter of it. The window is a clip. With motion off one feature stands
there: the others carry `opacity="0"` as an attribute, which the animation overrides.

```svg
<style>
@keyframes turn{0%{transform:translateY(32px);opacity:0}4%,25%{transform:translateY(0);opacity:1}29%,100%{transform:translateY(-32px);opacity:0}}
.turn{animation:turn 12s cubic-bezier(.4,0,.2,1) infinite}
</style>
<defs><clipPath id="feat"><rect x="72" y="380" width="460" height="48"/></clipPath></defs>
<g clip-path="url(#feat)">
<g class="turn" opacity="0" style="animation-delay:-9s"><circle cx="84" cy="404" r="6" fill="$accent"/><text x="104" y="411" class="s" font-size="20" fill="$ink">Works offline</text></g>
<g class="turn" opacity="0" style="animation-delay:-6s"><circle cx="84" cy="404" r="6" fill="$accent"/><text x="104" y="411" class="s" font-size="20" fill="$ink">Your books stay yours</text></g>
<g class="turn" opacity="0" style="animation-delay:-3s"><circle cx="84" cy="404" r="6" fill="$accent"/><text x="104" y="411" class="s" font-size="20" fill="$ink">One click to install</text></g>
<g class="turn" style="animation-delay:0s"><circle cx="84" cy="404" r="6" fill="$accent"/><text x="104" y="411" class="s" font-size="20" fill="$ink">Free, for good</text></g>
</g>
```

In a hero this goes inside `<g id="facts">`, under the description.

