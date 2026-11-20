#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["fonttools", "brotli"]
# ///
"""Measure a hero source and report what a viewer would see go wrong.

    uv run check.py assets/hero.src.svg           (errors, warnings and the measured figures)
    uv run check.py assets/hero.src.svg --json    (the same, as JSON)

build.py runs these checks on every build. They measure the source: where each
shape and each line of text lands on the 1280x640 canvas (text is measured with
the real fonts), how far and how fast each animation travels, and whether each
loop closes on itself. Nothing here judges whether the picture is a good idea;
it catches what can be counted.
"""
import json, math, re, sys
import xml.etree.ElementTree as ET
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
SVG = "http://www.w3.org/2000/svg"
XLINK = "{http://www.w3.org/1999/xlink}href"
XMLSPACE = "{http://www.w3.org/XML/1998/namespace}space"
FACES = {"s": ("SpaceGrotesk.ttf", 500), "b": ("SpaceGrotesk.ttf", 700), "m": ("JetBrainsMono.ttf", None)}
W, H = 1280, 640       # the canvas of the source being checked: set by check() from its kind
CANVAS = {"hero": (1280, 640), "section": (1280, 448)}
README = 838 / 1280    # GitHub shows a 1280 px wide picture at about this scale
SKIP = {"defs", "clipPath", "mask", "pattern", "linearGradient", "radialGradient", "symbol", "style", "title",
        "desc", "metadata", "filter", "marker"}
CHEAP = {"transform", "opacity"}  # composited: smooth everywhere
PAINTED = {"stroke-dashoffset", "offset-distance"}  # repainted each frame, accepted for flow lines and paths
IGNORED = {"animation-timing-function", "transform-origin", "transform-box", "offset-path", "offset-rotate"}
NAMED = {"white": "#ffffff", "black": "#000000"}

# ---- limits, in canvas pixels unless said otherwise
MIN_TEXT = 13          # 8.5 px at README width
LABEL_TEXT = 16        # most of the text is at least this: 10.5 px at README width
SMALL_SHARE = 0.5      # share of the lines of text that may be smaller than LABEL_TEXT
NAME_SIZE = (26, 64)   # the repository name
LOGO_SIZE = (32, 160)  # the shorter side of the logo
TAGLINE_SIZE = (38, 68)  # the key phrase: the largest text on the canvas
TAGLINE_WORDS = 10
ABOUT_SIZE = (18, 26)  # the description under the key phrase
ABOUT_WORDS = (8, 24)
FACT_SIZE = 24         # a figure in #facts is at least this large
FACTS = 4              # figures at most; none is fine when features or nothing stand there
STAGE_SHARE = 0.34     # of the canvas
COPY_SHARE = (0.25, 0.55)  # the text block against text block + picture: only the extremes are reported
STAGE_PARTS = 24       # shapes and lines of text the picture is made of
STAGE_LARGE = 140      # px: the shorter side of the object that anchors the picture
STAGE_SMALL = (48, 6)  # px, count: details whose shorter side is this or less
STAGE_MOVING = 5       # animated elements in the picture
EDGE = 24              # still text keeps this far from the canvas edge
BOX_PAD = 8            # px: text keeps at least this far from the sides of the box it sits in,
PILL_PAD = 0.5         # and half its size in a pill (a box under PILL_HIGH times the text's size),
PANEL_PAD = 1.0        # or its own size in a panel, on the left and right,
PANEL_PAD_Y = 0.5      # and half its size above and below
PILL_HIGH = 2.6
SMALL_BOX_PAD = 0.12   # a shape in a box under BOX_PAD / this px keeps this share of the box's shorter side
MISSING_EM = 1.25      # a character the fonts lack is drawn by a fallback font of each machine: count it this wide
STILL_WORDS = 48       # words standing still in the picture
LABEL_WORDS = 10        # in one still line
SIZES = 7              # distinct font sizes
MIN_TRAVEL, MIN_SCALE, MIN_TURN, MIN_FADE = 6, 0.03, 2, 0.12
MAX_SPEED = 700        # px/s: faster than this cannot be followed
MAX_TEXT_SPEED = 130   # px/s for text that travels
MIN_STEP = 0.1         # s: a change faster than this reads as a glitch
STEP_JUMP = 24         # px per step of a steps() animation
DURATION = (0.4, 60)   # s
LEAD_TRAVEL = 40       # px: something in the stage travels at least this far
LEAD_SIZE = 20         # px: and the largest thing that travels is at least this big on its shorter side
SYNC_SLACK = 0.3      # seconds a lit label may run ahead of or behind the box that highlights it
LINE_CONTRAST = 3      # a connector with walking dashes against the background
ICON_CONTRAST = 3      # an icon against what it sits on (WCAG 1.4.11, non-text)
ICON_MAX = 40          # px: thin strokes in a cluster smaller than this are a pictogram, and must say what they mean
ICON_MIN = 24          # px: an icon's grid on the canvas, 16 px at README width
ICON_STROKE = 2        # px: the thinnest line an icon may have on the canvas
# a section scene: a short canvas with a headline that says what the section claims, and a picture that shows it
TITLE_SIZE = (34, 56)  # the headline of the scene: the largest text on it
TITLE_WORDS = 8
SUB_SIZE = (16, 24)
SUB_WORDS = (3, 18)
EYEBROW_SIZE = (13, 18)  # a short label over the headline, in the accent
SCENE_STAGE_SHARE = 0.45
SCENE_COPY_SHARE = (0.1, 0.45)
SCENE_PARTS = 18
SCENE_LARGE = 110

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


def length(v, size, default=0.0):
    """A length in px; em is relative to the font size."""
    return num(v, default) * (size if v and v.strip().endswith("em") else 1)


def text_width(text, size, face="s", spacing=0.0):
    """Width of one line in px with the skill's fonts, and the characters they lack (counted MISSING_EM wide)."""
    f = font(face)
    k, cmap, hmtx = size / f["head"].unitsPerEm, f.getBestCmap(), f["hmtx"]
    w, lost = 0.0, set()
    for ch in text:
        if ord(ch) in cmap:
            w += hmtx[cmap[ord(ch)]][0] * k + spacing
        elif not ch.isspace():
            w += MISSING_EM * size + spacing
            lost.add(ch)
    return w, lost


def local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def num(v, default=0.0):
    m = re.search(r"-?\d*\.?\d+(?:e-?\d+)?", v or "")
    return float(m.group()) if m else default


def seconds(v):
    return float(v[:-2]) / 1000 if v.endswith("ms") else float(v[:-1])


# ---- geometry: matrices are (a b c d e f), boxes are (x0 y0 x1 y1)
IDENT = (1, 0, 0, 1, 0, 0)


def mul(m, n):
    a, b, c, d, e, f = m
    A, B, C, D, E, F = n
    return (a * A + c * B, b * A + d * B, a * C + c * D, b * C + d * D, a * E + c * F + e, b * E + d * F + f)


def vec(m, x, y):
    return m[0] * x + m[2] * y, m[1] * x + m[3] * y


def mscale(m):
    return math.sqrt(abs(m[0] * m[3] - m[1] * m[2]))


def parse_transform(s):
    m = IDENT
    for fn, args in re.findall(r"(\w+)\s*\(([^)]*)\)", s or ""):
        v = [float(x) for x in re.findall(r"-?\d*\.?\d+(?:e-?\d+)?", args)]
        if fn == "translate" and v:
            t = (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0)
        elif fn == "scale" and v:
            t = (v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0)
        elif fn == "rotate" and v:
            c, s_ = math.cos(math.radians(v[0])), math.sin(math.radians(v[0]))
            t = (c, s_, -s_, c, 0, 0)
            if len(v) == 3:
                t = mul(mul((1, 0, 0, 1, v[1], v[2]), t), (1, 0, 0, 1, -v[1], -v[2]))
        elif fn == "matrix" and len(v) == 6:
            t = tuple(v)
        elif fn == "skewX" and v:
            t = (1, 0, math.tan(math.radians(v[0])), 1, 0, 0)
        elif fn == "skewY" and v:
            t = (1, math.tan(math.radians(v[0])), 0, 1, 0, 0)
        else:
            continue
        m = mul(m, t)
    return m


def tbox(m, b):
    xs, ys = zip(*[(m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5]) for x in (b[0], b[2]) for y in (b[1], b[3])])
    return (min(xs), min(ys), max(xs), max(ys))


def union(a, b):
    if a is None or b is None:
        return a or b
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


def inter(a, b):
    c = (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))
    return c if c[0] < c[2] and c[1] < c[3] else None


def area(b):
    return max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1]) if b else 0.0


def shift(b, dx, dy):
    return (b[0] + dx, b[1] + dy, b[2] + dx, b[3] + dy)


def shape_box(el):
    tag, g = local(el.tag), el.get

    def n(a, total=0):
        v = g(a) or ""
        return num(v) / 100 * total if v.strip().endswith("%") else num(v)

    if tag == "rect":
        return (n("x", W), n("y", H), n("x", W) + n("width", W), n("y", H) + n("height", H))
    if tag == "circle":
        return (n("cx") - n("r"), n("cy") - n("r"), n("cx") + n("r"), n("cy") + n("r"))
    if tag == "ellipse":
        return (n("cx") - n("rx"), n("cy") - n("ry"), n("cx") + n("rx"), n("cy") + n("ry"))
    if tag == "line":
        return (min(n("x1"), n("x2")), min(n("y1"), n("y2")), max(n("x1"), n("x2")), max(n("y1"), n("y2")))
    if tag in ("polyline", "polygon"):
        v = [float(x) for x in re.findall(r"-?\d*\.?\d+(?:e-?\d+)?", g("points") or "")]
        if len(v) >= 2:
            return (min(v[0::2]), min(v[1::2]), max(v[0::2]), max(v[1::2]))
    if tag == "path" and g("d"):
        try:
            from fontTools.pens.boundsPen import BoundsPen
            from fontTools.svgLib.path import parse_path

            pen = BoundsPen(None)
            parse_path(g("d"), pen)
            return pen.bounds
        except Exception:
            return None
    return None


# ---- CSS: enough of it to know which element runs which animation
def declarations(body):
    out = {}
    for d in body.split(";"):
        if ":" in d:
            k, v = d.split(":", 1)
            out[k.strip().lower()] = v.strip()
    return out


def parse_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    keyframes, twice = {}, set()

    def take(m):
        stops = {}
        for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", m.group(2)):
            for s in sel.split(","):
                s = s.strip().lower()
                p = 0.0 if s == "from" else 100.0 if s == "to" else num(s, -1)
                if p >= 0:
                    stops.setdefault(p, {}).update(declarations(body))
        if m.group(1) in keyframes and keyframes[m.group(1)] != sorted(stops.items()):
            twice.add(m.group(1))
        keyframes[m.group(1)] = sorted(stops.items())
        return ""

    css = re.sub(r"@keyframes\s+([\w-]+)\s*\{((?:[^{}]*\{[^{}]*\})*)\s*\}", take, css)
    css = re.sub(r"@[\w-]+[^{;]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", "", css)  # @media, @font-face, @supports
    rules = [(sel.strip(), declarations(body)) for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css)]
    keyframes["__twice__"] = sorted(twice)
    return keyframes, rules


def split_commas(v):
    return [p.strip() for p in re.split(r",(?![^(]*\))", v) if p.strip()]


EASINGS = ("linear", "ease", "ease-in", "ease-out", "ease-in-out", "step-start", "step-end")


def parse_animation(value, known):
    """One animation of a shorthand -> dict(name, dur, delay, timing, count, direction)."""
    a = {"name": None, "dur": 0.0, "delay": 0.0, "timing": "ease", "count": "1", "direction": "normal"}
    times = []
    for t in re.findall(r"[\w-]+\([^)]*\)|\S+", value):
        if re.fullmatch(r"-?\d*\.?\d+m?s", t):
            times.append(seconds(t))
        elif t in known:
            a["name"] = t
        elif t == "infinite" or re.fullmatch(r"\d*\.?\d+", t):
            a["count"] = t
        elif t in EASINGS or t.startswith(("cubic-bezier(", "steps(", "linear(")):
            a["timing"] = t
        elif t in ("alternate", "reverse", "alternate-reverse", "normal"):
            a["direction"] = t
        elif t in ("none", "both", "forwards", "backwards", "running", "paused"):
            continue
        elif a["name"] is None:
            a["name"] = t
    if times:
        a["dur"] = times[0]
    if len(times) > 1:
        a["delay"] = times[1]
    return a


def transform_parts(v):
    """A keyframe's transform -> (tx, ty, sx, sy, rotation), or None when it uses % or something else."""
    tx = ty = rot = 0.0
    sx = sy = 1.0
    for fn, args in re.findall(r"([\w]+)\s*\(([^)]*)\)", v or ""):
        if "%" in args or "calc" in args:
            return None
        n = [float(x) for x in re.findall(r"-?\d*\.?\d+(?:e-?\d+)?", args)]
        if not n:
            continue
        if fn in ("translate", "translate3d"):
            tx, ty = tx + n[0], ty + (n[1] if len(n) > 1 else 0)
        elif fn == "translateX":
            tx += n[0]
        elif fn == "translateY":
            ty += n[0]
        elif fn == "scale":
            sx, sy = sx * n[0], sy * (n[1] if len(n) > 1 else n[0])
        elif fn == "scaleX":
            sx *= n[0]
        elif fn == "scaleY":
            sy *= n[0]
        elif fn in ("rotate", "rotateZ"):
            rot += n[0] * (360 if "turn" in args else 57.29578 if "rad" in args else 1)
        elif fn in ("translateZ", "perspective"):
            continue
        else:
            return None
    return (tx, ty, sx, sy, rot)


class Hero:
    def __init__(self, root, palette, kind="hero"):
        self.root, self.palette, self.kind = root, palette, kind
        self.errors, self.warns, self.facts = [], [], {}
        self.parent = {c: p for p in root.iter() for c in p}
        self.byid = {e.get("id"): e for e in root.iter() if e.get("id")}
        self.order = {e: i for i, e in enumerate(root.iter())}
        css = "".join(e.text or "" for e in root.iter(f"{{{SVG}}}style"))
        self.keyframes, self.rules = parse_css(css)
        self.twice = self.keyframes.pop("__twice__")
        self._style, self._anims = {}, {}
        self.M, self.box, self.texts, self.shapes = {}, {}, [], []
        self.measure(root, IDENT, True)

    # ---- what an element is
    def chain(self, el):
        while el is not None:
            yield el
            el = self.parent.get(el)

    def describe(self, el):
        for t in self.texts:
            if t["el"] is el:
                return '"' + (t["s"] if len(t["s"]) < 34 else t["s"][:31] + "...") + '"'
        bits = "".join(f' {a}="{el.get(a)}"' for a in ("id", "class", "x", "y", "cx", "cy", "data-kit") if el.get(a))
        return f"<{local(el.tag)}{bits}>"

    def style(self, el):
        if el not in self._style:
            out, classes = {}, set((el.get("class") or "").split())
            for sel, decl in self.rules:
                for part in sel.split(","):
                    comp = re.sub(r"::?[\w-]+(\([^)]*\))?", "", (part.split() or [""])[-1])
                    if not comp or comp == "*":
                        continue
                    tag = re.match(r"[a-zA-Z][\w-]*", comp)
                    if tag and tag.group() != local(el.tag):
                        continue
                    ids = re.findall(r"#([\w-]+)", comp)
                    if all(c in classes for c in re.findall(r"\.([\w-]+)", comp)) and all(i == el.get("id") for i in ids):
                        out.update(decl)
                        break
            out.update(declarations(el.get("style") or ""))
            self._style[el] = out
        return self._style[el]

    def anims(self, el):
        if el not in self._anims:
            st, out = self.style(el), []
            if st.get("animation") and st["animation"] != "none":
                out = [parse_animation(p, self.keyframes) for p in split_commas(st["animation"])]
            elif st.get("animation-name"):
                out = [parse_animation(st["animation-name"], self.keyframes)]
            for key, field in (("animation-delay", "delay"), ("animation-duration", "dur")):
                if st.get(key):
                    vals = split_commas(st[key])
                    for i, a in enumerate(out):
                        try:
                            a[field] = seconds(vals[i % len(vals)])
                        except ValueError:
                            pass
            for a in out:
                a["stops"] = self.keyframes.get(a["name"])
                a["props"] = {p for _, d in a["stops"] or [] for p in d} - IGNORED
            self._anims[el] = out
        return self._anims[el]

    def mover(self, el):
        """Nearest element, itself included, whose animation moves it."""
        for a in self.chain(el):
            if any(x["props"] & {"transform", "offset-distance"} for x in self.anims(a)):
                return a
        return None

    def fades(self, el):
        return any("opacity" in x["props"] for a in self.chain(el) for x in self.anims(a))

    def inherit(self, el, attr, default=None):
        for a in self.chain(el):
            if a.get(attr) is not None:
                return a.get(attr)
            if attr in self.style(a):
                return self.style(a)[attr]
        return default

    def face(self, el):
        for a in self.chain(el):
            for c in (a.get("class") or "").split():
                if c in FACES:
                    return c
        return None

    def color(self, value, theme):
        v = (value or "").strip()
        if v.startswith("$"):
            return self.palette.get(v[1:], (None, None))[theme]
        return NAMED.get(v.lower(), v if re.fullmatch(r"#[0-9a-fA-F]{3}|#[0-9a-fA-F]{6}", v) else None)

    # ---- where everything lands on the canvas
    def measure(self, el, M, record):
        tag = local(el.tag)
        if tag in SKIP and not (tag == "symbol" and not record):
            return None
        if self.inherit(el, "display") == "none":
            return None
        M2 = mul(M, parse_transform(el.get("transform")))
        box = None
        if tag in ("svg", "g", "a", "switch", "symbol"):
            if tag == "svg" and el is not self.root:
                M2 = mul(M2, (1, 0, 0, 1, num(el.get("x")), num(el.get("y"))))
            for c in el:
                box = union(box, self.measure(c, M2, record))
        elif tag == "use":
            target = self.byid.get((el.get("href") or el.get(XLINK) or "#")[1:])
            if target is not None:
                box = self.measure(target, mul(M2, (1, 0, 0, 1, num(el.get("x")), num(el.get("y")))), False)
        elif tag == "text":
            box = self.measure_text(el, M2, record)
        else:
            b = shape_box(el)
            box = tbox(M2, b) if b else None
            if record and box:
                self.shapes.append({"el": el, "tag": tag, "box": box})
        if record:
            self.M[el], self.box[el] = M2, box
        return box

    def measure_text(self, el, M, record):
        keep = self.inherit(el, XMLSPACE) == "preserve"
        runs = [(el.text or "", el)]
        for ts in el:
            runs.append(("".join(ts.itertext()), ts))
            runs.append((ts.tail or "", el))
        if not keep:
            runs = [(re.sub(r"\s+", " ", t), n) for t, n in runs]
        runs = [(t, n) for t, n in runs if t]
        if not runs:
            return None
        if not keep:
            runs[0] = (runs[0][0].lstrip(), runs[0][1])
            runs[-1] = (runs[-1][0].rstrip(), runs[-1][1])
        x, y = num(el.get("x")) + num(el.get("dx")), num(el.get("y")) + num(el.get("dy"))
        chunks, biggest, lost = [], 0.0, set()
        for t, n in runs:
            own = n is not el
            fs = num(self.inherit(n, "font-size"), 16)
            if not chunks or (own and (n.get("x") is not None or n.get("y") is not None)):
                if own:
                    x, y = num(n.get("x"), x), num(n.get("y"), y)
                chunks.append([x, y, self.inherit(n, "text-anchor", "start"), 0.0, fs])
            if own and n.get("dy"):
                chunks[-1][1] += num(n.get("dy")) * (fs if "em" in n.get("dy") else 1)
                y = chunks[-1][1]
            w, miss = text_width(t, fs, self.face(n) or "s", length(self.inherit(n, "letter-spacing"), fs))
            chunks[-1][3] += w
            lost |= miss
            chunks[-1][3] += num(n.get("dx")) if own else 0
            chunks[-1][4] = max(chunks[-1][4], fs)
            biggest = max(biggest, fs)
        box = None
        base = self.inherit(el, "dominant-baseline", "")
        for cx, cy, anchor, w, fs in chunks:
            x0 = cx - {"middle": w / 2, "end": w}.get(anchor, 0)
            cy += 0.35 * fs if base in ("middle", "central") else 0.72 * fs if base == "hanging" else 0
            box = union(box, (x0, cy - 0.74 * fs, x0 + w, cy + 0.2 * fs))
        box = tbox(M, box)
        if record:
            s = "".join((" " if n is not el and any(n.get(k) is not None for k in ("x", "y", "dy")) else "") + t for t, n in runs).strip()
            self.texts.append({"el": el, "s": s, "box": box, "fs": biggest * mscale(M), "words": len(s.split()),
                               "lost": lost, "classed": self.face(el) is not None})
        return box

    def inside(self, el, ancestor):
        return ancestor is not None and any(a is ancestor for a in self.chain(el))

    def container(self, t, together=True):
        """The smallest box drawn before this text that holds its middle; with `together`, one that moves with it."""
        cx, cy = (t["box"][0] + t["box"][2]) / 2, (t["box"][1] + t["box"][3]) / 2
        mover, best = self.mover(t["el"]), None
        for s in self.shapes:
            b = s["box"]
            if s["tag"] not in ("rect", "path") or self.order[s["el"]] > self.order[t["el"]] or (together and self.mover(s["el"]) is not mover):
                continue
            if s["el"] is t["el"] or self.inside(s["el"], t["el"]):
                continue  # itself, or a part of it
            tb = t["box"]
            if "s" not in t and tb[0] <= b[0] + 0.5 and tb[1] <= b[1] + 0.5 and b[2] <= tb[2] + 0.5 and b[3] <= tb[3] + 0.5:
                continue  # a shape drawn over a smaller one does not sit in it (text may: a pill too small for it holds it all the same)
            if not (b[0] <= cx <= b[2] and b[1] <= cy <= b[3]) or area(b) > 0.6 * W * H:
                continue
            if b[3] - b[1] < 0.9 * (t["box"][3] - t["box"][1]):
                continue
            if self.inherit(s["el"], "fill", "#000") == "none" and self.inherit(s["el"], "stroke", "none") == "none":
                continue
            if s["tag"] == "path" and (self.inherit(s["el"], "fill", "#000") == "none" or not re.search(r"[zZ]\s*$", s["el"].get("d") or "")):
                continue  # a line or an open path is not a box
            if best is None or area(b) < area(best["box"]):
                best = s
        return best

    def held_in(self, t):
        """The box this text or shape sits in when the story is complete. What moves is drawn in its finished place (motion.md
        rule 3), so it is measured there too; what only passes through (opacity 0 at rest) or runs behind a clip is not held."""
        if any(a.get("opacity") is not None and num(a.get("opacity"), 1) == 0 or a.get("clip-path") for a in self.chain(t["el"])):
            return self.container(t)
        return self.container(t, together=False)

    # ---- the checks
    def run(self):
        {"hero": self.check_slots, "section": self.check_scene_slots}[self.kind]()
        self.check_text()
        self.check_contents()
        self.check_contrast()
        self.check_centring()
        self.check_strokes()
        self.check_motion()
        self.check_highlight_sync()
        self.check_sweeps()
        return self

    def slot(self, name, what):
        el = self.byid.get(name)
        if el is None:
            self.errors.append(f'no element with id="{name}": mark {what} with it, so the build can measure it')
        elif self.box.get(el) is None:
            self.errors.append(f'id="{name}" has nothing drawn in it')
            el = None
        return el

    def part(self, name, what):
        el = self.byid.get(name)
        if el is None:
            self.warns.append(f'no element with id="{name}": {what}')
        elif self.box.get(el) is None:
            self.warns.append(f'id="{name}" has nothing drawn in it')
            el = None
        return el

    def check_slots(self):
        for k in self.twice:
            self.errors.append(f"@keyframes {k} is written twice, differently: the last one replaces the first for every element that uses it. Give each its own name")
        logo = self.byid.get("logo")  # a repository without a mark has none
        if logo is not None and self.box.get(logo) is None:
            self.errors.append('id="logo" has nothing drawn in it')
            logo = None
        name = self.slot("name", "the repository name")
        tagline = self.slot("tagline", "the key phrase")
        stage = self.slot("stage", "the group that holds the picture of what the tool does")
        about = self.part("about", "under the key phrase goes a description of one or two lines that says what is worth knowing")
        facts = self.byid.get("facts")  # the highlights are optional
        if facts is not None and self.box.get(facts) is None:
            facts = None
        ticker = self.byid.get("ticker")  # the strip is optional too
        if ticker is not None and self.box.get(ticker) is None:
            ticker = None
        backdrop = self.byid.get("backdrop")  # optional, still or moving: the plan says which (kit.py backdrop)
        f = self.facts
        if name is not None:
            b = self.box[name]
            t = next((t for t in self.texts if t["el"] is name), None)
            size = t["fs"] if t else (b[3] - b[1]) / 0.72  # a wordmark drawn as shapes: from its height
            f["name_px"] = round(size)
            if not NAME_SIZE[0] <= size <= NAME_SIZE[1]:
                self.warns.append(f"the name is {size:.0f} px tall; keep it between {NAME_SIZE[0]} and {NAME_SIZE[1]}: it signs the poster, the key phrase leads")
            if b[2] - b[0] > 0.45 * W:
                self.warns.append(f"the name is {b[2] - b[0]:.0f} px wide, more than 45% of the canvas: make it smaller")
        if logo is not None:
            b = self.box[logo]
            side = min(b[2] - b[0], b[3] - b[1])
            f["logo_px"] = round(side)
            if not LOGO_SIZE[0] <= side <= LOGO_SIZE[1]:
                self.warns.append(f"the logo is {side:.0f} px on its shorter side; keep it between {LOGO_SIZE[0]} and {LOGO_SIZE[1]}")
            if name is not None:
                n = self.box[name]
                gap = max(n[0] - b[2], b[0] - n[2], n[1] - b[3], b[1] - n[3], 0)
                f["logo_to_name_px"] = round(gap)
                if gap > 64:
                    self.warns.append(f"the logo sits {gap:.0f} px from the name: put them together (within 64 px), they are read as one thing")
                if inter(b, n) and area(inter(b, n)) > 0.2 * area(n):
                    self.errors.append("the logo and the name overlap")
            if any("transform" in a["props"] and self.travel(a, logo)[0] > MIN_TRAVEL for a in self.anims(logo)):
                self.warns.append("the logo travels: it may move inside itself, but it stays where it is")
        if tagline is not None:
            lines = [t for t in self.texts if self.inside(t["el"], tagline)]
            words = sum(t["words"] for t in lines)
            f["tagline_words"] = words
            if lines:
                size = max(t["fs"] for t in lines)
                f["tagline_px"] = round(size)
                if not TAGLINE_SIZE[0] <= size <= TAGLINE_SIZE[1]:
                    self.warns.append(f"the tagline is {size:.0f} px; keep it between {TAGLINE_SIZE[0]} and {TAGLINE_SIZE[1]}: it is the key phrase, the first thing read")
                rivals = [x for x in self.texts if not self.inside(x["el"], tagline) and x["fs"] >= size]
                if rivals:
                    self.warns.append(f"{self.describe(rivals[0]['el'])} is {rivals[0]['fs']:.0f} px, as large as the tagline ({size:.0f} px): the tagline is the largest text on the canvas")
            if words > TAGLINE_WORDS:
                self.warns.append(f"the tagline has {words} words; say it in {TAGLINE_WORDS} or fewer, on one or two lines")
        if about is not None:
            lines = [t for t in self.texts if self.inside(t["el"], about)]
            words = sum(t["words"] for t in lines)
            f["about_words"] = words
            if lines:
                size = max(t["fs"] for t in lines)
                if not ABOUT_SIZE[0] <= size <= ABOUT_SIZE[1]:
                    self.warns.append(f"the description in #about is {size:.0f} px; keep it between {ABOUT_SIZE[0]} and {ABOUT_SIZE[1]}")
            if not ABOUT_WORDS[0] <= words <= ABOUT_WORDS[1]:
                self.warns.append(f"the description in #about has {words} words; write {ABOUT_WORDS[0]} to {ABOUT_WORDS[1]}, on one or two lines")
        if facts is not None:
            figures = [t for t in self.texts if self.inside(t["el"], facts) and t["fs"] >= FACT_SIZE]
            f["facts"] = len(figures)
            turns = [t for t in self.texts if self.inside(t["el"], facts) and (self.mover(t["el"]) is not None or self.fades(t["el"]))]
            if len(figures) > FACTS:
                self.warns.append(f"#facts shows {len(figures)} figures: keep the {FACTS} or fewer a person would repeat to a friend, or none")
            if not figures and not turns and sum(t["words"] for t in self.texts if self.inside(t["el"], facts)) > 24:
                self.warns.append("#facts is a block of still text: show features one at a time, taking turns in one place, or leave it out")
        for el, label in ((name, "name"), (tagline, "tagline"), (about, "description")):
            if el is not None and (self.mover(el) is not None or self.fades(el)):
                self.errors.append(f"the {label} is animated: it stays still, so it can be read at any moment")
        if ticker is not None and not any(self.inside(t["el"], ticker) and self.mover(t["el"]) is not None for t in self.texts):
            self.warns.append("no text travels in #ticker: it is a strip of text that never stops, behind a clip")
        self.check_stage(stage, (logo, name, tagline, about, facts), (logo, name, tagline, about, facts, ticker, backdrop))

    def check_stage(self, stage, copy_els, separate, share_min=STAGE_SHARE, copy_range=COPY_SHARE, parts_min=STAGE_PARTS, large=STAGE_LARGE):
        """The picture: how much of the canvas it takes, against the text block, and what it is made of."""
        f = self.facts
        if stage is None:
            return
        b = None  # what can be seen of the picture: each part cut by the canvas and by its clip or mask
        parts = [x for x in self.shapes + self.texts if self.inside(x["el"], stage)]
        parts += [{"el": e, "box": self.box[e]} for e in stage.iter() if local(e.tag) == "use" and self.box.get(e)]
        for x in parts:
            if area(x["box"]) < 0.9 * W * H:
                b = union(b, inter(x["box"], self.region(x["el"])))
        share = area(b) / (W * H) if b else 0
        f["stage_share"] = round(share, 2)
        what = "repository" if self.kind == "hero" else "section"
        if share < share_min:
            self.warns.append(f"the picture in #stage covers {share:.0%} of the canvas; give it at least {share_min:.0%}, it is what explains the {what}")
        for el in separate:
            if el is not None and self.inside(el, stage):
                self.errors.append(f'id="{el.get("id")}" is inside #stage: the text, the picture, the strip and the background are separate groups')
        copy = None
        for el in copy_els:
            copy = union(copy, self.box.get(el) if el is not None else None)
        if copy and b:
            ratio = area(copy) / (area(copy) + area(b))
            f["copy_share"] = round(ratio, 2)
            if not copy_range[0] <= ratio <= copy_range[1]:
                much = "the text block is too small beside the picture and gets lost" if ratio < copy_range[0] else "the text block crowds out the picture"
                usual = "heroes sit between 35 / 65 and 45 / 55" if self.kind == "hero" else "scenes sit between 15 / 85 and 35 / 65"
                self.warns.append(f"text and picture are {ratio:.0%} / {1 - ratio:.0%}: {much}. Most {usual}; keep this one only when the picture needs it")
            hit = sum(area(inter(copy, x["box"]) or (0, 0, 0, 0)) for x in parts if area(x["box"]) < 0.9 * W * H)
            if hit > 0.05 * area(copy):
                self.warns.append("the picture in #stage runs under the text block: give each its own side of the canvas")
        sides = [min(x["box"][2] - x["box"][0], x["box"][3] - x["box"][1]) for x in parts if "s" not in x]
        small = sum(1 for s in sides if s <= STAGE_SMALL[0])
        moving = sum(1 for e in stage.iter() if self.anims(e))
        f["stage_parts"], f["stage_moving"] = len(parts), moving
        if len(parts) < parts_min:
            self.warns.append(f"the picture in #stage is made of {len(parts)} parts: it reads as empty. Draw the real thing with its detail ({parts_min} parts or more): rows, chips, counters, sample content")
        if not any(s >= large for s in sides):
            self.warns.append(f"nothing in #stage is large: one object {large} px or more on its shorter side anchors the picture")
        if small < STAGE_SMALL[1]:
            self.warns.append(f"#stage has {small} small detail(s): mix sizes, a large object with medium ones and {STAGE_SMALL[1]} or more small ones ({STAGE_SMALL[0]} px or less)")
        if moving < STAGE_MOVING:
            self.warns.append(f"{moving} thing(s) move in #stage: a picture that is alive has {STAGE_MOVING} or more, one leading and the others following or ambient")
        self.check_icons(stage)

    def check_cursor(self, stage):
        """A cursor that reaches something clickable becomes a pointer there: the scene holds a pointer as well as the arrow."""
        kinds = {e.get("data-cursor") for e in stage.iter() if e.get("data-kit") == "cursor"}
        clickable = [e for e in stage.iter() if e.get("data-clickable") == "true"]
        if "arrow" in kinds and clickable and "pointer" not in kinds:
            self.warns.append(f"the cursor stays an arrow, and the scene has {len(clickable)} clickable part(s): over a button, a link or an option it "
                              "turns into a pointer. Use `kit.py cursor-swap` with the moments it hovers")

    def check_icons(self, stage):
        """Small pictograms: each says what it means (data-icon), is drawn large and thick enough, and the judges read it cold."""
        self.check_cursor(stage)
        declared = [e for e in stage.iter() if e.get("data-icon") is not None]
        self.facts["icons"] = len(declared)
        for e in declared:
            b = self.box.get(e)
            if b is None:
                continue
            means = e.get("data-icon").strip()
            if not means:
                self.warns.append(f"an icon has an empty data-icon: write what it means here, in a few words (\"cut\", \"read again\")")
            k = mscale(self.M.get(self.parent.get(e), IDENT)) if self.parent.get(e) is not None else 1  # the groups around it, not its own scale
            # a set icon says its drawn size (data-size, scaled by any group around it); a home-made one is measured
            size = num(e.get("data-size")) * k if e.get("data-size") else max(b[2] - b[0], b[3] - b[1])
            if size < ICON_MIN:
                self.warns.append(f"the icon \"{means}\" is {size:.0f} px; draw it at {ICON_MIN} px or more (its grid, for a set icon), or it is "
                                  f"{size * README:.0f} px at README width and blurs into something else")
            widths = [num(self.inherit(s, "stroke-width"), 1) * mscale(self.M.get(s, IDENT)) for s in e.iter()
                      if s in self.M and local(s.tag) in ("path", "circle", "ellipse", "line", "polyline", "rect")
                      and self.inherit(s, "stroke", "none") not in ("none", "transparent")]
            if widths and min(widths) < ICON_STROKE - 0.05:
                self.warns.append(f"the icon \"{means}\" has strokes of {min(widths):.1f} px; use {ICON_STROKE} or more, thinner lines vanish at README width")
        # thin strokes that are not frames or connectors, and not inside a declared icon: curves, short lines and rings drawn without fill
        strokes = []
        for s in self.shapes:
            if not self.inside(s["el"], stage) or s["tag"] not in ("path", "circle", "ellipse", "polyline", "line"):
                continue
            if any(self.inside(s["el"], e) for e in declared):
                continue
            if self.inherit(s["el"], "fill", "#000") != "none" or self.inherit(s["el"], "stroke", "none") in ("none", "transparent"):
                continue
            w, h = s["box"][2] - s["box"][0], s["box"][3] - s["box"][1]
            if max(w, h) > ICON_MAX and min(w, h) <= 4:  # a straight connector or rule passes by, it is not part of a drawing
                continue
            strokes.append(s)
        # strokes that touch and are seen at the same time belong to one drawing; cards that take turns in one place do not add up
        def layer(el):
            return next((a for a in self.chain(el) if any("opacity" in x["props"] for x in self.anims(a))), None)
        groups = []
        for s in strokes:
            near = [g for g in groups if layer(g[0]["el"]) is layer(s["el"])
                    and any(inter(o["box"], (s["box"][0] - 4, s["box"][1] - 4, s["box"][2] + 4, s["box"][3] + 4)) for o in g)]
            merged = [s] + [x for g in near for x in g]
            groups = [g for g in groups if g not in near] + [merged]
        for g in groups:
            b = None
            for s in g:
                b = union(b, s["box"])
            if len(g) < 2 or max(b[2] - b[0], b[3] - b[1]) > ICON_MAX:
                continue
            self.warns.append(f"{self.describe(g[0]['el'])} and {len(g) - 1} more thin stroke(s) draw a small icon ({b[2] - b[0]:.0f}×{b[3] - b[1]:.0f} px "
                              f"at {b[0]:.0f}, {b[1]:.0f}) that does not say what it means. Wrap it in <g data-icon=\"what it means\">, or take a known one "
                              f"with `assets.py search <repo> icons <words>`: the judges read every icon cold, at the size a reader sees it")

    def check_scene_slots(self):
        """A section scene: eyebrow, title and sub are the text block, the stage shows what the section says."""
        for k in self.twice:
            self.errors.append(f"@keyframes {k} is written twice, differently: the last one replaces the first for every element that uses it. Give each its own name")
        title = self.slot("title", "the headline of the scene: what this section claims, in a few words")
        stage = self.slot("stage", "the group that holds the picture of what this section explains")
        eyebrow, sub = self.byid.get("eyebrow"), self.byid.get("sub")
        eyebrow = eyebrow if eyebrow is not None and self.box.get(eyebrow) else None
        sub = sub if sub is not None and self.box.get(sub) else None
        backdrop = self.byid.get("backdrop")  # optional, still or moving: the plan says which (kit.py backdrop)
        for bad in ("name", "tagline", "about", "facts", "ticker", "logo"):
            if self.byid.get(bad) is not None:
                self.warns.append(f'id="{bad}" belongs to the hero: a scene has #eyebrow, #title, #sub and #stage, and does not sign itself again')
        f = self.facts
        if title is not None:
            lines = [t for t in self.texts if self.inside(t["el"], title)]
            words = sum(t["words"] for t in lines)
            f["title_words"] = words
            if lines:
                size = max(t["fs"] for t in lines)
                f["title_px"] = round(size)
                if not TITLE_SIZE[0] <= size <= TITLE_SIZE[1]:
                    self.warns.append(f"the title is {size:.0f} px; keep it between {TITLE_SIZE[0]} and {TITLE_SIZE[1]}: it is what the section claims, read first")
                rivals = [x for x in self.texts if not self.inside(x["el"], title) and x["fs"] >= size]
                if rivals:
                    self.warns.append(f"{self.describe(rivals[0]['el'])} is {rivals[0]['fs']:.0f} px, as large as the title ({size:.0f} px): the title is the largest text on the scene")
            if words > TITLE_WORDS:
                self.warns.append(f"the title has {words} words; say it in {TITLE_WORDS} or fewer")
        if sub is not None:
            lines = [t for t in self.texts if self.inside(t["el"], sub)]
            words = sum(t["words"] for t in lines)
            f["sub_words"] = words
            if lines and not SUB_SIZE[0] <= max(t["fs"] for t in lines) <= SUB_SIZE[1]:
                self.warns.append(f"#sub is {max(t['fs'] for t in lines):.0f} px; keep it between {SUB_SIZE[0]} and {SUB_SIZE[1]}")
            if not SUB_WORDS[0] <= words <= SUB_WORDS[1]:
                self.warns.append(f"#sub has {words} words; write {SUB_WORDS[0]} to {SUB_WORDS[1]}, one line")
        if eyebrow is not None:
            lines = [t for t in self.texts if self.inside(t["el"], eyebrow)]
            if lines and not EYEBROW_SIZE[0] <= max(t["fs"] for t in lines) <= EYEBROW_SIZE[1]:
                self.warns.append(f"#eyebrow is {max(t['fs'] for t in lines):.0f} px; keep it between {EYEBROW_SIZE[0]} and {EYEBROW_SIZE[1]}")
            if sum(t["words"] for t in lines) > 4:
                self.warns.append("#eyebrow is a label of one to four words: the name of the section")
        for el, label in ((eyebrow, "eyebrow"), (title, "title"), (sub, "sub")):
            if el is not None and (self.mover(el) is not None or self.fades(el)):
                self.errors.append(f"the {label} is animated: it stays still, so it can be read at any moment")
        self.check_stage(stage, (eyebrow, title, sub), (eyebrow, title, sub, backdrop), SCENE_STAGE_SHARE, SCENE_COPY_SHARE, SCENE_PARTS, SCENE_LARGE)

    def check_contents(self):
        """Shapes and icons inside a box keep inside it, with room: a spill or a near miss reads as a mistake."""
        icons = [e for e in self.root.iter() if e.get("data-icon") is not None and self.box.get(e)]
        items = [{"el": e, "box": self.box[e]} for e in icons]
        for sh in self.shapes:
            el = sh["el"]
            if sh["tag"] not in ("rect", "circle", "ellipse", "path", "polygon") or any(self.inside(el, e) for e in icons):
                continue
            if self.inherit(el, "fill", "#000") in ("none", "transparent"):
                continue  # a frame, a ring or a connector: lines may meet the edge they point at
            if sh["tag"] == "path" and not re.search(r"[zZ]\s*$", el.get("d") or ""):
                continue
            if any(self.inside(el, self.byid.get(i)) for i in ("backdrop", "ticker")):
                continue
            items.append({"el": el, "box": sh["box"]})
        for it in items:
            if any(a.get("data-cursor") for a in self.chain(it["el"])):
                continue  # a cursor points at a box from above it; it is not held in it
            c = self.held_in(it)
            if c is None:
                continue
            b, cb = it["box"], c["box"]
            kit = next((a for a in self.chain(it["el"]) if a.get("data-kit")), None)
            if kit is not None and self.inside(c["el"], kit):
                continue  # a kit part is drawn to its own measure (a bar's fill, a switch's knob)
            gaps = (b[0] - cb[0], b[1] - cb[1], cb[2] - b[2], cb[3] - b[3])
            hit = inter(b, cb)
            inside = area(hit) / max(area(b), 1e-9) if hit else 0
            what = (it["el"].get("data-icon") and f'the icon "{it["el"].get("data-icon")}"' or self.describe(it["el"])) + f" at {b[0]:.0f},{b[1]:.0f}"
            if min(gaps) < -1:
                if inside >= 0.6:  # mostly in: it spills; a badge set across a corner on purpose is less than that inside
                    self.errors.append(f"{what} runs {-min(gaps):.0f} px out of the box it sits in: move it in, shrink it or grow the box")
                continue
            # flush (a fill, a header) is a choice; almost touching is not. A small box (a mark, a key) keeps a share of its size instead
            need = min(BOX_PAD, SMALL_BOX_PAD * min(cb[2] - cb[0], cb[3] - cb[1]))
            near = [g for g in gaps if 0.5 < g < need - 0.5]
            if near:
                self.errors.append(f"{what} is {min(near):.0f} px from the edge of the box it sits in; keep {need:.0f} px or more, or set it flush against the edge")

    def check_text(self):
        f, canvas = self.facts, (0, 0, W, H)
        apart = [self.byid.get(i) for i in ("name", "tagline", "about", "facts", "eyebrow", "title", "sub")]
        still = [t for t in self.texts if self.mover(t["el"]) is None]
        for t in self.texts:
            if not t["classed"]:
                self.warns.append(f"{self.describe(t['el'])} has no class s, b or m: it falls back to a system font and looks different on every machine")
            if t["lost"]:
                self.errors.append(f"{self.describe(t['el'])} uses {' '.join(sorted(t['lost']))}, which the fonts do not have: each machine draws it in another font and at another width, and outlines drop it. Draw it as a shape (an icon from the chosen family) beside the text, or use another character")
        small = sorted({round(t["fs"], 1) for t in self.texts if t["fs"] < MIN_TEXT})
        if small:
            self.warns.append(f"font-size below {MIN_TEXT} ({small}): unreadable at README width, where the hero is shown at ~65%")
        counted = [t for t in self.texts if not any(self.inside(t["el"], self.byid.get(i)) for i in ("facts", "ticker"))]
        tiny = [t for t in counted if t["fs"] < LABEL_TEXT]  # the labels of the figures and the strip are small by design
        if len(counted) >= 5 and len(tiny) > SMALL_SHARE * len(counted):
            self.warns.append(f"{len(tiny)} of {len(counted)} lines of text are under {LABEL_TEXT} px, which is {LABEL_TEXT * README:.0f} px in a README: say less and say it larger. Labels that name a step are 16 px or more; only texture goes smaller")
        sizes = sorted({round(t["fs"]) for t in self.texts})
        f["text_sizes"] = sizes
        if len(sizes) > SIZES:
            self.warns.append(f"{len(sizes)} different font sizes ({sizes}): use {SIZES} or fewer, each for one role")
        # text against the canvas
        for t in still:
            b = t["box"]
            out = max(-b[0], -b[1], b[2] - W, b[3] - H)
            if out > 1:
                self.errors.append(f"{self.describe(t['el'])} runs {out:.0f} px off the canvas")
            elif out > -EDGE:
                self.warns.append(f"{self.describe(t['el'])} is {-out:.0f} px from the canvas edge; leave {EDGE}")
        # text against the box it sits in
        for t in self.texts:
            c = self.held_in(t)
            if c is None:
                continue
            b, cb = t["box"], c["box"]
            fs = t["fs"]
            side = min(b[0] - cb[0], cb[2] - b[2])
            over = max(cb[0] - b[0], b[2] - cb[2], cb[1] - b[1], b[3] - cb[3])
            pill = cb[3] - cb[1] < PILL_HIGH * fs
            need = max(BOX_PAD, PILL_PAD * fs) if pill else max(BOX_PAD, PANEL_PAD * fs)
            need_y = 0 if pill else max(BOX_PAD, PANEL_PAD_Y * fs)
            if over > 1:
                self.errors.append(f"{self.describe(t['el'])} runs {over:.0f} px out of its box ({cb[2] - cb[0]:.0f} px wide, the text needs {b[2] - b[0]:.0f}): shorten it, shrink it, break it into lines or widen the box")
            elif side < need - 0.5:
                self.errors.append(f"{self.describe(t['el'])} is {max(side, 0):.0f} px from the side of its box; a {'pill' if pill else 'panel'} keeps {need:.0f} px on both sides of {fs:.0f} px text. Widen the box, break the line or shorten it (kit.py card and note wrap and size themselves)")
            elif min(b[1] - cb[1], cb[3] - b[3]) < need_y - 0.5:
                self.errors.append(f"{self.describe(t['el'])} is {max(min(b[1] - cb[1], cb[3] - b[3]), 0):.0f} px from the top or bottom of its panel; keep {need_y:.0f}")
        # text against text
        for i, a in enumerate(self.texts):
            for b in self.texts[i + 1:]:
                if self.mover(a["el"]) is not self.mover(b["el"]) or self.fades(a["el"]) or self.fades(b["el"]):
                    continue
                hit = inter(a["box"], b["box"])
                if hit and area(hit) > 0.08 * min(area(a["box"]), area(b["box"])):
                    msg = f"{self.describe(a['el'])} and {self.describe(b['el'])} overlap"
                    (self.errors if area(hit) > 0.25 * min(area(a["box"]), area(b["box"])) else self.warns).append(msg)
        # how much there is to read
        extra = [t for t in still if not any(self.inside(t["el"], a) for a in apart)]
        words = sum(t["words"] for t in extra)
        f["still_words"] = words
        if words > STILL_WORDS:
            self.warns.append(f"{words} words stand still in the picture; keep it to {STILL_WORDS}, shapes and motion tell the story")
        for t in extra:
            if t["words"] > LABEL_WORDS:
                self.warns.append(f"{self.describe(t['el'])} is a sentence of {t['words']} words: a label names a thing in {LABEL_WORDS} words or fewer")

    def backdrop(self, box, theme, depth=0):
        """The colour a reader sees inside this box: its fill, made translucent by fill-opacity and opacity, over what lies behind it."""
        if box is None or depth > 8:
            return self.color("$bg", theme)
        under = self.backdrop(self.container(box, together=False), theme, depth + 1)
        own = self.color(self.inherit(box["el"], "fill"), theme)
        if not own:
            return under
        alpha = num(self.inherit(box["el"], "fill-opacity"), 1)
        for a in self.chain(box["el"]):
            if not any("opacity" in x["props"] for x in self.anims(a)):
                alpha *= num(a.get("opacity"), 1)
        return mix(own, under, alpha) if alpha < 1 and under else own

    def check_contrast(self):
        seen = set()
        for t in self.texts:
            fill = self.inherit(t["el"], "fill", "#000000")
            c = self.container(t, together=False)  # a button that dips is still what its label is read on
            mid = (t["box"][0] + t["box"][2]) / 2
            if c is None and not 0 <= mid <= W:
                continue  # a copy of running text that waits outside the canvas: its twin in view is measured
            behind = self.inherit(c["el"], "fill") if c else "$bg"
            opacity = 1.0  # as it is when shown: an animated opacity replaces the attribute, so that one is skipped
            for a in self.chain(t["el"]):
                if not any("opacity" in x["props"] for x in self.anims(a)):
                    opacity *= num(a.get("opacity"), 1)
            opacity *= num(t["el"].get("fill-opacity"), 1)
            need = 3 if t["fs"] * README >= 24 or (t["fs"] * README >= 18.5 and self.face(t["el"]) == "b") else 4.5
            for ti, theme in enumerate(("dark", "light")):
                fg, bg = self.color(fill, ti), self.backdrop(c, ti)
                if not fg or not bg or (fill, behind, theme) in seen:
                    continue
                if opacity < 1:
                    fg = mix(fg, bg, opacity)
                ratio = contrast(fg, bg)
                if ratio < need:
                    seen.add((fill, behind, theme))
                    self.warns.append(f"{theme}: {self.describe(t['el'])} in {fill} on {behind} has contrast {ratio:.1f}, below {need}")
        self.check_icon_contrast()

    def check_icon_contrast(self):
        """An icon is read by its strongest ink: it needs ICON_CONTRAST against what it sits on, in both themes."""
        for e in self.root.iter():
            if e.get("data-icon") is None or self.box.get(e) is None:
                continue
            who = f'the icon "{e.get("data-icon").strip()}"'
            c = self.container({"el": e, "box": self.box[e]}, together=False)
            behind = self.inherit(c["el"], "fill") if c else "$bg"  # its name, for the message
            inks, loose = [], False
            for s in e.iter():
                if s not in self.M or local(s.tag) not in ("path", "circle", "ellipse", "line", "polyline", "polygon", "rect"):
                    continue
                opacity = 1.0
                for a in self.chain(s):
                    if not any("opacity" in x["props"] for x in self.anims(a)):
                        opacity *= num(a.get("opacity"), 1)
                for attr in ("fill", "stroke"):
                    v = (self.inherit(s, attr, "#000000" if attr == "fill" else "none") or "").strip()
                    if v in ("none", "transparent") or v.startswith("url"):
                        continue
                    if v == "currentColor":
                        loose = True
                        v = self.inherit(s, "color", "#000000")  # with no color= above it, currentColor is black
                    inks.append((v, opacity * num(self.inherit(s, f"{attr}-opacity"), 1)))
            if loose:
                self.warns.append(f"{who} is painted in currentColor: some viewers ignore color= and draw it black. Write the $role in its fill= and stroke=")
            for ti, theme in enumerate(("dark", "light")):
                bg = self.backdrop(c, ti)
                scored = [(contrast(mix(fg, bg, o) if o < 1 else fg, bg), v) for v, o in inks if bg and (fg := self.color(v, ti))]
                if scored and max(scored)[0] < ICON_CONTRAST:
                    ratio, v = max(scored)
                    self.warns.append(f"{theme}: {who} in {v} on {behind} has contrast {ratio:.1f}, below {ICON_CONTRAST}: it is lost against what it sits on")

    # ---- what the picture looks like at a moment of the loop (keyframes joined in straight lines, easing ignored)
    def at(self, a, prop, base, T):
        if a["dur"] <= 0 or not a["stops"]:
            return None
        k, frac = divmod(T - a["delay"], a["dur"])
        p = frac / a["dur"] * 100
        if a["direction"] == "reverse" or (a["direction"] in ("alternate", "alternate-reverse") and (int(k) % 2 == 1) != (a["direction"] == "alternate-reverse")):
            p = 100 - p
        pts = self.timeline(a, prop, base)
        if not pts:
            return None
        held = a["timing"].startswith("steps") or a["timing"] in ("step-start", "step-end")
        for (p0, v0), (p1, v1) in zip(pts, pts[1:]):
            if p0 <= p <= p1:
                if prop == "opacity":
                    v0, v1 = num(v0, 1), num(v1, 1)
                    return v0 if held or p1 == p0 else v0 + (v1 - v0) * (p - p0) / (p1 - p0)
                t0, t1 = transform_parts(v0), transform_parts(v1)
                if t0 is None or t1 is None:
                    return None
                f = 0 if held or p1 == p0 else (p - p0) / (p1 - p0)
                return (t0[0] + (t1[0] - t0[0]) * f, t0[1] + (t1[1] - t0[1]) * f)
        return None

    def opacity_at(self, el, T, stop=None):
        """Opacity at T, from el up to (not including) the ancestors it shares with `stop`."""
        shared = set(self.chain(stop)) if stop is not None else set()
        o = 1.0
        for a in self.chain(el):
            if a in shared:
                break
            fading = [x for x in self.anims(a) if "opacity" in x["props"]]
            v = self.at(fading[0], "opacity", a.get("opacity") or "1", T) if fading else None
            o *= num(a.get("opacity"), 1) if v is None else v
        return o

    def shift_at(self, el, T, stop=None):
        shared = set(self.chain(stop)) if stop is not None else set()
        dx = dy = 0.0
        for a in self.chain(el):
            if a in shared:
                break
            for x in self.anims(a):
                if "transform" in x["props"]:
                    v = self.at(x, "transform", "none", T)
                    if v:
                        k = mscale(self.M.get(self.parent.get(a), IDENT)) if self.parent.get(a) is not None else 1
                        dx, dy = dx + v[0] * k, dy + v[1] * k
        return dx, dy

    def check_highlight_sync(self):
        """A box that steps from label to label lights each one: the label shows lit while the box is on it, and only then."""
        fading = [t for t in self.texts if self.fades(t["el"])]
        if not fading:
            return
        N = 240
        for s in self.shapes:
            el = s["el"]
            if s["tag"] not in ("rect", "path") or self.mover(el) is None:
                continue
            durs = [x["dur"] for a in self.chain(el) for x in self.anims(a) if x["dur"] > 0]
            if not durs:
                continue
            P = max(durs)
            ts = [P * i / N for i in range(N)]
            b = s["box"]
            visits = []
            for t in fading:
                if self.inside(t["el"], el) or self.inside(el, t["el"]):
                    continue
                th = t["box"][3] - t["box"][1]
                if b[3] - b[1] < 0.9 * th:
                    continue
                # what the two share (a group that slides or fades them together) moves both alike: only the rest counts
                rel = [(bx - tx, by - ty) for (bx, by), (tx, ty) in zip((self.shift_at(el, T, t["el"]) for T in ts), (self.shift_at(t["el"], T, el) for T in ts))]
                if max(math.hypot(x0 - x1, y0 - y1) for x0, y0 in rel[::8] for x1, y1 in rel[::8]) < th:
                    continue  # the box does not travel from label to label
                cx, cy = (t["box"][0] + t["box"][2]) / 2, (t["box"][1] + t["box"][3]) / 2
                over = [self.opacity_at(el, T, t["el"]) > 0.5 and b[0] + dx <= cx <= b[2] + dx and b[1] + dy <= cy <= b[3] + dy
                        for (dx, dy), T in zip(rel, ts)]
                if sum(over) * P / N >= 0.5 and not all(over):
                    visits.append((t, over))
            if len(visits) < 2:
                continue  # it passes by; a highlight rests on two labels or more
            for t, over in visits:
                o = [self.opacity_at(t["el"], T, el) for T in ts]
                hi, lo = max(o), min(o)
                if hi - lo < 0.2:
                    continue
                lit = [v >= lo + 0.75 * (hi - lo) for v in o]
                if sum(l and v for l, v in zip(lit, over)) < 0.5 * sum(over):
                    continue  # it lights to its own rhythm, not with this box: the two are not one highlight
                run = longest = 0
                for i in range(2 * N):  # twice round, so a run across the loop's end counts whole
                    run = run + 1 if lit[i % N] != over[i % N] else 0
                    longest = max(longest, min(run, N))
                late = longest * P / N
                if late > SYNC_SLACK:
                    self.warns.append(f"{self.describe(t['el'])} is lit {late:.1f} s out of step with the box {self.describe(el)} that highlights it: "
                                      "give the label and the box the same duration and the same keyframe percentages, so it lights when the box arrives and dims when it leaves")

    def check_sweeps(self):
        """A marker that runs along a line of text, reading it, stops where the text ends."""
        N = 120
        for s in self.shapes:
            el = s["el"]
            if s["tag"] not in ("rect", "path", "circle", "ellipse") or self.mover(el) is None:
                continue
            if any(a.get("data-kit") == "cursor" for a in self.chain(el)):
                continue
            durs = [x["dur"] for a in self.chain(el) for x in self.anims(a) if x["dur"] > 0]
            if not durs:
                continue
            P, b = max(durs), s["box"]
            for t in self.texts:
                tb, th = t["box"], t["box"][3] - t["box"][1]
                if self.inside(t["el"], el) or b[3] - b[1] > 1.6 * th:
                    continue  # a box that holds the line, not a marker on it
                ts = [P * i / N for i in range(N)]
                seen = [(T, self.shift_at(el, T, t["el"])) for T in ts if self.opacity_at(el, T, t["el"]) > 0.3]
                on = [(b[0] + dx, b[2] + dx) for _, (dx, dy) in seen
                      if min(b[3] + dy, tb[3]) - max(b[1] + dy, tb[1]) >= 0.5 * min(b[3] - b[1], th)]
                if not on:
                    continue
                left, right = min(x0 for x0, _ in on), max(x1 for _, x1 in on)
                w = tb[2] - tb[0]
                if b[2] - b[0] > 0.5 * w or right - left < 0.5 * w or not tb[0] - 0.25 * w <= left <= tb[0] + 0.25 * w:
                    continue  # not a small marker that runs along this line from its start
                c = self.container(t, together=False)
                if self.inherit(el, "fill") == (self.inherit(c["el"], "fill") if c else "$bg"):
                    continue  # a cover in the colour behind the text, that reveals it as it is typed
                row = [o["box"][2] for o in self.texts if o["box"][0] <= right and o["box"][2] >= tb[0]
                       and min(o["box"][3], tb[3]) - max(o["box"][1], tb[1]) >= 0.5 * th]
                end = max(row + [tb[2]])
                if right > end + max(16.0, 0.1 * w):
                    self.warns.append(f"{self.describe(el)} runs along {self.describe(t['el'])} to x={right:.0f}, {right - end:.0f} px past where the text ends "
                                      f"(x={end:.0f}): stop it at the end of the text, the reader follows it as it reads")
                    break

    def check_centring(self):
        """A one-line label in a box about its own height (a chip, a button, a highlight) sits in the middle of it, top to bottom."""
        for t in self.texts:
            fs, tb = t["fs"], t["box"]
            if tb[3] - tb[1] > 1.3 * fs:
                continue  # more than one line: a card, not a label
            c = self.container(t, together=False)
            if c is None or c["tag"] != "rect":
                continue
            b = c["box"]
            h = b[3] - b[1]
            if not 1.2 * fs <= h <= 2.8 * fs:
                continue
            ink = tb[3] - 0.55 * fs  # the middle of the capitals: baseline minus 0.35 em
            off = ink - (b[1] + b[3]) / 2
            if abs(off) > max(2.0, 0.1 * h):
                self.warns.append(f"{self.describe(t['el'])} sits {abs(off):.0f} px {'low' if off > 0 else 'high'} in its {h:.0f} px box: put its baseline "
                                  f"at the box's middle + 0.35 × font-size ({(b[1] + b[3]) / 2 + 0.35 * fs:.1f})")

    def check_strokes(self):
        thin = 0
        for s in self.shapes:
            if self.inherit(s["el"], "stroke", "none") in ("none", "transparent"):
                continue
            if num(self.inherit(s["el"], "stroke-width"), 1) * mscale(self.M[s["el"]]) < 1:
                thin += 1
        if thin:
            self.warns.append(f"{thin} stroke(s) thinner than 1 px: they fade out at README width, use 1.5 or more")

    def timeline(self, a, prop, base):
        pts = [(p, d[prop]) for p, d in a["stops"] if prop in d]
        if pts and pts[0][0] > 0:
            pts.insert(0, (0.0, base))
        if pts and pts[-1][0] < 100:
            pts.append((100.0, base))
        return pts

    def travel(self, a, el):
        """Farthest distance between two keyframes of this animation, in canvas pixels, and the parsed stops."""
        k = mscale(self.M.get(self.parent.get(el), IDENT)) if self.parent.get(el) is not None else 1
        pts = [(p, transform_parts(v)) for p, v in self.timeline(a, "transform", "none")]
        if any(t is None for _, t in pts):
            return 0.0, None
        far = max([math.hypot(a_[0] - b_[0], a_[1] - b_[1]) for _, a_ in pts for _, b_ in pts] or [0.0])
        return far * k, pts

    def region(self, el):
        """The part of the canvas where this element can be seen: the canvas cut by clips and masks above it."""
        r = (0, 0, W, H)
        for a in self.chain(el):
            for attr in ("clip-path", "mask"):
                m = re.search(r"url\(#([^)]+)\)", a.get(attr) or self.style(a).get(attr, ""))
                target = self.byid.get(m.group(1)) if m else None
                if target is not None:
                    b = None
                    for c in target:
                        b = union(b, self.measure(c, self.M.get(a, IDENT), False))
                    if b:
                        r = inter(r, b) or (0, 0, 0, 0)
        return r

    def units(self, el, M):
        """The boxes of the things el is made of, looking through a lone <g> or <use> to what it wraps."""
        kids = [c for c in el if local(c.tag) not in SKIP]
        if len(kids) == 1:
            c, tag = kids[0], local(kids[0].tag)
            M2 = mul(M, parse_transform(c.get("transform")))
            if tag == "use":
                target = self.byid.get((c.get("href") or c.get(XLINK) or "#")[1:])
                if target is not None:
                    return self.units(target, mul(mul(M2, (1, 0, 0, 1, num(c.get("x")), num(c.get("y")))), parse_transform(target.get("transform"))))
            elif tag in ("g", "symbol"):
                return self.units(c, M2)
        return [b for b in (self.measure(c, M, False) for c in kids) if b]

    def repeats(self, el, dx, dy):
        """True when the content of el looks the same after moving by (dx, dy)."""
        m = re.search(r"url\(#([^)]+)\)", (el.get("fill") or "") + (el.get("stroke") or ""))
        pattern = self.byid.get(m.group(1)) if m else None
        if pattern is not None and local(pattern.tag) == "pattern":
            pw, ph = num(pattern.get("width")), num(pattern.get("height"))
            near = lambda v, p: p > 0 and min(abs(v) % p, p - abs(v) % p) < 0.6 or (p == 0 and abs(v) < 0.6)
            return near(dx, pw) and near(dy, ph)
        kids = self.units(el, self.M.get(el, IDENT))
        if len(kids) < 2:
            return False
        for div in (1, 2, 3, 4):
            ox, oy = dx / div, dy / div
            twins = 0
            for b in kids:
                for sign in (1, -1):
                    want = shift(b, sign * ox, sign * oy)
                    if any(o is not b and all(abs(o[i] - want[i]) < 1.5 for i in range(4)) for o in kids):
                        twins += 1
                        break
            if twins >= 0.8 * len(kids):
                return True
        return False

    def check_motion(self):
        f, E, Wn = self.facts, self.errors, self.warns
        stage = self.byid.get("stage")
        animated = [(el, a) for el in self.root.iter() for a in self.anims(el)]
        names = {a["name"] for _, a in animated}
        f["animations"], f["animated_elements"] = len(names), len({el for el, _ in animated})
        if len(names) < 3:
            Wn.append(f"only {len(names)} distinct animations: the picture should be alive, with one thing leading and the rest quiet")
        if list(self.root.iter(f"{{{SVG}}}animate")) + list(self.root.iter(f"{{{SVG}}}animateTransform")) + list(self.root.iter(f"{{{SVG}}}animateMotion")):
            Wn.append("SMIL animation (<animate>, <animateTransform>, <animateMotion>) keeps running for people who asked for reduced motion: use CSS keyframes")
        lead, speeds, staged, done, biggest = False, [], {}, set(), 0.0
        for el, a in animated:
            who = f"{self.describe(el)} ({a['name']})"
            if a["stops"] is None:
                E.append(f"{who}: there is no @keyframes {a['name']}")
                continue
            dur, alt, props = a["dur"], "alternate" in a["direction"], a["props"]
            first = a["name"] not in done  # report what belongs to the keyframes once, not once per element
            done.add(a["name"])
            if dur <= 0:
                E.append(f"{who} has no duration")
                continue
            if first and not DURATION[0] <= dur <= DURATION[1]:
                Wn.append(f"{who} lasts {dur:g} s; keep loops between {DURATION[0]} and {DURATION[1]} s")
            bad = props - CHEAP - PAINTED
            if first and bad & {"width", "height", "x", "y", "cx", "cy", "r", "rx", "ry", "d", "font-size", "left", "top", "points"}:
                E.append(f"@keyframes {a['name']} animates {', '.join(sorted(bad))}: geometry does not animate in every browser. Move or scale it with transform")
            elif first and bad:
                Wn.append(f"@keyframes {a['name']} animates {', '.join(sorted(bad))}, which is repainted every frame: cross-fade two layers with opacity, or move it with transform")
            if "transform" in props and el.get("transform"):
                E.append(f"{who} has its own transform attribute, which the animation replaces: it will jump to the corner. Put the attribute on a parent <g>")
            if self.inherit(el, "filter") and el.get("filter"):
                Wn.append(f"{who} is animated and filtered: the filter is recomputed every frame. Animate a plain shape, or put the filter on something still")

            far, pts = self.travel(a, el)
            scale_k = mscale(self.M.get(self.parent.get(el), IDENT)) if self.parent.get(el) is not None else 1
            ops = [(p, num(v, 1)) for p, v in self.timeline(a, "opacity", el.get("opacity") or "1")]
            o_range = (max(o for _, o in ops) - min(o for _, o in ops)) if ops else 0
            hidden_ends = bool(ops) and ops[0][1] <= 0.02 and ops[-1][1] <= 0.02
            turns = scales = 0.0
            if pts:
                turns = max(t[4] for _, t in pts) - min(t[4] for _, t in pts)
                scales = max(max(t[2] for _, t in pts) - min(t[2] for _, t in pts), max(t[3] for _, t in pts) - min(t[3] for _, t in pts))
                if (turns or scales) and "transform-origin" not in self.style(el):
                    Wn.append(f"{who} scales or rotates without transform-origin: it turns around the corner of the canvas. Add transform-box:fill-box;transform-origin:center")

            # does the loop close on itself?
            if not alt:
                if ops and abs(ops[0][1] - ops[-1][1]) > 0.02:
                    Wn.append(f"{who}: opacity is {ops[0][1]:g} at the start and {ops[-1][1]:g} at the end, so it pops when the loop restarts. Start and end on the same value")
                if pts:
                    s, e = pts[0][1], pts[-1][1]
                    dx, dy = e[0] - s[0], e[1] - s[1]
                    spin = abs(e[4] - s[4])
                    if abs(e[2] - s[2]) > 0.005 or abs(e[3] - s[3]) > 0.005 or (spin > 0.5 and abs(spin % 360) > 0.5 and abs(spin % 360 - 360) > 0.5):
                        if not hidden_ends:
                            Wn.append(f"{who} ends at a different size or angle than it starts and is visible at both ends: it snaps back each loop. End where it starts, or fade to opacity 0 at 0% and 100%")
                    elif math.hypot(dx, dy) > 0.5:
                        cdx, cdy = vec(self.M.get(self.parent.get(el), IDENT), dx, dy) if self.parent.get(el) is not None else (dx, dy)
                        box, seen = self.box.get(el), self.region(el)
                        s0 = vec(self.M.get(self.parent.get(el), IDENT), s[0], s[1])
                        e0 = vec(self.M.get(self.parent.get(el), IDENT), e[0], e[1])
                        offstage = box is not None and not inter(shift(box, *s0), seen) and not inter(shift(box, *e0), seen)
                        if not (hidden_ends or offstage or self.repeats(el, cdx, cdy)):
                            E.append(f"{who} travels {math.hypot(cdx, cdy):.0f} px and jumps back in plain sight. Close the loop: repeat its content every {math.hypot(dx, dy):.0f} px, or start and end outside the canvas or its mask, or fade to opacity 0 at 0% and 100%")
                dash = self.timeline(a, "stroke-dashoffset", self.inherit(el, "stroke-dashoffset", "0"))
                if dash and abs(num(dash[0][1]) - num(dash[-1][1])) > 0.01:
                    arr = [float(x) for x in re.findall(r"\d*\.?\d+", self.inherit(el, "stroke-dasharray", "") or "")]
                    period = sum(arr) * (2 if len(arr) % 2 else 1)
                    delta = abs(num(dash[0][1]) - num(dash[-1][1]))
                    if period <= 0:
                        E.append(f"{who} animates stroke-dashoffset on a line with no stroke-dasharray")
                    elif min(delta % period, period - delta % period) > 0.05 and not hidden_ends:
                        E.append(f"{who}: stroke-dashoffset moves {delta:g} but the dashes repeat every {period:g}, so the line jumps each loop. Move it by {period:g} or a multiple")
                off = self.timeline(a, "offset-distance", "0%")
                if off and off[0][1] != off[-1][1] and not hidden_ends and not re.search(r"[zZ]\s*['\")]", self.style(el).get("offset-path", "")):
                    Wn.append(f"{who} follows an open path and is visible at both ends: fade it to opacity 0 at 0% and 100%, or close the path")

            # what is seen when motion is off, and what a connector looks like at rest
            resting = self.inside(el, self.byid.get("facts")) or any(a.get("data-rest") == "shown" for a in self.chain(el))  # what takes turns on purpose
            if hidden_ends and far >= LEAD_TRAVEL and num(el.get("opacity"), 1) > 0.02 and not resting:
                Wn.append(f"{who} exists only while it travels, but with motion off it sits frozen where it starts. Give the element opacity=\"0\" as an attribute: the animation overrides it while it runs. When it is drawn where it rests on purpose, put it in a <g data-rest=\"shown\">")
            if first and "stroke-dashoffset" in props:
                stroke, width = self.inherit(el, "stroke", "none"), num(self.inherit(el, "stroke-width"), 1) * mscale(self.M.get(el, IDENT))
                for ti, theme in enumerate(("dark", "light")):
                    fg, bg = self.color(stroke, ti), self.color("$bg", ti)
                    if fg and bg and contrast(fg, bg) < LINE_CONTRAST:
                        Wn.append(f"{theme}: the connector {self.describe(el)} in {stroke} has contrast {contrast(fg, bg):.1f} against the background, below {LINE_CONTRAST}: it disappears at README width")
                if width < 2:
                    Wn.append(f"the connector {self.describe(el)} is {width:g} px thick: use 2 or more, it carries the direction of the flow")

            # is it large enough, slow enough and calm enough to read?
            moves_only = props <= {"transform"}
            if first and pts and moves_only and far < MIN_TRAVEL and scales < MIN_SCALE and turns < MIN_TURN:
                Wn.append(f"{who} moves {far:.1f} px: too small to read as motion, it looks like a glitch. Make it larger or remove it")
            if first and props == {"opacity"} and o_range < MIN_FADE:
                Wn.append(f"{who} changes opacity by {o_range:.2f}: too little to see. Make it {MIN_FADE} or more, or remove it")
            steps = re.match(r"steps\((\d+)", a["timing"])
            if pts:
                top = 0.0
                for (p0, t0), (p1, t1) in zip(pts, pts[1:]):
                    d, t = math.hypot(t1[0] - t0[0], t1[1] - t0[1]) * scale_k, (p1 - p0) / 100 * dur
                    if d > 0.5 and t > 0:
                        top = max(top, d / t)
                        if first and t < MIN_STEP and not steps:
                            Wn.append(f"{who} moves {d:.0f} px in {t * 1000:.0f} ms: that reads as a glitch. Give the move at least 150 ms")
                if top:
                    speeds.append(top)
                has_text = any(self.inside(t["el"], el) for t in self.texts)
                if first and top > MAX_SPEED:
                    Wn.append(f"{who} moves at {top:.0f} px/s: too fast to follow. Stay under {MAX_SPEED}")
                elif first and has_text and top > MAX_TEXT_SPEED:
                    Wn.append(f"{who} carries text at {top:.0f} px/s: nobody can read it. Stay under {MAX_TEXT_SPEED} (10-30 for lines to read in passing)")
                if first and steps and far / max(int(steps.group(1)), 1) > STEP_JUMP:
                    Wn.append(f"{who} jumps {far / int(steps.group(1)):.0f} px per step: use more steps or a continuous timing")
            if ops and o_range >= 0.3:
                turns_ = sum(1 for (_, x), (_, y), (_, z) in zip(ops, ops[1:], ops[2:]) if (y - x) * (z - y) < 0) + 1
                rate = turns_ / 2 / dur
                if first and rate > 3:
                    E.append(f"{who} flashes {rate:.1f} times a second: more than 3 can trigger seizures (WCAG 2.3.1). Slow it down")
                elif first and rate > 1:
                    Wn.append(f"{who} blinks {rate:.1f} times a second: slower than once a second reads as alive, faster reads as an alarm")
            if first and ops and 0.02 < min(o for _, o in ops) < 0.55 and any(self.inside(t["el"], el) for t in self.texts):
                Wn.append(f"{who} fades text down to {min(o for _, o in ops):g}: text that pulses stays at 0.55 or above")

            # a story told in steps: a keyframe that holds what the one before it set
            vals = [{k: v for k, v in d.items() if k not in IGNORED} for _, d in a["stops"]]
            holds = any(x == y and x for x, y in zip(vals, vals[1:]))
            if holds:
                staged.setdefault(round(dur, 3), a["name"])
            if self.inside(el, stage) and (far >= LEAD_TRAVEL or props & PAINTED or holds):
                lead = True
            if self.inside(el, stage) and (far >= LEAD_TRAVEL or "offset-distance" in props) and self.box.get(el):
                b = self.box[el]
                biggest = max(biggest, min(b[2] - b[0], b[3] - b[1]))
        if stage is not None and not lead:
            Wn.append(f"nothing in #stage travels {LEAD_TRAVEL} px or changes in steps: a flow is shown by something going from one step to the next")
        elif 0 < biggest < LEAD_SIZE:
            Wn.append(f"the largest thing that travels in #stage is {biggest:.0f} px, which is {biggest * README:.0f} px in a README: what goes through the flow is the lead, make it {LEAD_SIZE + 4} px or more")
        durs = sorted(staged)
        if len(durs) > 1 and any(abs(d / durs[0] - round(d / durs[0])) > 0.01 for d in durs):
            Wn.append(f"animations with steps last {', '.join(f'{d:g} s' for d in durs)}: they drift apart. Give the steps of one story the same duration (or a multiple) and shift them with negative animation-delay")
        all_durs = sorted({round(a["dur"], 3) for _, a in animated if a["dur"] > 0})
        f["loop_seconds"] = all_durs
        f["cycle_seconds"] = durs[-1] if durs else (all_durs[-1] if all_durs else 0)
        f["fastest_px_s"] = round(max(speeds)) if speeds else 0


def lum(hexc):
    h = hexc.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    ch = [int(h[i: i + 2], 16) / 255 for i in (0, 2, 4)]
    ch = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in ch]
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mix(fg, bg, alpha):
    def rgb(h):
        h = h.lstrip("#")
        h = "".join(c * 2 for c in h) if len(h) == 3 else h
        return [int(h[i: i + 2], 16) for i in (0, 2, 4)]

    return "#" + "".join(f"{round(f * alpha + b * (1 - alpha)):02x}" for f, b in zip(rgb(fg), rgb(bg)))


def read_source(raw):
    """Source text -> (palette, body without the palette and brief comments). Exits when there is no palette."""
    raw = re.sub(r"<!--\s*brief.*?-->", "", raw, flags=re.S)  # a brief may hold "--", which XML does not allow in a comment
    m = re.search(r"<!--\s*palette(.*?)-->", raw, re.S)
    if not m:
        sys.exit("error: no <!--palette ... --> comment in the source")
    palette = {}
    for line in m.group(1).strip().splitlines():
        p = line.split()
        if len(p) == 3 and p[1].startswith("#") and p[2].startswith("#"):
            palette[p[0]] = (p[1], p[2])
    return palette, raw.replace(m.group(0), "").strip()


def kind_of(path):
    """hero.src.svg is the hero, any other *.src.svg a section scene."""
    return "hero" if Path(path).name.split(".")[0] == "hero" else "section"


def check(root, palette, kind="hero"):
    global W, H
    W, H = CANVAS[kind]
    return Hero(root, palette, kind).run()


def summary(facts):
    f = facts
    bits = []
    if "title_px" in f:
        bits.append(f"title {f['title_px']} px, {f.get('title_words', 0)} words")
    if "name_px" in f:
        bits.append(f"name {f['name_px']} px")
    if "logo_px" in f:
        bits.append(f"logo {f['logo_px']} px")
    if "tagline_px" in f:
        bits.append(f"tagline {f['tagline_px']} px, {f.get('tagline_words', 0)} words")
    if "stage_share" in f:
        bits.append(f"picture {f['stage_share']:.0%} of the canvas, {f.get('stage_parts', 0)} parts, {f.get('stage_moving', 0)} moving")
    if "copy_share" in f:
        bits.append(f"text / picture {f['copy_share']:.0%} / {1 - f['copy_share']:.0%}")
    if "facts" in f:
        bits.append(f"{f['facts']} figures")
    bits.append(f"{f.get('still_words', 0)} still words in the picture")
    if f.get("text_sizes"):
        bits.append(f"text {f['text_sizes'][0]}-{f['text_sizes'][-1]} px in {len(f['text_sizes'])} sizes")
    bits.append(f"{f.get('animations', 0)} animations on {f.get('animated_elements', 0)} elements")
    if f.get("loop_seconds"):
        bits.append("loops of " + ", ".join(f"{d:g}" for d in f["loop_seconds"]) + " s")
    if f.get("fastest_px_s"):
        bits.append(f"fastest {f['fastest_px_s']} px/s")
    return "measured: " + " · ".join(bits)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    palette, body = read_source(Path(args[0]).read_text(encoding="utf-8"))
    try:
        root = ET.fromstring(body)
    except ET.ParseError as e:
        sys.exit(f"error: the SVG is not well-formed XML: {e}")
    hero = check(root, palette, kind_of(args[0]))
    hero.errors = list(dict.fromkeys(hero.errors))
    warns = list(dict.fromkeys(hero.warns))
    if "--json" in sys.argv:
        print(json.dumps({"errors": hero.errors, "warnings": warns, "measured": hero.facts}, indent=2))
    else:
        print("\n".join(["error: " + e for e in hero.errors] + ["warning: " + w for w in warns]) or "checks passed")
        print(summary(hero.facts))
    sys.exit(1 if hero.errors else 0)


if __name__ == "__main__":
    main()
