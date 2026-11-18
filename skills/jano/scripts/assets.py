#!/usr/bin/env python3
"""Icons, objects, logos, flags and file icons from known sets, one family per category per repository.

    python assets.py styles [category]                       every family, grouped by how it looks
    python assets.py suggest <category> --fill --stroke --corners --grid [--domain] --repo <name>
                                                             families ranked by how well they fit the repository's look
    python assets.py preview <category> [family[:variant],...]           one picture with the same things drawn by every family
    python assets.py choose <repo> <category> <family> --why "..." [--variant v]
                                                             records the choice in assets/readme/plan.json
    python assets.py search <repo> <category> <words>        names in the chosen family that match
    python assets.py get <repo> <category> <name> "<what it means here>" [--x --y --size --color $role --tint $role]
                                                             the <g> to paste into a scene
    python assets.py notices                                 THIRD_PARTY_NOTICES.md for Jano's own repository

Categories: icons, objects, logos, flags, files. The library is assets/library/ (manifest.json
and one .json.gz per family); every family's licence was read in its own repository, and only
MIT, ISC and CC0 families are packed. A picture uses one family per category, the one the plan
names, so a README keeps one look.
"""
import math, gzip, hashlib, html, json, re, sys
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "assets" / "library"
PLAN = "assets/readme/plan.json"
CATEGORIES = ("icons", "objects", "logos", "flags", "files")
ATTRS = {"fill": ("line", "solid", "glyph", "duotone", "pixel", "color"), "stroke": ("thin", "light", "regular", "bold", "none", "any"),
         "corners": ("round", "sharp", "mixed", "any"), "grid": None}
CONCEPTS = {  # what the preview draws in every family of a category, so families are compared on the same things
    "icons": ["file", "folder", "lock", "search", "check", "user", "settings", "arrow right", "terminal", "cloud"],
    "objects": ["book", "laptop", "rocket", "package", "magnifying glass", "key", "light bulb", "gear", "locked", "chart"],
    "logos": ["github", "python", "docker", "react", "linux", "npm", "javascript", "rust", "slack", "visual studio code"],
    "flags": ["mx", "us", "br", "fr", "jp", "de", "in", "gb", "es", "ca"],
    "files": ["json", "markdown", "python", "folder", "typescript", "yaml", "docker", "git", "image", "lock"],
}
_sets = {}


def manifest():
    return json.loads((LIB / "manifest.json").read_text(encoding="utf-8"))["sets"]


def family(prefix):
    return next((f for f in manifest() if f["prefix"] == prefix), None)


def load(prefix):
    if prefix not in _sets:
        _sets[prefix] = json.loads(gzip.decompress((LIB / f"{prefix}.json.gz").read_bytes()))
    return _sets[prefix]


def names(prefix, variant=None):
    """Icon names of a family (aliases included), limited to a variant when the family has them."""
    s, f = load(prefix), family(prefix)
    pattern = f["variants"].get(variant) if variant else None
    out = list(s["icons"]) + list(s["aliases"])
    return [n for n in out if not pattern or re.search(pattern, n)]


SYNONYMS = {  # the words families use for the same thing
    "file": ["document", "file-text", "page"], "search": ["magnifying-glass", "magnifier", "find", "zoom"], "settings": ["gear", "cog", "cog-6-tooth"],
    "user": ["person", "account", "profile-circle"], "folder": ["directory"], "terminal": ["command-line", "console", "prompt"],
    "lock": ["padlock", "locked"], "check": ["checkmark", "tick", "done"], "arrow right": ["arrow-right", "right-arrow", "arrow-forward"],
    "cloud": ["cloud"], "trash": ["delete", "bin"], "edit": ["pencil", "pen"], "warning": ["alert", "exclamation"], "home": ["house"],
}


def starts(w, xs):
    """A word starts a longer part only when little is added: search -> searching, not rust -> rustdesk."""
    return len(w) >= 4 and any(x.startswith(w) and len(x) - len(w) <= 3 for x in xs)


def find(prefix, words, variant=None, limit=12):
    """Names ranked by how well they match the words: whole name, name parts, tags, then words that start a part."""
    s = load(prefix)
    phrase = " ".join(words).lower().strip()
    tries = [phrase] + SYNONYMS.get(phrase, [])
    for alt in (phrase.replace(".", "dot").replace("+", "plus"), phrase.replace(".", "").replace("+", "p")):
        if alt and alt not in tries:  # node.js is nodedotjs in one set and nodejs in another
            tries.append(alt)
    best = {}
    for rank, attempt in enumerate(tries):
        ws = [w for w in re.split(r"[\s,]+|-", attempt) if w]
        joined = "-".join(ws)
        for n in names(prefix, variant):
            base = s["aliases"].get(n, n)
            parts = n.split("-")
            tags = set(t.lower() for t in s["tags"].get(base, []))
            score = 0
            if n == joined:
                score += 20
            elif n.startswith(joined + "-") and len(n) - len(joined) <= 9:
                score += 12
            for w in ws:
                score += 3 if w in parts else 2 if w in tags else 1 if starts(w, parts) or starts(w, tags) else 0
            if not score or not all(w in parts or w in tags or starts(w, parts) for w in ws):
                continue
            score -= rank  # the user's own words before their synonyms
            if score > best.get(n, -99):
                best[n] = score
    return [n for n, _ in sorted(best.items(), key=lambda kv: (-kv[1], len(kv[0])))[:limit]]


def body_of(prefix, name):
    s = load(prefix)
    base = s["aliases"].get(name, name)
    if base not in s["icons"]:
        return None, None
    w, h = s["sizes"].get(base, [s["width"], s["height"]])
    return s["icons"][base], (w, h)


# ---- the plan
def plan_path(repo):
    return Path(repo) / PLAN


def read_plan(repo):
    p = plan_path(repo)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def chosen(repo, category):
    c = (read_plan(repo).get("assets") or {}).get(category)
    if not c:
        sys.exit(f"error: the plan has no {category} family yet. Look at `assets.py styles {category}` and `assets.py preview {category}`, "
                 f"then `assets.py choose <repo> {category} <family> --why \"...\"`")
    return c


# ---- commands
def cmd_styles(category=None):
    fams = [f for f in manifest() if not category or f["category"] == category]
    by = {}
    for f in fams:
        a = f["attrs"]
        by.setdefault((f["category"], a["fill"]), []).append(f)
    for (cat, fill), group in sorted(by.items()):
        print(f"\n{cat} · {fill}")
        for f in sorted(group, key=lambda f: f["prefix"]):
            a = f["attrs"]
            variants = f" variants: {', '.join(f['variants'])}" if f["variants"] else ""
            print(f"  {f['prefix']:28} {f['count']:6} · stroke {a['stroke']}, corners {a['corners']}, grid {a['grid'] or 'free'}, "
                  f"colour {'takes a $role' if f['recolor'] == 'mono' else 'keeps its own' if f['recolor'] == 'keep' else 'never changes'} · {f['licence']}{variants}")
            print(f"  {'':28} {f['about']}")


# how a variant changes a family's look; a variant not listed looks like the family
VARIANT_LOOK = {
    "fill": {"fill": "solid", "stroke": "none"}, "filled": {"fill": "solid", "stroke": "none"}, "solid": {"fill": "solid", "stroke": "none"},
    "negative": {"fill": "solid", "stroke": "none"}, "duotone": {"fill": "color"},
    "thin": {"stroke": "thin"}, "light": {"stroke": "light"}, "bold": {"stroke": "bold"},
    "mini": {"fill": "solid", "stroke": "none", "grid": 20}, "micro": {"fill": "solid", "stroke": "none", "grid": 16},
    "16": {"grid": 16}, "24": {"grid": 24},
    "outline": {"fill": "line"}, "line": {"fill": "line"}, "regular": {"fill": "line", "stroke": "regular"},
}
NEAR = {("solid", "glyph"), ("glyph", "solid"), ("thin", "light"), ("light", "thin"), ("regular", "bold"), ("bold", "regular")}


def looks(f):
    """The family's looks: its default one when it has no variants, else one per variant."""
    base = {k: v for k, v in f["attrs"].items() if k != "domain"}
    if base.get("stroke") == "any":
        base["stroke"] = "regular"
    if not f["variants"]:
        return [(None, base)]
    return [(v, {**base, **VARIANT_LOOK.get(v, {})}) for v in f["variants"]]


def fit(look, want):
    score = 0
    for k, v in want.items():
        if v is None or k == "domain":
            continue
        a = look.get(k)
        if k == "stroke" and look.get("fill") in ("solid", "glyph") and want.get("fill") in ("solid", "glyph"):
            score += 3  # a filled shape has no stroke to compare
        elif k == "grid":
            score += 2 if a and abs(a - int(v)) <= 1 else 1 if a and abs(a - int(v)) <= 8 else 0
        elif a == v:
            score += 3
        elif (a, v) in NEAR:
            score += 2
    return score


def cmd_suggest(category, want, repo=""):
    rows = []
    for f in (f for f in manifest() if f["category"] == category):
        penalty = 3 if f["attrs"].get("domain") and f["attrs"]["domain"] != want.get("domain") else 0  # a set made for one field
        variant, score = max(((v, fit(l, want)) for v, l in looks(f)), key=lambda x: x[1])
        # families that fit equally are listed in an order of their own for each repository, never alphabetically,
        # so the same family does not win every tie
        tie = hashlib.sha1(f"{repo}:{f['prefix']}".encode()).hexdigest()
        rows.append((penalty - score, tie, f["prefix"], variant, f))
    rows.sort()
    best = rows[0][0] if rows else 0
    for s, _, p, v, f in rows:
        name = f"{p}:{v}" if v else p
        print(f"{'*' if s == best else ' '} {-s:2}  {name:28} {f['about']}")
    print("\n* fits best; family:variant names the variant that fits. Preview them (`preview <category> family:variant,...`),\n"
          "pick the one that looks like the mark, and record it and why with `choose ... --variant`.")


def cmd_preview(category, only=None):
    import tempfile
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build
    want = [x.split(":") for x in only] if only else [[f["prefix"]] for f in manifest() if f["category"] == category]
    fams = [(family(w[0]), w[1] if len(w) > 1 else None) for w in want]
    bad = [w[0] for w, (f, _) in zip(want, fams) if not f or f["category"] != category]
    if bad:
        sys.exit(f"error: not {category} families: {', '.join(bad)}")
    rows = []
    for f, variant in fams:
        cells = []
        for concept in CONCEPTS[category]:
            hit = find(f["prefix"], [concept], variant=variant, limit=1)
            if hit:
                body, (w, h) = body_of(f["prefix"], hit[0])
                cells.append(f'<div class=c><svg viewBox="0 0 {w} {h}" width="44" height="44" style="color:#e6edf3">{body}</svg><i>{html.escape(hit[0][:16])}</i></div>')
            else:
                cells.append('<div class=c><b>—</b><i>none</i></div>')
        rows.append(f'<div class=r><p>{f["prefix"]}{":" + variant if variant else ""}<br><small>{f["attrs"]["fill"]}, {f["attrs"]["stroke"]}</small></p>{"".join(cells)}</div>')
    page = Path(tempfile.mkdtemp(prefix=f"jano-assets-{category}-")) / "preview.html"
    page.write_text('<!doctype html><meta charset=utf-8><style>body{margin:0;padding:16px;background:#0d1117;color:#e6edf3;font:13px system-ui;width:1240px}'
                    '.r{display:flex;align-items:center;gap:6px;border-bottom:1px solid #30363d;padding:6px 0}.r p{width:180px;margin:0}'
                    '.c{width:96px;display:flex;flex-direction:column;align-items:center;gap:2px}.c i{font-size:10px;color:#8b949e}</style>'
                    + "".join(rows), encoding="utf-8")
    png = page.with_suffix(".png")
    if build.take_pictures([(page, png, 40 + 76 * len(rows))]):
        print(f"preview {png}")
    else:
        print(f"no browser to take the picture; open {page}")


def cmd_choose(repo, category, prefix, why, variant=None):
    f = family(prefix)
    if not f or f["category"] != category:
        sys.exit(f"error: {prefix} is not a {category} family: see `assets.py styles {category}`")
    if f["variants"] and variant not in f["variants"]:
        sys.exit(f"error: {prefix} comes in variants {', '.join(f['variants'])}: give --variant, the one that matches the mark")
    if len(why.split()) < 6:
        sys.exit("error: say why in a sentence: what in the repository's mark or hero this family matches (weight, corners, fill)")
    p = plan_path(repo)
    plan = read_plan(repo)
    plan.setdefault("assets", {})[category] = {"family": prefix, "variant": variant, "why": why}
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{category}: {prefix}{' / ' + variant if variant else ''}")


def cmd_search(repo, category, words):
    c = chosen(repo, category)
    hits = find(c["family"], words, c.get("variant"), limit=20)
    if not hits:
        print(f"nothing in {c['family']} for {' '.join(words)}: try other words for the same thing (`assets.py search` matches names and tags), "
              "or draw it in the family's manner and declare it with data-icon")
    for n in hits:
        print(n)


def snippet(prefix, name, means, x=0.0, y=0.0, size=None, color="$muted", tint=None):
    f = family(prefix)
    body, dims = body_of(prefix, name)
    if body is None:
        sys.exit(f"error: {prefix} has no {name!r}: `assets.py search` lists what it has")
    w, h = dims
    if size is None:
        # 24 px, or larger for a family drawn in thinner lines, so its strokes reach 2 px on the scene
        widths = [float(v) for v in re.findall(r'stroke-width="([\d.]+)"', body)]
        size = max(24.0, math.ceil(max(w, h) * 2 / min(widths))) if widths and min(widths) > 0 else 24.0
    k = size / max(w, h)
    tag = hashlib.sha1(f"{prefix}:{name}:{x}:{y}".encode()).hexdigest()[:6]
    # ids inside the drawing (gradients, clips) get a suffix, so two copies in one scene do not collide
    for i in set(re.findall(r'\bid="([^"]+)"', body)):
        body = body.replace(f'id="{i}"', f'id="{i}-{tag}"').replace(f"url(#{i})", f"url(#{i}-{tag})").replace(f'href="#{i}"', f'href="#{i}-{tag}"')
    if tint and f["recolor"] != "never":
        body = re.sub(r'(fill|stroke|stop-color)="(?!none|url)[^"]+"', lambda m: f'{m.group(1)}="{tint}"', body)
        body = re.sub(r'(fill|stroke|stop-color):\s*(?!none|url)[^;"]+', lambda m: f"{m.group(1)}:{tint}", body)
    colour = f' color="{color}"' if f["recolor"] == "mono" else ""
    means = re.sub(r'["<>&]', "", means)
    return (f'<g data-asset="{prefix}:{name}" data-icon="{means}" data-size="{size:g}" transform="translate({x:g} {y:g}) scale({k:.4g})"{colour}>'
            f"{body}</g>")


def cmd_get(repo, category, name, means, x, y, size, color, tint):
    c = chosen(repo, category)
    if c.get("variant"):
        pattern = family(c["family"])["variants"][c["variant"]]
        if not re.search(pattern, name):
            sys.exit(f"error: {name} is not in the {c['variant']} variant the plan chose for {c['family']}: search again")
    print(snippet(c["family"], name, means, x, y, size, color, tint))


def notice_text(f):
    return (LIB / f["licence_text"]).read_text(encoding="utf-8").strip()


def notices():
    """The text of THIRD_PARTY_NOTICES.md, from the manifest and the licence files."""
    out = ["# Third-party notices", "",
           "Jano's skill ships the asset sets below in `skills/jano/assets/library/`, and the two fonts in `skills/jano/assets/`. "
           "Each set's licence was read in its own repository; its full text is in `skills/jano/assets/library/licenses/`. "
           "The pictures Jano draws with them carry the set and icon name in a `data-asset` attribute and the set's notice in the SVG's metadata.", "",
           "| Set | Category | Licence | Holder | Source | Icons |", "|---|---|---|---|---|---|"]
    for f in sorted(manifest(), key=lambda f: (f["category"], f["prefix"])):
        out.append(f"| {f['title']} | {f['category']} | {f['licence']} | {f['holder']} | {f['repo']} | {f['count']} |")
    out += ["", "Brand logos are trademarks of their owners; Jano uses them only to name the product they stand for.", "",
            "## Fonts", "", "- Space Grotesk, SIL Open Font License 1.1 (`skills/jano/assets/SpaceGrotesk-OFL.txt`).",
            "- JetBrains Mono, SIL Open Font License 1.1 (`skills/jano/assets/JetBrainsMono-OFL.txt`).", "", "## Licence texts", ""]
    seen = set()
    for f in sorted(manifest(), key=lambda f: f["licence_text"]):
        if f["licence_text"] in seen:
            continue
        seen.add(f["licence_text"])
        titles = ", ".join(x["title"] for x in manifest() if x["licence_text"] == f["licence_text"])
        out += [f"### {titles}", "", "```text", notice_text(f), "```", ""]
    return "\n".join(out)


def cmd_notices():
    root = Path(__file__).resolve().parents[3]
    (root / "THIRD_PARTY_NOTICES.md").write_text(notices(), encoding="utf-8", newline="\n")
    print(f"wrote {root / 'THIRD_PARTY_NOTICES.md'}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    opts, pos = {}, []
    it = iter(args)
    for a in it:
        if a.startswith("--"):
            opts[a[2:]] = next(it, "")
        else:
            pos.append(a)
    cmd = pos[0]
    if cmd == "styles":
        cmd_styles(pos[1] if len(pos) > 1 else None)
    elif cmd == "suggest":
        if len(pos) < 2 or pos[1] not in CATEGORIES:
            sys.exit(f"error: suggest <category>, one of {', '.join(CATEGORIES)}")
        cmd_suggest(pos[1], {k: opts.get(k) for k in list(ATTRS) + ["domain"]}, opts.get("repo", ""))
    elif cmd == "preview":
        cmd_preview(pos[1], pos[2].split(",") if len(pos) > 2 else None)
    elif cmd == "choose":
        cmd_choose(pos[1], pos[2], pos[3], opts.get("why", ""), opts.get("variant"))
    elif cmd == "search":
        cmd_search(pos[1], pos[2], pos[3:])
    elif cmd == "get":
        if len(pos) < 5:
            sys.exit('error: get <repo> <category> <name> "<what it means here>"')
        cmd_get(pos[1], pos[2], pos[3], pos[4], float(opts.get("x", 0)), float(opts.get("y", 0)), float(opts["size"]) if opts.get("size") else None,
                opts.get("color", "$muted"), opts.get("tint"))
    elif cmd == "notices":
        cmd_notices()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
