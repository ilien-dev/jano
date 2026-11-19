#!/usr/bin/env python3
"""Jano's own parts for scenes: drawn the same way every time, sized to their real text, coloured by palette role.

    python kit.py list                                  the parts and their options
    python kit.py <part> [--option value ...]           the SVG to paste into a scene

Every part is a <g data-kit="..."> written with palette roles ($panel, $line, $ink, $body,
$muted, $accent, $bg), so it takes the repository's colours. Text is measured with the
skill's fonts, so a chip or a button is always as wide as its label. Clickable parts carry
data-clickable; cursors carry data-cursor, and a cursor that crosses a clickable part turns
into a pointer there (see cursor-swap). Parts are MIT, part of Jano: nothing to credit.
"""
import html, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import ICON_MIN, PANEL_PAD, text_width  # noqa: E402

PARTS = {
    "window": "x y w h title chrome(dots|plain) — an app window with a title bar",
    "terminal": "x y w h title lines(a|b|c, '$ ' marks a command) — a terminal with real lines",
    "card": "x y w h title text size(15) face(s|m) — a panel with an optional heading and text wrapped inside its padding; h grows to fit when left out",
    "chip": "x y text role(accent) size(14) — a pill sized to its text",
    "button": "x y text variant(primary|ghost) size(16) — a button sized to its text; clickable",
    "cursor": "x y kind(arrow|pointer|text) size(26) color($ink) — the tip is at (x, y)",
    "cursor-swap": "x y on(25-40,60-75) dur(8) name(cur) — an arrow that turns into a pointer during the given percent ranges",
    "file": "x y name role(accent) — a file card with a folded corner and its real name",
    "code": "x y lines(a|b|c) size(14) — lines of code in mono",
    "progress": "x y w value(0.6) role(accent) — a bar",
    "toggle": "x y on(true) — a switch",
    "badge": "x y text role(accent) — a small label with a dot",
    "note": "x y text role(accent) size(14) icon(true) — a callout sized to its text, with room for an icon from the chosen family on its left",
    "skeleton": "x y w lines(3) — grey lines that stand for text",
    "device": "x y kind(phone|laptop|browser) w h — an outline to put a screen in",
}


def width(text, size, face="s"):
    """The width check.py measures. A character the fonts lack stops the part: it has no width anyone can rely on."""
    w, lost = text_width(str(text), float(size), face)
    if lost:
        sys.exit(f"error: {' '.join(sorted(lost))} is not in the skill's fonts: each machine draws it in another font and at another width. "
                 "Leave it out of the text and draw it as an icon from the chosen family (assets.py get), or use another character")
    return w


def wrap(text, size, face, room):
    """Lines of `text` no wider than `room` px, broken between words."""
    lines, cur = [], ""
    for word in str(text).split():
        nxt = f"{cur} {word}".strip()
        if cur and width(nxt, size, face) > room:
            lines.append(cur)
            cur = word
        else:
            cur = nxt
        if width(cur, size, face) > room:
            sys.exit(f"error: the word {word!r} is wider than the card's room ({room:.0f} px at {size:g} px): widen the card or shrink the text")
    return lines + ([cur] if cur else [])


def esc(t):
    return html.escape(str(t), quote=False)


def window(x=0, y=0, w=520, h=320, title="", chrome="dots"):
    bar = 34
    dots = "" if chrome == "plain" else "".join(f'<circle cx="{x + 20 + i * 16}" cy="{y + bar / 2}" r="5" fill="$line"/>' for i in range(3))
    label = f'<text x="{x + w / 2}" y="{y + bar / 2 + 5}" class="m" font-size="14" fill="$muted" text-anchor="middle">{esc(title)}</text>' if title else ""
    return (f'<g data-kit="window"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="$panel" stroke="$line" stroke-width="1.5"/>'
            f'<path d="M{x} {y + bar}H{x + w}" stroke="$line" stroke-width="1.5"/>{dots}{label}</g>')


def terminal(x=0, y=0, w=520, h=220, title="terminal", lines=""):
    rows, out = [l for l in str(lines).split("|") if l], []
    for i, line in enumerate(rows):
        ty = y + 34 + 30 + i * 24
        if line.startswith("$ "):
            out.append(f'<text x="{x + 20}" y="{ty}" class="m" font-size="15" fill="$ink"><tspan fill="$accent">$</tspan> {esc(line[2:])}</text>')
        else:
            out.append(f'<text x="{x + 20}" y="{ty}" class="m" font-size="15" fill="$body">{esc(line)}</text>')
        if width(line, 15, "m") > w - 40:
            print(f"warning: terminal line {line[:30]!r} is wider than the terminal: widen it or shorten the line", file=sys.stderr)
    return window(x, y, w, h, title).replace('data-kit="window"', 'data-kit="terminal"', 1).replace("</g>", "".join(out) + "</g>", 1)


def card(x=0, y=0, w=240, h=None, title="", text="", size=15, face="s"):
    size = float(size)
    pad = max(20, PANEL_PAD * max(size, 18))  # a panel keeps its text's own size on each side
    head = f'<text x="{x + pad:g}" y="{y + 32}" class="b" font-size="18" fill="$ink">{esc(title)}</text>' if title else ""
    if title and width(title, 18, "b") > w - 2 * pad:
        sys.exit(f"error: the card's title is {width(title, 18, 'b'):.0f} px wide and the card leaves {w - 2 * pad:.0f}: widen it or shorten the title")
    lead, top = round(size * 1.45, 1), y + (52 if title else pad) + size * 0.74
    lines = wrap(text, size, face, w - 2 * pad) if text else []
    body = "".join(f'<text x="{x + pad:g}" y="{top + i * lead:.1f}" class="{face}" font-size="{size:g}" fill="$body">{esc(l)}</text>' for i, l in enumerate(lines))
    need = (top + (len(lines) - 1) * lead + size * 0.2 + pad - y) if lines else (52 if title else 0) + pad
    if h is None:
        h = max(need, 80)
    elif float(h) < need:
        sys.exit(f"error: the card's text needs {need:.0f} px of height and it has {float(h):.0f}: leave h out, raise it or shorten the text")
    return f'<g data-kit="card"><rect x="{x}" y="{y}" width="{w}" height="{float(h):g}" rx="12" fill="$panel" stroke="$line" stroke-width="1.5"/>{head}{body}</g>'


def chip(x=0, y=0, text="", role="accent", size=14):
    w, h = width(text, size) + 24, size + 14
    return (f'<g data-kit="chip"><rect x="{x}" y="{y}" width="{w:.0f}" height="{h}" rx="{h / 2}" fill="none" stroke="${role}" stroke-width="1.5"/>'
            f'<text x="{x + w / 2:.1f}" y="{y + h / 2 + size * 0.35:.1f}" class="s" font-size="{size}" fill="${role}" text-anchor="middle">{esc(text)}</text></g>')


def button(x=0, y=0, text="", variant="primary", size=16):
    w, h = width(text, size, "b") + 40, size + 24
    if variant == "ghost":
        box, ink = f'fill="none" stroke="$line" stroke-width="1.5"', "$ink"
    else:
        box, ink = 'fill="$accent"', "$bg"
    return (f'<g data-kit="button" data-clickable="true"><rect x="{x}" y="{y}" width="{w:.0f}" height="{h}" rx="{h / 2}" {box}/>'
            f'<text x="{x + w / 2:.1f}" y="{y + h / 2 + size * 0.35:.1f}" class="b" font-size="{size}" fill="{ink}" text-anchor="middle">{esc(text)}</text></g>')


CURSORS = {  # drawn on a 24 px grid with the tip at 0,0; Jano's own shapes
    "arrow": "M0 0V19L5 14.5L8.6 22.3L12 20.8L8.5 13.2H15Z",
    "pointer": ("M6.5 0C7.9 0 9 1.1 9 2.5V9.2C9.4 9 9.9 8.9 10.4 8.9C11.6 8.9 12.6 9.6 13 10.6C13.4 10.4 13.9 10.3 14.4 10.3C15.7 10.3 16.8 11.2 17.1 12.4"
                "C17.5 12.2 17.9 12.1 18.4 12.1C19.8 12.1 21 13.3 21 14.7V19C21 23.4 17.4 27 13 27H11.5C8.8 27 6.4 25.6 5 23.4L1 17C.3 15.9 .6 14.5 1.7 13.8"
                "C2.7 13.2 4 13.4 4.7 14.4L4 13.6V2.5C4 1.1 5.1 0 6.5 0Z"),
    "text": "M3 0H12M3 24H12M7.5 0V24",
}


def cursor(x=0, y=0, kind="arrow", size=26, color="$ink", outline="$bg"):
    k = size / 24
    d = CURSORS[kind]
    if kind == "text":
        shape = f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.4" stroke-linecap="round"/>'
    else:
        dx = -6.5 if kind == "pointer" else 0  # the pointer's tip is the finger's end
        shape = f'<path transform="translate({dx} 0)" d="{d}" fill="{color}" stroke="{outline}" stroke-width="1.6" stroke-linejoin="round"/>'
    return f'<g data-kit="cursor" data-cursor="{kind}" transform="translate({x} {y}) scale({k:.3g})">{shape}</g>'


def cursor_swap(x=0, y=0, on="25-40,60-75", dur=8, name="cur"):
    """An arrow and a pointer in one place: the pointer shows while over something clickable."""
    spans = [tuple(float(v) for v in r.split("-")) for r in str(on).split(",") if r]
    stops_ptr, stops_arr = ["0%{opacity:0}"], ["0%{opacity:1}"]
    for a, b in spans:
        stops_ptr += [f"{a:g}%{{opacity:0}}", f"{a + 0.5:g}%,{b:g}%{{opacity:1}}", f"{b + 0.5:g}%{{opacity:0}}"]
        stops_arr += [f"{a:g}%{{opacity:1}}", f"{a + 0.5:g}%,{b:g}%{{opacity:0}}", f"{b + 0.5:g}%{{opacity:1}}"]
    stops_ptr.append("100%{opacity:0}")
    stops_arr.append("100%{opacity:1}")
    css = (f"@keyframes {name}-ptr{{{''.join(stops_ptr)}}}@keyframes {name}-arr{{{''.join(stops_arr)}}}"
           f".{name}-ptr{{animation:{name}-ptr {dur}s step-end infinite}}.{name}-arr{{animation:{name}-arr {dur}s step-end infinite}}")
    return (f"<!-- add to <style>: {css} -->\n"
            f'<g data-kit="cursor-swap"><g class="{name}-arr">{cursor(x, y, "arrow")}</g><g class="{name}-ptr" opacity="0">{cursor(x, y, "pointer")}</g></g>')


def file(x=0, y=0, name="README.md", role="accent"):
    w, h, fold = width(name, 14, "m") + 52, 40, 10
    return (f'<g data-kit="file"><path d="M{x} {y + 6}a6 6 0 0 1 6-6H{x + w - fold}L{x + w} {y + fold}V{y + h - 6}a6 6 0 0 1-6 6H{x + 6}a6 6 0 0 1-6-6Z" '
            f'fill="$panel" stroke="$line" stroke-width="1.5"/><rect x="{x + 12}" y="{y + 12}" width="14" height="16" rx="3" fill="${role}"/>'
            f'<text x="{x + 36}" y="{y + 25}" class="m" font-size="14" fill="$ink">{esc(name)}</text></g>')


def code(x=0, y=0, lines="", size=14):
    rows = [l for l in str(lines).split("|")]
    out = "".join(f'<text x="{x}" y="{y + size + i * (size + 8)}" class="m" font-size="{size}" fill="$body" xml:space="preserve">{esc(l)}</text>' for i, l in enumerate(rows))
    return f'<g data-kit="code">{out}</g>'


def progress(x=0, y=0, w=240, value=0.6, role="accent"):
    return (f'<g data-kit="progress"><rect x="{x}" y="{y}" width="{w}" height="10" rx="5" fill="$line"/>'
            f'<rect x="{x}" y="{y}" width="{w * float(value):.0f}" height="10" rx="5" fill="${role}"/></g>')


def toggle(x=0, y=0, on="true"):
    on = str(on).lower() != "false"
    return (f'<g data-kit="toggle" data-clickable="true"><rect x="{x}" y="{y}" width="44" height="24" rx="12" fill="{"$accent" if on else "$line"}"/>'
            f'<circle cx="{x + (32 if on else 12)}" cy="{y + 12}" r="9" fill="$bg"/></g>')


def badge(x=0, y=0, text="", role="accent"):
    w = width(text, 13, "m") + 30
    return (f'<g data-kit="badge"><rect x="{x}" y="{y}" width="{w:.0f}" height="24" rx="6" fill="$panel" stroke="$line" stroke-width="1.5"/>'
            f'<circle cx="{x + 12}" cy="{y + 12}" r="4" fill="${role}"/><text x="{x + 22}" y="{y + 16.5}" class="m" font-size="13" fill="$body">{esc(text)}</text></g>')


def note(x=0, y=0, text="", role="accent", size=14, icon="true"):
    size = float(size)
    room = max(ICON_MIN, round(size * 1.4)) if str(icon).lower() != "false" else 0
    pad, h = max(12, size), max(round(size * 2.4), room + 12)
    gap = 8 if room else 0
    w = pad + room + gap + width(text, size) + pad
    tx, ty = x + pad + room + gap, y + h / 2 + size * 0.35
    if room:  # on stderr, so the part pastes as it is
        print(f'note: paste after it the icon from the chosen family: assets.py get <repo> icons <name> "<what it means>" '
              f'--x {x + pad:g} --y {y + (h - room) / 2:g} --size {room} --color ${role}', file=sys.stderr)
    return (f'<g data-kit="note"><rect x="{x}" y="{y}" width="{w:.0f}" height="{h}" rx="{min(10, h / 2):g}" fill="$panel" stroke="${role}" stroke-width="1.5"/>'
            f'<text x="{tx:g}" y="{ty:.1f}" class="s" font-size="{size:g}" fill="$ink">{esc(text)}</text></g>')


def skeleton(x=0, y=0, w=240, lines=3):
    n = int(lines)
    return "".join([f'<g data-kit="skeleton">'] + [f'<rect x="{x}" y="{y + i * 20}" width="{w * (0.62 if i == n - 1 else 1):.0f}" height="10" rx="5" fill="$line"/>' for i in range(n)] + ["</g>"])


def device(x=0, y=0, kind="phone", w=None, h=None):
    if kind == "phone":
        w, h = float(w or 220), float(h or 440)
        return (f'<g data-kit="device" data-device="phone"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="36" fill="$panel" stroke="$line" stroke-width="3"/>'
                f'<rect x="{x + w * 0.35:.0f}" y="{y + w * 0.06:.0f}" width="{w * 0.3:.0f}" height="{max(6, w * 0.08):.0f}" rx="{max(3, w * 0.04):.0f}" fill="$line"/></g>')
    if kind == "laptop":
        w, h = float(w or 520), float(h or 320)
        return (f'<g data-kit="device" data-device="laptop"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="$panel" stroke="$line" stroke-width="3"/>'
                f'<path d="M{x - 40} {y + h + 6}H{x + w + 40}l-20 18H{x - 20}Z" fill="$line"/></g>')
    w, h = float(w or 560), float(h or 340)
    return window(x, y, w, h, "", "dots").replace('data-kit="window"', 'data-kit="device" data-device="browser"', 1).replace(
        "</g>", f'<rect x="{x + 80}" y="{y + 9}" width="{w - 160}" height="16" rx="8" fill="$bg"/></g>', 1)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if not args or args[0] in ("list", "-h", "--help"):
        print(__doc__)
        for k, v in PARTS.items():
            print(f"  {k:12} {v}")
        return
    part, opts = args[0], {}
    it = iter(args[1:])
    for a in it:
        if a.startswith("--"):
            opts[a[2:].replace("-", "_")] = next(it, "")
    fn = {"cursor-swap": cursor_swap}.get(part) or globals().get(part)
    if part not in PARTS or not callable(fn):
        sys.exit(f"error: no part {part!r}: kit.py list")
    for k in ("x", "y", "w", "h", "size", "dur"):
        if k in opts and opts[k] != "":
            opts[k] = float(opts[k])
    print(fn(**opts))


if __name__ == "__main__":
    main()
