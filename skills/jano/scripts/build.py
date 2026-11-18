#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["fonttools", "brotli"]
# ///
"""Build <name>-dark.svg and <name>-light.svg from one <name>.src.svg.

    uv run build.py assets/hero.src.svg                (installs what it needs)
    uv run build.py assets/hero.src.svg assets/readme/*.src.svg
    python build.py assets/hero.src.svg                (after: pip install fonttools brotli)

The file name says what is built: hero.src.svg is the hero (1280x640), and any
other name is a section scene (1280x448).

The source starts with a palette comment, one role per line (name dark light):

    <!--palette
    bg     #0F1115 #F0F5FB
    accent #4FD1C5 #0B7A70
    -->

and uses the roles as $bg, $accent... anywhere in the SVG. The build measures the
source (check.py: sizes, overflow, contrast, loops), swaps the roles per theme,
embeds subsets of the fonts (classes .s text, .b bold, .m mono), turns text that
moves into outlines so it travels without pixel jumps, adds the reduced-motion
rule, and writes a preview page plus two pictures of it: the loop as eight frozen
frames, and the finished frame as GitHub shows it in both themes. A hero also gives
its social preview, the card GitHub shows when the repository is shared: a still
vector (assets/social-preview.svg) and the PNG GitHub takes, shot from it.

An optional <!--brief ... --> comment holds what the hero claims and where each claim
comes from: the preview page shows it, the outputs leave it out. Several sources at
once (assets/options/*/hero.src.svg) build each one and add a page with them side by side.
"""
import base64, glob, hashlib, html, io, os, re, shutil, struct, subprocess, sys, tempfile, zlib
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check  # noqa: E402
from check import FACES, SVG, XMLSPACE, font, num  # noqa: E402

RASTER_KB = 400  # a real screenshot inside a scene: past this the README loads slowly
# GitHub's social preview: 1280x640 for best display, PNG, JPG or GIF under 1 MB. Its template
# keeps what matters 80 px from every edge (40 pt at 2x), where other sites crop the card.
SOCIAL = (1280, 640)
SOCIAL_SAFE = 80
SOCIAL_BYTES = 1024 * 1024


LIBRARY = Path(__file__).resolve().parent.parent / "assets" / "library"


def asset_notice(body):
    """The notices of the asset sets a picture uses, as invisible <metadata>: the set's licence travels with its icons, nothing shows."""
    used = sorted({m.split(":")[0] for m in re.findall(r'data-asset="([^"]+)"', body)})
    if not used or not (LIBRARY / "manifest.json").exists():
        return ""
    import json
    sets = {s["prefix"]: s for s in json.loads((LIBRARY / "manifest.json").read_text(encoding="utf-8"))["sets"]}
    lines, texts = [], {}
    for prefix in used:
        s = sets.get(prefix)
        if not s:
            continue
        lines.append(f"{s['title']} ({prefix}): {s['licence']}, {s['holder']}, {s['repo']}")
        if "CC0" not in s["licence"]:
            texts.setdefault(s["licence_text"], (LIBRARY / s["licence_text"]).read_text(encoding="utf-8").strip())
    text = "Assets used in this picture:\n" + "\n".join(lines) + ("\n\n" + "\n\n".join(texts.values()) if texts else "")
    return "<metadata>" + html.escape(text, quote=False) + "</metadata>"


_whole = {}


def subset_font(face, chars):
    from fontTools import subset
    from fontTools.ttLib import TTFont

    # subsetting changes the font in place: work on a fresh copy, or the next source of the same run loses letters
    if face not in _whole:
        buf = io.BytesIO()
        font(face).recalcTimestamp = False
        font(face).save(buf)
        _whole[face] = buf.getvalue()
    f = TTFont(io.BytesIO(_whole[face]), recalcTimestamp=False)  # no build time in the font: the same source builds the same bytes
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

def outline_moving_text(root, warns, moves):
    from fontTools.pens.svgPathPen import SVGPathPen

    parent = {c: p for p in root.iter() for c in p}

    def chain(el):
        while el is not None:
            yield el
            el = parent.get(el)

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


# ---- pictures of the result
def freeze(svg, t):
    """The same SVG, stopped t seconds into its loop: every animation paused with its delay moved back by t."""
    def shifted(v):
        return ",".join(f"{check.seconds(d.strip()) - t:.3f}s" for d in v.split(","))

    def delay(m):
        try:
            return m.group(1) + shifted(m.group(2))
        except ValueError:
            return m.group(0)

    def shorthand(m):
        if m.group(2).strip().startswith("none"):
            return m.group(0)
        delays = [check.parse_animation(p, ())["delay"] for p in check.split_commas(m.group(2))]
        return m.group(0) + ";animation-delay:" + ",".join(f"{d - t:.3f}s" for d in delays)

    svg = re.sub(r"(animation-delay\s*:\s*)([^;}\"]+)", delay, svg)
    svg = re.sub(r"(animation\s*:\s*)([^;}\"]+)", shorthand, svg)
    return svg.replace("</svg>", "<style>*{animation-play-state:paused!important}</style></svg>")


def find_browsers():
    """Chromium-family browsers that can take the pictures, best first."""
    home = Path.home()
    paths = [os.environ.get("JANO_BROWSER")]
    # the headless shell Playwright downloads starts fastest and never opens a window
    caches = (Path(os.environ.get("LOCALAPPDATA") or home) / "ms-playwright", home / ".cache/ms-playwright", home / "Library/Caches/ms-playwright")
    for pat in ("chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell*", "chromium-*/chrome-win*/chrome.exe",
                "chromium-*/chrome-linux*/chrome", "chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium"):
        for cache in caches:
            paths += sorted(map(str, cache.glob(pat)), reverse=True)[:1]
    names = ("chrome-headless-shell", "chrome", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "msedge", "microsoft-edge")
    paths += [shutil.which(n) for n in names]
    for root in (os.environ.get("PROGRAMFILES"), os.environ.get("PROGRAMFILES(X86)"), os.environ.get("LOCALAPPDATA")):
        if root:
            paths += [str(Path(root) / "Google/Chrome/Application/chrome.exe"), str(Path(root) / "Microsoft/Edge/Application/msedge.exe")]
    paths += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
              "/Applications/Chromium.app/Contents/MacOS/Chromium"]
    return list(dict.fromkeys(p for p in paths if p and Path(p).is_file()))


def shoot(browser, page, png, height, width=1320):
    """A PNG of a local page. True when it was written."""
    profile = tempfile.mkdtemp(prefix="jano-browser-")
    png.unlink(missing_ok=True)
    args = [browser, "--disable-gpu", "--hide-scrollbars", "--no-first-run", "--no-sandbox", f"--user-data-dir={profile}",
            "--force-device-scale-factor=1", f"--window-size={width},{height}", f"--screenshot={png}", page.as_uri()]
    if "headless-shell" not in Path(browser).name:
        args.insert(1, "--headless")
    try:
        # no pipes: a browser's child processes keep them open and the wait never ends
        proc = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            proc.wait(45)
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
            proc.kill()
    except OSError:
        pass
    shutil.rmtree(profile, ignore_errors=True)
    return png.exists() and png.stat().st_size > 0


def take_pictures(shots):
    """Shoots every (page, png, height) with the first browser that works. True when all were written."""
    for browser in find_browsers()[:3]:
        if all(shoot(browser, *shot) for shot in shots):
            return True
    return False


def png_size(png):
    """(width, height) of a PNG, read from its header."""
    return struct.unpack(">II", png.read_bytes()[16:24])


def png_stamp(png, sha):
    """Writes the fingerprint of the source into the PNG as a text chunk, right after the header."""
    data = png.read_bytes()
    body = b"tEXt" + b"jano-src\0" + sha.encode()
    chunk = struct.pack(">I", len(body) - 4) + body + struct.pack(">I", zlib.crc32(body))
    png.write_bytes(data[:33] + chunk + data[33:])


def social_svg(svg, sha):
    """The social preview as a still vector: the hero's finished frame (dark), scaled into the safe area, on its own background."""
    w, h = SOCIAL
    scale = (w - 2 * SOCIAL_SAFE) / w
    # the background is the fill of the first shape that covers the whole canvas
    bg = "#0d1117"
    for rect in re.findall(r"<rect\b[^>]*>", svg):
        fill = re.search(r'fill="(#[0-9A-Fa-f]{3,8})"', rect)
        if fill and re.search(r'width="(1280|100%)"', rect) and re.search(r'height="(640|100%)"', rect):
            bg = fill.group(1)
            break
    label = re.search(r'aria-label="([^"]*)"', svg)
    inner = svg.replace("<svg ", f'<svg x="{SOCIAL_SAFE}" y="{(h - h * scale) / 2:g}" width="{w * scale:g}" height="{h * scale:g}" ', 1)
    inner = inner.replace("</svg>", "<style>*{animation:none!important}</style></svg>")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" data-jano-src="{sha}" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{label.group(1) if label else "social preview"}"><rect width="{w}" height="{h}" fill="{bg}"/>{inner}</svg>')


def build(src):
    """Builds one source. Returns what the options page needs, or None when the source has errors."""
    out = src.parent
    kind = check.kind_of(src)
    stem = src.name.split(".")[0]
    raw = src.read_text(encoding="utf-8")
    brief = re.search(r"<!--\s*brief(.*?)-->", raw, re.S)
    if brief:
        raw = raw.replace(brief.group(0), "")
        brief = brief.group(1).strip()
    errors, warns = [], []
    palette, body = check.read_source(raw)

    # ---- what GitHub will not show, or will show wrong
    w, h = check.CANVAS[kind]
    if f'viewBox="0 0 {w} {h}"' not in body:
        errors.append(f'viewBox must be "0 0 {w} {h}" for {"the hero" if kind == "hero" else "a section scene"}')
    if 'role="img"' not in body or "aria-label=" not in body:
        errors.append('root <svg> needs role="img" and an aria-label that says what the picture shows')
    for bad in ("<script", "<foreignObject", "@import"):
        if bad in body:
            errors.append(f"{bad} is not allowed: GitHub shows the SVG as an image, nothing external loads")
    # a real screenshot is the one picture a scene may hold, embedded; the hero stays drawn
    images = re.findall(r"<image\b[^>]*>", body)
    for im in images:
        if kind != "section" or not re.search(r"""href\s*=\s*["']data:image/(png|jpeg|webp|gif);base64,""", im):
            errors.append("<image> is not allowed" + ("" if kind == "section" else " in the " + kind) + ": GitHub shows the SVG as an image, nothing external loads. A section scene may embed a real screenshot as a data:image URI, when the user agreed to one")
            break
    raster = sum(len(m) for m in re.findall(r"data:image/[a-z]+;base64,([A-Za-z0-9+/=]+)", body)) * 3 / 4 / 1024
    if raster > RASTER_KB:
        warns.append(f"the embedded screenshot(s) weigh {raster:.0f} KB: crop to what the scene shows and save as JPEG or WebP, under {RASTER_KB} KB")
    # only addresses something would load: one written as visible text is fine
    ext = re.findall(r"""(?:href|src)\s*=\s*["'](https?://[^"']+)|url\(\s*["']?(https?://[^"')\s]+)""", body)
    ext = [a or b for a, b in ext if "www.w3.org" not in (a or b)]
    if ext:
        errors.append(f"external URL(s) will not load: {ext[:3]}")
    if "<style>" not in body:
        errors.append("no <style> block: the hero has no animation")
    for a in re.findall(r"animation\s*:\s*([^;}\"]+)", body):
        if "infinite" not in a and "none" not in a:
            errors.append(f"animation without 'infinite' (it would play once, like a video): {a.strip()}")
    for d in re.findall(r"animation-delay\s*:\s*([^;}\"]+)", body):
        if not d.strip().startswith("-") and d.strip() not in ("0s", "0"):
            warns.append(f"positive animation-delay {d.strip()}: the first loop starts frozen. Use a negative delay to shift phase")
    if re.search(r"repeatCount=\"(?!indefinite)", body):
        errors.append("SMIL animation must use repeatCount=\"indefinite\"")
    used = set(re.findall(r"\$([a-z][a-z0-9_]*)", body))
    for u in used - set(palette):
        errors.append(f"${u} is used but not in the palette")

    # ---- what can be measured: sizes, overflow, contrast, loops
    ET.register_namespace("", SVG)
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    try:
        root = ET.fromstring(body)
    except ET.ParseError as e:
        print(f"error: the SVG is not well-formed XML: {e}")
        return None
    hero = check.check(root, palette, kind)
    errors = list(dict.fromkeys(errors + hero.errors))
    warns += hero.warns
    if errors:
        print("\n".join("error: " + e for e in errors))
        return None

    # ---- moving text to outlines
    outlined = outline_moving_text(root, warns, lambda el: hero.mover(el) is not None)
    body = ET.tostring(root, encoding="unicode")

    # ---- fonts for the text that stays still
    text = re.sub(r"<style>.*?</style>", "", body, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    chars = "".join(sorted(set(text) - set("\n\r\t"))) + " "
    faces = (
        f"@font-face{{font-family:SG;src:url(data:font/woff2;base64,{subset_font('s', chars)}) format('woff2')}}"
        f"@font-face{{font-family:SG7;src:url(data:font/woff2;base64,{subset_font('b', chars)}) format('woff2')}}"
        f"@font-face{{font-family:JB;src:url(data:font/woff2;base64,{subset_font('m', chars)}) format('woff2')}}\n"
        "text{text-rendering:geometricPrecision}.s{font-family:SG,sans-serif}.b{font-family:SG7,sans-serif;font-weight:700}.m{font-family:JB,monospace;font-variant-ligatures:none}\n"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}\n"
    )
    body = body.replace("<style>", "<style>" + faces, 1)

    names, themed = [], []
    # the outputs carry a fingerprint of their source, so a check can tell a stale build in any clone, whatever the file dates
    print_sha = hashlib.sha256(src.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:16]  # line endings as git stores them
    body = body.replace("<svg ", f'<svg data-jano-src="{print_sha}" ', 1)
    notice = asset_notice(body)
    for ti, theme in enumerate(("dark", "light")):
        svg = re.sub(r"\$([a-z][a-z0-9_]*)", lambda k: palette[k.group(1)][ti], body)
        svg = svg.replace("</svg>", notice + "</svg>") if notice else svg  # after the palette and the fonts: the notice is text nobody sees
        f = out / f"{stem}-{theme}.svg"
        f.write_text(svg + "\n", encoding="utf-8", newline="\n")
        names.append(f)
        themed.append(svg)
        kb = len(svg.encode()) / 1024
        if kb - raster > 200:
            warns.append(f"{f.name} is {kb:.0f} KB: simplify, a picture should stay under 200 KB (screenshots apart)")
        print(f"wrote {f} ({kb:.0f} KB)")
    print(f"{outlined} moving text element(s) turned into outlines")

    # ---- preview: one folder per source path, so two repos with the same name do not overwrite each other
    tag = hashlib.sha1(str(src).encode()).hexdigest()[:8]
    repo = next((p for p in src.parents if (p / ".git").exists() or (p / "README.md").exists()), src.parent.parent)
    folder = Path(tempfile.gettempdir()) / f"{stem}-preview-{repo.name}-{tag}"
    folder.mkdir(exist_ok=True)
    cycle = hero.facts.get("cycle_seconds") or 6
    times = [round(cycle * i / 8, 2) for i in range(8)]
    for i, t in enumerate(times):
        (folder / f"frame-{i}.svg").write_text(freeze(themed[0], t), encoding="utf-8")
    # with motion off a hero shows its finished frame: that is the picture of each theme
    for theme, svg in zip(("dark", "light"), themed):
        (folder / f"still-{theme}.svg").write_text(svg.replace("</svg>", "<style>*{animation:none!important}</style></svg>"), encoding="utf-8")
    css = ("<!doctype html><meta charset=utf-8><title>hero preview</title><style>body{margin:0;font:14px system-ui;background:#0d1117;color:#f0f6fc}"
           "section{padding:20px 32px}p{margin:0 0 8px}img{display:block;margin:0 0 20px}.g{display:grid;grid-template-columns:1fr 1fr;gap:12px 16px}.g img{width:100%;margin:0}"
           ".l img{display:inline-block;margin-right:16px;vertical-align:middle}.w{background:#fff;color:#1f2328}.r{display:flex;gap:24px;align-items:flex-start}</style>")
    logo = out / "logo.svg"
    logos = "".join(f'<img src="{logo.as_uri()}" width="{s}" height="{s}">' for s in (16, 24, 48, 96)) if logo.exists() else "<i>no assets/logo.svg</i>"

    # the loop, stopped at eight moments: what moves, where it goes, and whether the last frame leads back into the first
    loop = css + f"<section><p>the loop, stopped every {cycle / 8:.2g} s of {cycle:g} s (dark)</p><div class=g>"
    loop += "".join(f'<div><p>{t:g} s</p><img src="frame-{i}.svg"></div>' for i, t in enumerate(times)) + "</div></section>"
    (folder / "loop.html").write_text(loop, encoding="utf-8")
    # the hero as GitHub shows it with motion off: both themes at README width, a phone, and blurred
    wide = 838
    look = css + f'<section><p>dark, README width, motion off: the finished frame</p><img src="still-dark.svg" width="{wide}"></section>'
    look += f'<section class=w><p>light, README width, motion off: the finished frame</p><img src="still-light.svg" width="{wide}"></section>'
    look += ('<section><div class=r><div><p>phone (360 px)</p><img src="still-dark.svg" width="360"></div>'
             '<div><p>words blurred: is the story still there?</p><img src="still-dark.svg" width="400" style="filter:blur(3px)"></div>'
             '<div><p>phone, light</p><img src="still-light.svg" width="360"></div></div></section>')
    (folder / "look.html").write_text(look, encoding="utf-8")
    # the live page, for a person or a browser tool
    page = css.replace("background:#0d1117;color:#f0f6fc", "")
    if brief:
        page += f'<section><p>brief: check each claim before the hero goes in the README</p><pre style="white-space:pre-wrap;margin:0">{html.escape(brief)}</pre></section>'
    for f, bg, fg in ((names[0], "#0d1117", "#f0f6fc"), (names[1], "#ffffff", "#1f2328")):
        page += f'<section style="background:{bg};color:{fg}"><p>{f.name} at README width (838px)</p><img src="{f.as_uri()}" width="838"><p>phone (360px)</p><img src="{f.as_uri()}" width="360"><p class="l">logo {logos}</p></section>'
    prev = folder / "index.html"
    prev.write_text(page, encoding="utf-8")
    print(f"preview {prev}")
    shots = [(folder / "loop.html", folder / "loop.png", 1480), (folder / "look.html", folder / "look.png", 1290)]
    # the repository's social preview comes from its hero, so the two never drift apart; an option is not the hero yet
    social = out / "social-preview.png" if kind == "hero" and out.parent.name != "options" else None
    if social:
        # the card is drawn as a vector first, so it stays sharp at any size; the PNG GitHub takes is shot from it
        card = social.with_suffix(".svg")
        card.write_text(social_svg(themed[0], print_sha) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {card} ({len(card.read_bytes()) / 1024:.0f} KB)")
        page = folder / "social.html"
        page.write_text(f'<!doctype html><body style="margin:0;overflow:hidden"><img src="{card.as_uri()}" width="{SOCIAL[0]}" height="{SOCIAL[1]}" style="display:block">', encoding="utf-8")
        shots.append((page, social, SOCIAL[1], SOCIAL[0]))
    if "--no-pictures" in sys.argv:
        if social:
            print(f"no social preview: {social.name} needs the pictures; build without --no-pictures")
    elif take_pictures(shots):
        print(f"pictures {shots[0][1]} {shots[1][1]}")
        if social:
            png_stamp(social, print_sha)
            size, kb = png_size(social), social.stat().st_size / 1024
            if size != SOCIAL:
                warns.append(f"{social.name} came out {size[0]}x{size[1]}, not {SOCIAL[0]}x{SOCIAL[1]}: set JANO_BROWSER to another Chromium-family browser")
            if social.stat().st_size >= SOCIAL_BYTES:
                warns.append(f"{social.name} is {kb:.0f} KB and GitHub takes 1 MB at most: fewer gradients and fine textures in the hero")
            print(f"social preview {social} ({size[0]}x{size[1]}, {kb:.0f} KB): upload it in Settings > General > Social preview")
    else:
        print(f"no pictures: no Chrome, Chromium or Edge could take them (set JANO_BROWSER to one). Open {folder / 'loop.html'} and {folder / 'look.html'} in a browser instead")
        if social:
            print(f"no social preview: {social.name} needs the same browser")
    print(check.summary(hero.facts))
    print("\n".join("warning: " + w for w in dict.fromkeys(warns)) or "checks passed")
    return {"files": names, "brief": brief}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sources = []
    for a in (a for a in sys.argv[1:] if not a.startswith("--")):
        # PowerShell and cmd hand the pattern over as it is written: expand it here
        found = sorted(glob.glob(a)) if any(c in a for c in "*?[") else ([a] if Path(a).exists() else [])
        if not found:
            sys.exit(f"error: no file matches {a}")
        sources += [Path(f).resolve() for f in found]
    if not sources:
        sys.exit(__doc__)
    built = []
    for src in sources:
        if len(sources) > 1:
            print(f"\n== {src}")
        built.append(build(src))
    if len(sources) > 1 and all(s.name == "hero.src.svg" for s in sources):
        # the options side by side, each with its brief, so the user can pick one or mix parts of several
        tag = hashlib.sha1("|".join(map(str, sources)).encode()).hexdigest()[:8]
        page = Path(tempfile.gettempdir()) / f"hero-options-{tag}.html"
        body = ("<!doctype html><meta charset=utf-8><title>hero options</title><style>body{margin:0;font:14px system-ui;background:#0d1117;color:#f0f6fc}"
                "section{padding:20px 32px;border-bottom:1px solid #30363d}h2{margin:0 0 12px;font-size:16px}.r{display:grid;grid-template-columns:1fr 1fr;gap:16px}"
                "img{width:100%;display:block}pre{white-space:pre-wrap;margin:12px 0 0;color:#9da7b3}</style>")
        for src, b in zip(sources, built):
            name = html.escape(src.parent.name)
            if b is None:
                body += f"<section><h2>{name}</h2><p>did not build: see its errors above</p></section>"
                continue
            body += f'<section><h2>{name}</h2><div class=r><img src="{b["files"][0].as_uri()}"><img src="{b["files"][1].as_uri()}" style="background:#fff"></div>'
            body += (f"<pre>{html.escape(b['brief'])}</pre>" if b["brief"] else "") + "</section>"
        page.write_text(body, encoding="utf-8")
        print(f"\noptions {page}")
    sys.exit(1 if None in built else 0)


if __name__ == "__main__":
    main()
