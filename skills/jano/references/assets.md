# Assets: icons, objects, logos, flags and file icons

The library in `assets/library/` holds 34 families from known sets, each with its licence
read in its own repository: only MIT, ISC and CC0 families are packed, so nothing in a picture
asks the repository that uses it for a credit. A picture never shows a credit. The set and the
icon's name travel in the `data-asset` attribute and the set's notice in the SVG's invisible
metadata; Jano's own repository lists them all in `THIRD_PARTY_NOTICES.md`. Never tell the user
to credit an asset.

## One family per category, chosen for this repository

A README keeps one look, so each category uses one family, recorded in the plan:

```
assets.py styles <category>                       every family, grouped by how it looks
assets.py suggest <category> --fill line --stroke regular --corners round --grid 24 --repo <name>
assets.py preview <category> <family[:variant],...>  the same things drawn by each, side by side
assets.py choose <repo> <category> <family> --why "..." [--variant v]
assets.py search <repo> <category> <words>        only in the chosen family
assets.py get <repo> <category> <name> "<what it means here>" --x --y --size --color $role
```

1. **Describe the identity, not a favourite set.** Look at the mark and the hero: is the line
   thin, regular or bold; are corners round or sharp; is it drawn in lines, solid glyphs,
   pixels or colour? Pass that to `suggest`. Families that fit equally come out in an order of
   their own for each repository; none is the default, and the first in a list is not better.
   A family with variants is scored by its best variant, shown as `family:variant`: a solid
   mark finds the solid variants of line families too.
2. **Preview the ones that fit** and pick the family whose drawings look like the mark: the same
   weight, the same corners, the same amount of detail. Write that reason in `--why`.
3. **Use only that family** for the category. When it lacks a thing, search with other words
   (`assets.py search` knows common synonyms); when it truly has nothing, draw the thing in the
   family's manner and declare it with `data-icon`. Never take one icon from another family:
   `readme.py check` refuses it.
4. Different categories may use different families: line icons from one, flat objects from
   another, logos from a third. Each is chosen the same way.

## Colour

- **`takes a $role`** (one-colour families): pass `--color $role`; the role is written into
  every fill and stroke, so the palette's dark and light values both work. Never paint an icon in
  `currentColor`: some viewers ignore `color=` and draw it black. An icon needs contrast 3 against
  what it sits on, in both themes; `check.py` measures it.
- **`keeps its own`** (colour families): drawn in their own colours; `--tint $role` repaints every
  fill in one role when the colours clash with the palette.
- **`never changes`** (flags): a flag's colours are the flag. Theme the frame around it, never
  the flag.
- **Logos** state a fact ("works with", "written in", "runs on"), stand apart from the scene's
  subject, are smaller than the project's own name, and move only by position and opacity.
  Brands remain their owners' trademarks.

## Size

`get` draws an icon at 24 px, or larger when its family is drawn in thinner lines (heroicons,
iconoir and hugeicons at 1.5 px come out at 32 px), so every stroke is 2 px or more on the
scene. Pass `--size` to draw it larger; smaller fails the build's check.

## Every asset says what it means

`get` writes `data-icon="<what it means here>"`. The build measures it (24 px or more, strokes of
2 px or more) and `readme.py judge` cuts every one out at the size a README shows it for the
blind judge. A misread or unsure icon is rebuilt: another name in the same family, larger, or in
the other variant. It is never just removed.

## Icons

| Family | Looks | Colour | Count | Pick it when |
|---|---|---|---|---|
| `fluent-color` | color, stroke none, corners round, grid 24 | keeps its own (or `--tint`) | 890 | Fluent's multicolour icons: soft gradients, keep their colours or tint them to one role. |
| `octicon` | glyph, stroke regular, corners round, grid 16 | takes a `$role` | 936 | GitHub's own UI glyphs (16 and 24 px): repos, branches, PRs, issues. GitHub's logos are removed. Variants: `16`, `24`. |
| `zondicons` | glyph, stroke none, corners sharp, grid 20 | takes a `$role` | 297 | Solid 20 px glyphs: bold silhouettes that read at small sizes. |
| `akar-icons` | line, stroke regular, corners round, grid 24 | takes a `$role` | 458 | Rounded line icons with a hand-made warmth. |
| `bi` | line, stroke regular, corners mixed, grid 16 | takes a `$role` | 2,084 | Bootstrap's 16 px icons, outline and -fill: crisp at small sizes. Variants: `outline`, `fill`. |
| `bx` | line, stroke regular, corners mixed, grid 24 | takes a `$role` | 1,460 | Regular and solid Boxicons (the brand logos, bxl, are removed). Variants: `regular`, `solid`. |
| `fluent` | line, stroke regular, corners round, grid 24 | takes a `$role` | 20,404 | Microsoft's 20,000 product icons, regular and filled, in several sizes; soft and friendly. Variants: `regular`, `filled`. |
| `healthicons` | line, stroke regular, corners round, grid 24 | takes a `$role` | 2,797 | Health and medicine: devices, people, places, conditions; outline, filled and negative. Variants: `outline`, `filled`, `negative`. |
| `heroicons` | line, stroke regular, corners round, grid 24 | takes a `$role` | 1,288 | Tailwind's set: 1.5 px outline and solid; restrained and product-like. Variants: `outline`, `solid`, `mini`, `micro`. |
| `hugeicons` | line, stroke light, corners round, grid 24 | takes a `$role` | 6,140 | The free stroke-rounded style of Hugeicons: 6,000 friendly, rounded line icons. |
| `humbleicons` | line, stroke regular, corners round, grid 24 | takes a `$role` | 287 | A small, minimal line set: few strokes, very calm. |
| `iconoir` | line, stroke light, corners round, grid 24 | takes a `$role` | 1,682 | Thin 1.5 px line icons with an airy, editorial feel; solid variants for some. Variants: `regular`, `solid`. |
| `lucide` | line, stroke regular, corners round, grid 24 | takes a `$role` | 2,175 | Clean 2 px line icons with round caps; the default look of modern developer tools. |
| `majesticons` | line, stroke regular, corners round, grid 24 | takes a `$role` | 1,045 | Balanced line and solid pairs for product interfaces. Variants: `line`, `solid`. |
| `mynaui` | line, stroke regular, corners round, grid 24 | takes a `$role` | 2,658 | Neutral line and solid icons made for interfaces. Variants: `line`, `solid`. |
| `ph` | line, stroke any, corners round, grid 24 | takes a `$role` | 9,161 | One drawing in six weights: thin, light, regular, bold, fill and duotone; pick the weight that matches the mark. Variants: `regular`, `thin`, `light`, `bold`, `fill`, `duotone`. |
| `radix-icons` | line, stroke thin, corners sharp, grid 15 | takes a `$role` | 342 | 332 crisp 15 px icons for interfaces: precise, technical, small. |
| `simple-line-icons` | line, stroke thin, corners round, grid 32 | takes a `$role` | 194 | Thin, light line icons from the 2010s web; delicate (no longer maintained). |
| `tabler` | line, stroke regular, corners round, grid 24 | takes a `$role` | 6,594 | 6,500 line icons, the widest line vocabulary; a filled variant for many. Variants: `outline`, `filled`. |
| `pixelarticons` | pixel, stroke none, corners sharp, grid 24 | takes a `$role` | 1,306 | Pixel-art icons on a 24 px grid: retro, games, terminals, playful tools. |
| `eva` | solid, stroke regular, corners round, grid 24 | takes a `$role` | 490 | Soft outline and fill pairs with rounded ends (no longer maintained). Variants: `outline`, `fill`. |

## Objects

Things a scene holds: a book, a laptop, a rocket, a package, a key. Use them where a recognisable
object explains more than a pictogram, larger than icons (48 px or more).

| Family | Looks | Colour | Count | Pick it when |
|---|---|---|---|---|
| `fluent-emoji-flat` | color, stroke none, corners round, grid 32 | keeps its own (or `--tint`) | 3,174 | 3,000 flat objects, people-free things and symbols with few solid fills: easy to tint. |
| `fluent-emoji-high-contrast` | glyph, stroke none, corners round, grid 32 | takes a `$role` | 1,594 | Monochrome objects: one role colours them, they sit well beside line icons. |

## Logos

The tools and platforms a repository works with, by name.

| Family | Looks | Colour | Count | Pick it when |
|---|---|---|---|---|
| `devicon` | color, stroke none, corners any, grid 32 | keeps its own (or `--tint`) | 1,161 | Programming languages and tools in their own colours. |
| `logos` | color, stroke none, corners any, grid free | keeps its own (or `--tint`) | 2,305 | 2,000 logos in their brand colours, many with wordmarks. |
| `skill-icons` | color, stroke none, corners round, grid 24 | keeps its own (or `--tint`) | 400 | Tech logos set on rounded tiles, light and dark: a badge look. |
| `cib` | glyph, stroke none, corners any, grid 32 | takes a `$role` | 830 | 830 one-colour brand marks, a little heavier than Simple Icons. |
| `devicon-plain` | glyph, stroke none, corners any, grid 32 | takes a `$role` | 861 | Programming languages and tools as one-colour marks. |
| `simple-icons` | glyph, stroke none, corners any, grid 24 | takes a `$role` | 3,533 | 3,400 brand marks as one-colour silhouettes: take any role from the palette. |

## Flags

Languages and countries a repository supports.

| Family | Looks | Colour | Count | Pick it when |
|---|---|---|---|---|
| `cif` | color, stroke none, corners sharp, grid free | never changes | 199 | Plain rectangular flags. |
| `circle-flags` | color, stroke none, corners round, grid 32 | never changes | 696 | Round flags: friendly, sit well in chips and avatars. |
| `flag` | color, stroke none, corners sharp, grid free | never changes | 542 | Rectangular flags in 4:3 and 1:1 for every country. Variants: `4x3`, `1x1`. |
| `flagpack` | color, stroke none, corners round, grid 24 | never changes | 256 | Flags with rounded corners and a soft frame. |

## File icons

Files by type, for a file tree or a list of outputs. A kit `file` card with the real file name
often says more; use these when the type matters.

| Family | Looks | Colour | Count | Pick it when |
|---|---|---|---|---|
| `catppuccin` | line, stroke regular, corners round, grid 16 | keeps its own (or `--tint`) | 659 | File and folder icons by type (json, md, py, folder-src), pastel line style. |

## Parts are not assets

Windows, terminals, cards, chips, buttons, cursors, file cards, code, progress bars, toggles,
badges, skeletons and device outlines come from `scripts/kit.py`, Jano's own: drawn the same way
every time, sized to their real text and coloured by role. The cursor is free in style but turns
into a pointer over anything clickable (`kit.py cursor-swap`).
