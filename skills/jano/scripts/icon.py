#!/usr/bin/env python3
"""Icons drawn from a known set, so a small picture means what it should.

    python icon.py search <words>                 icons whose name or tags match, best first
    python icon.py <name> <means> [options]       the <g> to paste into a scene

Options: --x N --y N (top-left on the canvas), --size N (px, 24 or more), --color $role.

The set is Lucide (assets/icons.json, ISC licence): 1,500 icons drawn on a 24 px grid
with a 2 px stroke, made to be read at small sizes. The <g> it prints carries what the
icon means in data-icon, so the build can check it and the judges can read it cold.
"""
import json, re, sys
from pathlib import Path

ICONS = Path(__file__).resolve().parent.parent / "assets" / "icons.json"
MIN_SIZE = 24  # px on the canvas: the grid the set is drawn for; at README width that is 16 px


def load():
    return json.loads(ICONS.read_text(encoding="utf-8"))["icons"]


def search(words):
    icons, words = load(), [w.lower() for w in words]
    scored = []
    for name, (_, tags) in icons.items():
        hay = [name] + name.split("-") + [t.lower() for t in tags]
        score = sum(3 if w == name else 2 if w in hay else 1 if any(w in h for h in hay) else 0 for w in words)
        if score:
            scored.append((-score, len(name), name, tags))
    for _, _, name, tags in sorted(scored)[:15]:
        print(f"{name:28} {', '.join(tags[:8])}")
    if not scored:
        print("no icon matches: try another word for the same thing, or draw your own and declare it with data-icon")


def snippet(name, means, x=0.0, y=0.0, size=24.0, color="$muted"):
    icons = load()
    if name not in icons:
        sys.exit(f"error: no icon named {name!r}: run `icon.py search <words>`")
    if size < MIN_SIZE:
        print(f"warning: {size:g} px is under {MIN_SIZE}: the icon is drawn for {MIN_SIZE} px and blurs below it", file=sys.stderr)
    k = size / 24
    stroke = max(2.0, 2.0 * k) / k  # at least 2 px on the canvas, at any size
    means = re.sub(r'["<>&]', "", means)
    return (f'<g data-icon="{means}" data-source="lucide:{name}" transform="translate({x:g} {y:g}) scale({k:g})" fill="none" '
            f'stroke="{color}" stroke-width="{stroke:.4g}" stroke-linecap="round" stroke-linejoin="round">{icons[name][0]}</g>')


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "search":
        return search(args[1:])
    opts, pos = {}, []
    it = iter(args)
    for a in it:
        if a.startswith("--"):
            opts[a[2:]] = next(it, "")
        else:
            pos.append(a)
    if len(pos) < 2:
        sys.exit("error: give the icon's name and what it means here: icon.py scissors \"cut\" --x 70 --y 250")
    print(snippet(pos[0], pos[1], float(opts.get("x", 0)), float(opts.get("y", 0)), float(opts.get("size", 24)), opts.get("color", "$muted")))


if __name__ == "__main__":
    main()
