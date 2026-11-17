#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["fonttools", "brotli"]
# ///
"""Build hero-dark.svg and hero-light.svg from one hero.src.svg.

    uv run build.py assets/hero.src.svg      (installs what it needs)
    python build.py assets/hero.src.svg      (after: pip install fonttools brotli)

The source starts with a palette comment, one role per line (name dark light):

    <!--palette
    bg     #0F1115 #F0F5FB
    accent #4FD1C5 #0B7A70
    -->

and uses the roles as $bg, $accent... anywhere in the SVG. The build swaps them
per theme, embeds subsets of the fonts (classes .s text, .b bold, .m mono),
turns text that moves into outlines so it travels without pixel jumps, adds the
reduced-motion rule, checks the result and writes a preview page.
"""
import base64, hashlib, html, io, re, sys, tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
SVG = "http://www.w3.org/2000/svg"
XMLSPACE = "{http://www.w3.org/XML/1998/namespace}space"
FACES = {"s": ("SpaceGrotesk.ttf", 500), "b": ("SpaceGrotesk.ttf", 700), "m": ("JetBrainsMono.ttf", None)}
_fonts = {}


def font(face):
    if face not in _fonts:
        try:
            from fontTools.ttLib import TTFont
            import brotli  # noqa: F401  (woff2)
        except ImportError:
            sys.exit("error: run this with `uv run`, or first: pip install fonttools brotli")
        from fontTools.varLib import instancer

        file, wght = FACES[face]
        f = TTFont(ASSETS / file)
        _fonts[face] = instancer.instantiateVariableFont(f, {"wght": wght}) if wght else f
    return _fonts[face]


def subset_font(face, chars):
    from fontTools import subset

    f = font(face)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.hinting = False
    opts.desubroutinize = True
    sub = subset.Subsetter(opts)
    sub.populate(text=chars)
    sub.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff2"
    f.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


# ---- moving text -> outlines
# A browser places text glyphs on whole pixels, so text that travels slowly moves in
# small jumps. Outlines are plain shapes and move smoothly at any speed.

def moving_classes(css):
    """Classes (and keyframe names) whose animation changes transform."""
    kf = dict(re.findall(r"@keyframes\s+([\w-]+)\s*\{((?:[^{}]*\{[^{}]*\})*)", css))
    names = {n for n, b in kf.items() if "transform" in b}
    classes = set()
    for sel, decl in re.findall(r"([^{}]+)\{([^{}]*animation[^{}]*)\}", css):
        if any(re.search(rf"\b{re.escape(n)}\b", decl) for n in names):
            classes.update(re.findall(r"\.([\w-]+)", sel))
    return classes, names


def num(v, default=0.0):
    m = re.search(r"-?[\d.]+", v or "")
    return float(m.group()) if m else default


def outline_moving_text(root, warns):
    from fontTools.pens.svgPathPen import SVGPathPen

    css = "".join(e.text or "" for e in root.iter(f"{{{SVG}}}style"))
    classes, names = moving_classes(css)
    parent = {c: p for p in root.iter() for c in p}

    def chain(el):
        while el is not None:
            yield el
            el = parent.get(el)

    def moves(el):
        for a in chain(el):
            if set(a.get("class", "").split()) & classes:
                return True
            st = a.get("style", "")
            if "animation" in st and any(n in st for n in names):
                return True
        return False

    def inherit(el, attr, default=None):
        for a in chain(el):
            if a.get(attr) is not None:
                return a.get(attr)
        return default

    def face_of(el):
        for a in chain(el):
            for c in a.get("class", "").split():
                if c in FACES:
                    return c
        return None

    glyphs, count = {}, 0
    drop = ("x", "y", "dx", "dy", "font-size", "text-anchor", "letter-spacing", XMLSPACE)
    for el in [e for e in root.iter(f"{{{SVG}}}text") if moves(e)]:
        if face_of(el) is None:
            warns.append("moving <text> without class s, b or m was left as text; it may travel in pixel jumps")
            continue
        keep = inherit(el, XMLSPACE) == "preserve"
        runs = [(el.text or "", el)]  # (string, element that styles it)
        for ts in el:
            runs.append(("".join(ts.itertext()), ts))
            runs.append((ts.tail or "", el))
        if not keep:
            runs = [(re.sub(r"\s+", " ", t), n) for t, n in runs]
        runs = [(t, n) for t, n in runs if t]
        if not runs:
            continue
        if not keep:
            runs[0] = (runs[0][0].lstrip(), runs[0][1])
            runs[-1] = (runs[-1][0].rstrip(), runs[-1][1])

        out = ET.Element(f"{{{SVG}}}g", {k: v for k, v in el.attrib.items() if k not in drop})
        out.tail = el.tail
        cx, cy = num(el.get("x")), num(el.get("y"))
        chunks = []  # [x, y, anchor, [(group, width px, dx, dy)]]
        for t, n in runs:
            own = n is not el
            if not chunks or (own and (n.get("x") is not None or n.get("y") is not None)):
                if own:
                    cx, cy = num(n.get("x"), cx), num(n.get("y"), cy)
                chunks.append([cx, cy, inherit(n, "text-anchor", "start"), []])
            face = face_of(n)
            f = font(face)
            k = num(inherit(n, "font-size"), 16) / f["head"].unitsPerEm
            ls = num(inherit(n, "letter-spacing")) / k
            cmap, gs, hmtx = f.getBestCmap(), f.getGlyphSet(), f["hmtx"]
            g = ET.Element(f"{{{SVG}}}g", {a: v for a, v in n.attrib.items() if a not in drop} if own else {})
            g.set("data-k", f"{k:.5f}")
            pos = 0.0
            for ch in t:
                gname = cmap.get(ord(ch))
                if gname is None:
                    warns.append(f"moving text: '{ch}' is not in the font and was dropped")
                    continue
                gid = f"g{face}{f.getGlyphID(gname)}"
                if gid not in glyphs:
                    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.0f}")
                    gs[gname].draw(pen)
                    glyphs[gid] = pen.getCommands()
                if glyphs[gid]:
                    ET.SubElement(g, f"{{{SVG}}}use", {"href": "#" + gid, "x": f"{pos:.0f}"})
                pos += hmtx[gname][0] + ls
            chunks[-1][3].append((g, pos * k, num(n.get("dx")) if own else 0, num(n.get("dy")) if own else 0))
        for x, y, anchor, parts in chunks:
            width = sum(w + dx for _, w, dx, _ in parts)
            x -= {"middle": width / 2, "end": width}.get(anchor, 0)
            for g, w, dx, dy in parts:
                x, y = x + dx, y + dy
                k = g.attrib.pop("data-k")
                g.set("transform", f"translate({x:.2f} {y:.2f}) scale({k} -{k})")
                out.append(g)
                x += w
            cx, cy = x, y
        p = parent[el]
        p[list(p).index(el)] = out
        count += 1
    if glyphs:
        defs = ET.Element(f"{{{SVG}}}defs")
        for gid, d in glyphs.items():
            if d:
                ET.SubElement(defs, f"{{{SVG}}}path", {"id": gid, "d": d})
        root.insert(0, defs)
    return count


def lum(hexc):
    h = hexc.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    ch = [int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    ch = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in ch]
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1]).resolve()
    out = src.parent
    raw = src.read_text(encoding="utf-8")
    errors, warns = [], []

    m = re.search(r"<!--\s*palette(.*?)-->", raw, re.S)
    if not m:
        sys.exit("error: no <!--palette ... --> comment in the source")
    palette = {}
    for line in m.group(1).strip().splitlines():
        p = line.split()
        if len(p) == 3 and p[1].startswith("#") and p[2].startswith("#"):
            palette[p[0]] = (p[1], p[2])
    body = raw.replace(m.group(0), "").strip()

    # ---- checks on the source
    if 'viewBox="0 0 1280 640"' not in body:
        errors.append('viewBox must be "0 0 1280 640"')
    if 'role="img"' not in body or "aria-label=" not in body:
        errors.append('root <svg> needs role="img" and an aria-label that says what the hero shows')
    for bad in ("<script", "<foreignObject", "<image", "@import"):
        if bad in body:
            errors.append(f"{bad} is not allowed: GitHub shows the SVG as an image, nothing external loads")
    ext = [u for u in re.findall(r"https?://[^\"')\s]+", body) if "www.w3.org" not in u]
    if ext:
        errors.append(f"external URL(s) will not load: {ext[:3]}")
    if "<style>" not in body:
        errors.append("no <style> block: the hero has no animation")
    anims = re.findall(r"animation\s*:\s*([^;}]+)", body)
    for a in anims:
        if "infinite" not in a and "none" not in a:
            errors.append(f"animation without 'infinite' (it would play once, like a video): {a.strip()}")
        if "steps(" in a:
            warns.append(f"steps() makes motion jump: {a.strip()}")
    for d in re.findall(r"animation-delay\s*:\s*([^;}\"]+)", body):
        if not d.strip().startswith("-") and d.strip() not in ("0s", "0"):
            warns.append(f"positive animation-delay {d.strip()}: the first loop starts frozen. Use a negative delay to shift phase")
    if len(set(anims)) < 4:
        warns.append(f"only {len(set(anims))} distinct animations: every region of the hero should have some motion")
    if re.search(r"repeatCount=\"(?!indefinite)", body):
        errors.append("SMIL animation must use repeatCount=\"indefinite\"")
    used = set(re.findall(r"\$([a-z][a-z0-9_]*)", body))
    for u in used - set(palette):
        errors.append(f"${u} is used but not in the palette")
    small = sorted({float(s) for s in re.findall(r"font-size=\"([\d.]+)\"", body) if float(s) < 13})
    if small:
        warns.append(f"font-size below 13 ({small}): unreadable at README width, where the hero is shown at ~65%")
    for ti, theme in enumerate(("dark", "light")):
        if "bg" in palette:
            for role, need in (("ink", 7), ("body", 4.5), ("muted", 4.5), ("accent", 4.5)):
                if role in palette:
                    for surface in ("bg", "panel"):
                        if surface in palette:
                            c = contrast(palette[role][ti], palette[surface][ti])
                            if c < need:
                                warns.append(f"{theme}: ${role} on ${surface} contrast {c:.1f} < {need}")
    if errors:
        print("\n".join("error: " + e for e in errors))
        sys.exit(1)

    # ---- moving text to outlines
    ET.register_namespace("", SVG)
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    try:
        root = ET.fromstring(body)
    except ET.ParseError as e:
        sys.exit(f"error: the SVG is not well-formed XML: {e}")
    outlined = outline_moving_text(root, warns)
    body = ET.tostring(root, encoding="unicode")

    # ---- fonts for the text that stays still
    text = re.sub(r"<style>.*?</style>", "", body, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    chars = "".join(sorted(set(text) - set("\n\r\t"))) + " "
    faces = (
        f"@font-face{{font-family:SG;src:url(data:font/woff2;base64,{subset_font('s', chars)}) format('woff2')}}"
        f"@font-face{{font-family:SG7;src:url(data:font/woff2;base64,{subset_font('b', chars)}) format('woff2')}}"
        f"@font-face{{font-family:JB;src:url(data:font/woff2;base64,{subset_font('m', chars)}) format('woff2')}}\n"
        "text{text-rendering:geometricPrecision}.s{font-family:SG,sans-serif}.b{font-family:SG7,sans-serif;font-weight:700}.m{font-family:JB,monospace}\n"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}\n"
    )
    body = body.replace("<style>", "<style>" + faces, 1)

    names = []
    for ti, theme in enumerate(("dark", "light")):
        svg = re.sub(r"\$([a-z][a-z0-9_]*)", lambda k: palette[k.group(1)][ti], body)
        f = out / f"hero-{theme}.svg"
        f.write_text(svg + "\n", encoding="utf-8", newline="\n")
        names.append(f)
        kb = len(svg.encode()) / 1024
        if kb > 200:
            warns.append(f"{f.name} is {kb:.0f} KB: simplify, a hero should stay under 200 KB")
        print(f"wrote {f} ({kb:.0f} KB)")
    print(f"{outlined} moving text element(s) turned into outlines")

    # ---- preview: the hero at README width and phone width, on GitHub's two backgrounds
    logo = out / "logo.svg"
    logos = "".join(f'<img src="{logo.as_uri()}" width="{s}" height="{s}">' for s in (16, 24, 48, 96)) if logo.exists() else "<i>no assets/logo.svg</i>"
    page = "<!doctype html><meta charset=utf-8><title>hero preview</title><style>body{margin:0;font:14px system-ui}section{padding:32px}img{display:block;margin:0 0 24px}.l img{display:inline-block;margin-right:16px;vertical-align:middle}</style>"
    for f, bg, fg in ((names[0], "#0d1117", "#f0f6fc"), (names[1], "#ffffff", "#1f2328")):
        page += f'<section style="background:{bg};color:{fg}"><p>{f.name} at README width (838px)</p><img src="{f.as_uri()}" width="838"><p>phone (360px)</p><img src="{f.as_uri()}" width="360"><p class="l">logo {logos}</p></section>'
    # one preview per source path, so two repos with the same name do not overwrite each other
    tag = hashlib.sha1(str(src).encode()).hexdigest()[:8]
    prev = Path(tempfile.gettempdir()) / f"hero-preview-{src.parent.parent.name}-{tag}.html"
    prev.write_text(page, encoding="utf-8")
    print(f"preview {prev}")
    print("\n".join("warning: " + w for w in dict.fromkeys(warns)) or "checks passed")


if __name__ == "__main__":
    main()
