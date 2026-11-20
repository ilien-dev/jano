#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["fonttools", "brotli"]
# ///
"""Measure a README against its plan, so the result is counted and not guessed.

    uv run readme.py survey <repo>     what is there now, and what to ask the user before planning
    uv run readme.py rules             the rules: sections, word budgets, pictures, Markdown elements
    uv run readme.py check <repo>      the plan, the README, its translations, the pictures and the judges
    uv run readme.py judge <repo>      pictures and texts for the judges, and the prompts to give them

The plan lives in <repo>/assets/readme/plan.json (see `rules`). `check` exits 1 while
anything is wrong, so a README is finished only when it passes.
"""
import hashlib, json, re, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check as svgcheck  # noqa: E402
import kit  # noqa: E402

PLAN = "assets/readme/plan.json"
JUDGES = "assets/readme/judges.json"
AUDIENCES = ("general", "technical")

# ---- the rules. role: words in the section (min, max), picture per audience, alerts it may hold, may it hold a table
ROLES = {
    "lead":         {"words": (30, 110), "picture": {"general": "none", "technical": "none"}, "alerts": (), "table": False,
                     "what": "the first paragraphs under the top: what it is, for whom, what they get. No heading of its own"},
    "demo":         {"words": (15, 130), "picture": {"general": "required", "technical": "required"}, "alerts": ("TIP",), "table": False,
                     "what": "it working on a real case: what goes in, what comes out"},
    "features":     {"words": (40, 200), "picture": {"general": "required", "technical": "optional"}, "alerts": ("NOTE",), "table": False,
                     "what": "what a person gets, 3 to 6 items with a bold lead-in each"},
    "how":          {"words": (40, 220), "picture": {"general": "required", "technical": "required"}, "alerts": ("NOTE",), "table": False,
                     "what": "how it works, 3 to 5 numbered steps; the deep version goes to docs/"},
    "audience":     {"words": (20, 130), "picture": {"general": "optional", "technical": "optional"}, "alerts": (), "table": False,
                     "what": "who it is for, as people with a situation, 2 to 4 items"},
    "results":      {"words": (15, 160), "picture": {"general": "optional", "technical": "optional"}, "alerts": ("NOTE",), "table": True,
                     "what": "measured results, each with the file or run it comes from"},
    "compare":      {"words": (20, 200), "picture": {"general": "optional", "technical": "optional"}, "alerts": ("NOTE",), "table": True,
                     "what": "against the alternatives a reader already knows, fairly"},
    "install":      {"words": (10, 170), "picture": {"general": "optional", "technical": "optional"}, "alerts": ("IMPORTANT", "WARNING", "TIP"), "table": True,
                     "what": "the shortest path first, in a code block; other paths in <details>"},
    "use":          {"words": (20, 220), "picture": {"general": "optional", "technical": "optional"}, "alerts": ("TIP", "IMPORTANT", "WARNING", "CAUTION"), "table": True,
                     "what": "the first real use, then the common ones"},
    "reference":    {"words": (20, 260), "picture": {"general": "none", "technical": "none"}, "alerts": ("NOTE",), "table": True,
                     "what": "commands, options, API: a table or <details>; the full list in docs/"},
    "faq":          {"words": (30, 600), "picture": {"general": "none", "technical": "none"}, "alerts": (), "table": False,
                     "what": "questions people ask, each in its own <details>"},
    "limits":       {"words": (15, 170), "picture": {"general": "none", "technical": "none"}, "alerts": ("WARNING", "CAUTION", "NOTE"), "table": False,
                     "what": "what it does not do, plainly"},
    "privacy":      {"words": (15, 140), "picture": {"general": "optional", "technical": "none"}, "alerts": ("NOTE",), "table": False,
                     "what": "where the user's data goes"},
    "develop":      {"words": (10, 160), "picture": {"general": "none", "technical": "none"}, "alerts": (), "table": True,
                     "what": "building and testing it; long versions go to CONTRIBUTING.md or docs/"},
    "about":        {"words": (10, 110), "picture": {"general": "optional", "technical": "optional"}, "alerts": (), "table": False,
                     "what": "the name, the author, related projects"},
    "contributing": {"words": (5, 80), "picture": {"general": "none", "technical": "none"}, "alerts": (), "table": False,
                     "what": "one line and a link to CONTRIBUTING.md"},
    "license":      {"words": (3, 60), "picture": {"general": "none", "technical": "none"}, "alerts": (), "table": False,
                     "what": "the licence in one or two lines"},
}
REQUIRED = {"general": ["lead", "install", "license"], "technical": ["lead", "install", "license"]}
ONE_OF = {"general": [("demo", "features")], "technical": [("demo", "features", "how"), ("use", "reference")]}
SECTIONS = {"general": (5, 9), "technical": (6, 11)}       # ## headings
WORDS = {"general": 1100, "technical": 1600}              # words a reader sees without opening anything
PICTURES = {"general": (3, 5), "technical": (2, 4)}       # section scenes, the hero apart
ALERTS = 3                 # in the whole README
BADGES = 6
BOLD_WORDS = 8             # a bold run is a lead-in, not a sentence
ITALICS = 2                # per section
PARAGRAPH_WORDS = 90
LIST_ITEMS = 7             # outside <details>
FEATURE_ITEMS = (3, 6)     # what a person gets, in the features role
HOW_STEPS = (3, 5)         # numbered steps in the how role
TABLE_COLUMNS, TABLE_ROWS = 6, 10
SAME = 0.5                 # two pictures that share this much of what they show are the same picture
MARKERS = r"\b(experimental|beta|alpha|preview|coming soon|roadmap|planned|unreleased|wip|work in progress|not yet)\b"
FRONTEND = ("react", "vue", "svelte", "solid-js", "preact", "vite", "next", "nuxt", "astro", "@tauri-apps/api", "electron", "angular")
JARGON = r"\b(API|CLI|MCP|JSON|HTTP|SDK|SQL|SQLite|YAML|TOML|regex|stdin|stdout|hook|daemon|crate|async|runtime|schema|endpoint|token|REST|gRPC|binary|env|config|PID|socket|cache|compiler|parser|AST|LSP)\b"


def sha(*parts):
    h = hashlib.sha256()
    for p in parts:
        h.update(p if isinstance(p, bytes) else p.encode("utf-8"))
    return h.hexdigest()[:16]


def source_bytes(path):
    """A source's bytes with line endings as git stores them, so a clone on any system has the same fingerprint."""
    return path.read_bytes().replace(b"\r\n", b"\n") if path.exists() else b""


def check_backdrop(r, where, svg, want):
    """Every picture has the backdrop the plan names: none, or the same pattern and motion, so the README reads as one piece."""
    if want is None:
        return
    tag = re.search(r'<g\b[^>]*\bid="backdrop"[^>]*>', svg)
    if want == "none":
        if tag:
            r.e(where, 'has a #backdrop and the plan says "backdrop": "none": take it out')
        return
    if not tag:
        r.e(where, f'has no #backdrop and the plan says "{want}": paste kit.py backdrop --kind {want.split()[0]} --motion {want.split()[1]}')
        return
    got = re.search(r'data-backdrop="([^"]*)"', tag.group())
    if not got:
        r.e(where, f'has a #backdrop that does not say which it is: paste kit.py backdrop --kind {want.split()[0]} --motion {want.split()[1]}, '
                   'or give a texture drawn by hand data-backdrop="custom <motion>" (and the plan "custom <motion>")')
    elif got.group(1) != want:
        r.e(where, f'has the backdrop "{got.group(1)}" and the plan says "{want}": every picture uses the one the plan names')


def stale(src):
    """The outputs of a source that are missing or were built from another version of it."""
    want = hashlib.sha256(source_bytes(src)).hexdigest()[:16]
    out = []
    for theme in ("dark", "light"):
        f = src.with_name(src.name.replace(".src.svg", f"-{theme}.svg"))
        m = re.search(r'data-jano-src="([0-9a-f]+)"', f.read_text(encoding="utf-8", errors="replace")[:4000]) if f.exists() else None
        if not m or m.group(1) != want:
            out.append(f.name)
    return out


def social_stamp(card):
    """The source fingerprint build.py writes into the social preview (its .svg or its .png), or None."""
    data = card.read_bytes()[:4000] if card.exists() else b""
    # 16 hex digits exactly: in the PNG the chunk's binary CRC follows, and its first byte can read as one more digit
    m = re.search(rb'tEXtjano-src\0([0-9a-f]{16})|data-jano-src="([0-9a-f]{16})"', data)
    return (m.group(1) or m.group(2)).decode() if m else None


# ---- reading Markdown the way GitHub shows it, roughly
def strip_code(md):
    return re.sub(r"^(```|~~~).*?^\1[ \t]*$", "", md, flags=re.S | re.M)


def visible(md):
    """What a reader sees without opening anything: no code, no closed <details>, no tags, no comments."""
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    md = strip_code(md)
    md = re.sub(r"<details\b.*?</details>", "", md, flags=re.S | re.I)
    md = re.sub(r"<img\b[^>]*>|<source\b[^>]*>", "", md, flags=re.I)
    md = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", md)
    md = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", md)
    md = re.sub(r"<[^>]+>", " ", md)
    md = re.sub(r"^\s*\|?[\s:|-]+\|[\s:|-]*$", "", md, flags=re.M)  # table rules
    md = re.sub(r"^>\s*\[!\w+\]\s*$", "", md, flags=re.M)
    return md


def words(text):
    return len(re.findall(r"[\w'’-]+", text))


def split(md):
    """(top block, [(heading, body)]) by ## headings outside code."""
    lines, top, sections, cur, fence = md.splitlines(), [], [], None, None
    for line in lines:
        m = re.match(r"^(```|~~~)", line)
        if m:
            fence = None if fence == m.group(1) else (fence or m.group(1))
        h = re.match(r"^##\s+(.+?)\s*#*\s*$", line) if not fence else None
        if h:
            cur = [h.group(1), []]
            sections.append(cur)
        elif cur is None:
            top.append(line)
        else:
            cur[1].append(line)
    return "\n".join(top), [(h, "\n".join(b)) for h, b in sections]


def lead_of(top):
    """The lead: what follows the hero, title, badges and links in the top block."""
    out = []
    for block in re.split(r"\n\s*\n", top):
        b = block.strip()
        if not b or b.startswith(("<p align", "<h1", "<picture", "<div", "# ", "---", "<!--", "[![")) or re.fullmatch(r"(<[^>]+>\s*)+", b) \
                or re.search(r"\(README\.[\w-]+\.md\)|href=\"README\.[\w-]+\.md\"", b) and words(visible(b)) < 12:  # the language row
            continue
        out.append(b)
    return "\n\n".join(out)


def norm(heading):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>|[*_`]", "", heading or "")).strip().lower()


def slug(heading):
    h = re.sub(r"<[^>]+>|[*_`]", "", heading).strip().lower()
    h = re.sub(r"[^\w\- ]", "", h, flags=re.U)
    return h.replace(" ", "-")


def emoji(s):
    return any(ord(c) > 0x2190 and not c.isalpha() and c not in "–—’“”·…→←" for c in s)


# ---- the parts of a picture that say what it shows
def stage_signature(src):
    """Words and large shapes of #stage in a source, to tell two pictures apart."""
    raw = src.read_text(encoding="utf-8")
    try:
        if "<!--palette" in raw:
            palette, body = svgcheck.read_source(raw)
        else:  # a built picture: its colours are already written in
            palette, body = {}, raw
        root = ET.fromstring(body)
    except (Exception, SystemExit):
        return set(), set()
    kind = "hero" if src.name.startswith("hero") else svgcheck.kind_of(src)
    hero = svgcheck.Hero.__new__(svgcheck.Hero)
    svgcheck.W, svgcheck.H = svgcheck.CANVAS[kind]
    hero.__init__(root, palette, kind)
    stage = hero.byid.get("stage")
    if stage is None:
        return set(), set()
    text = " ".join(t["s"] for t in hero.texts if hero.inside(t["el"], stage)).lower()
    ws = {w for w in re.findall(r"[a-záéíóúñü0-9]{3,}", text)}
    w, h = svgcheck.CANVAS[kind]
    shapes = {(s["tag"], round((s["box"][2] - s["box"][0]) / w, 1), round((s["box"][3] - s["box"][1]) / h, 1))
              for s in hero.shapes if hero.inside(s["el"], stage) and min(s["box"][2] - s["box"][0], s["box"][3] - s["box"][1]) >= 60}
    return ws, shapes


def invented_commands(repo, raw):
    """Commands drawn in a picture (`<name> <word>`) that no Markdown file of the repository mentions."""
    name = repo.name.lower()
    if len(name) < 3:  # a name this short is an ordinary word ("a folder"), not a command
        return []
    drawn = set()
    for t in re.findall(r"<text(?:\s[^>]*)?>(.*?)</text>", raw, re.S):
        t = re.sub(r"<[^>]+>", "", t)
        drawn |= {m.group(1) for m in re.finditer(rf"(?<![\w/.-])({re.escape(name)}(?::| )[a-z][\w-]*)", t.lower())}
    if not drawn:
        return []
    text = " ".join(f.read_text(encoding="utf-8", errors="replace").lower() for f in list(repo.glob("*.md")) + list(repo.glob("docs/**/*.md"))[:200])
    return sorted(c for c in drawn if c not in text)


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a and b else 0.0


# ---- survey
def survey(repo):
    out = {"repo": str(repo)}
    readmes = sorted(p.name for p in repo.glob("README*.md"))
    out["readmes"] = readmes
    md = (repo / "README.md").read_text(encoding="utf-8") if (repo / "README.md").exists() else ""
    top, secs = split(md)
    out["now"] = {"sections": [h for h, _ in secs], "visible_words": words(visible(md)), "pictures": len(re.findall(r"<img\b|!\[", md)),
                  "alerts": len(re.findall(r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]", md, re.M))}
    out["docs"] = sorted(str(p.relative_to(repo)).replace("\\", "/") for p in repo.glob("docs/**/*.md"))[:40]
    out["assets"] = {"hero": next((h for h in ("assets/hero.src.svg", "assets/hero-dark.svg") if (repo / h).exists()), None), "logo": (repo / "assets/logo.svg").exists(),
                     "brand": sorted(str(p.relative_to(repo)).replace("\\", "/") for p in list(repo.glob("assets/*.svg")) + list(repo.glob("assets/brand/*")) + list(repo.glob("brand/*")))[:20]}
    found = []
    for f in [repo / r for r in readmes] + [repo / "CHANGELOG.md"] + [d for d in sorted(repo.glob("docs/**/*.md")) if not re.search(r"superpowers|plans?/|specs?/", d.as_posix())][:40]:
        if not f.exists():
            continue
        in_unreleased = False
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if f.name == "CHANGELOG.md":
                if re.match(r"^##\s", line):
                    in_unreleased = "unreleased" in line.lower()
                if not in_unreleased:
                    continue
            if re.search(MARKERS, line, re.I) and len(found) < 30:
                found.append(f"{f.relative_to(repo).as_posix()}:{i}: {line.strip()[:140]}")
    out["unfinished"] = found
    pkg = repo / "package.json"
    deps = ""
    if pkg.exists():
        try:
            j = json.loads(pkg.read_text(encoding="utf-8"))
            deps = " ".join(list(j.get("dependencies", {})) + list(j.get("devDependencies", {})))
        except ValueError:
            pass
    screen = [d for d in FRONTEND if re.search(rf"(^|\s){re.escape(d)}(\s|$)", deps)] + (["index.html"] if (repo / "index.html").exists() else [])
    screen += ["tauri"] if (repo / "src-tauri").exists() else []
    out["has_screen"] = screen
    v = visible(md)
    out["jargon_per_100_words"] = round(100 * len(re.findall(JARGON, v)) / max(words(v), 1), 1)
    ask = []
    if found:
        ask.append("the unfinished lines are candidates found by words like 'planned' or 'beta': a line that is not about a feature "
                   "(a log, a sentence that happens to use the word) goes in the plan with \"decision\": \"not-a-feature\", no question needed")
    ask.append("audience: who reads this README, people who use the result (general) or professionals of the trade (technical)? "
               f"Propose one from what you read (jargon {out['jargon_per_100_words']} per 100 words now) and let the user confirm it")
    if found:
        ask.append(f"unfinished: {len(found)} line(s) mark something as not finished; for each feature, keep it in the README or leave it out?")
    if screen:
        ask.append(f"real screen: the project has a screen ({', '.join(screen)}). The scenes are drawn SVG; ask whether one section may show a real "
                   "screenshot inside its scene instead, and only where a drawing would explain less")
    pick = kit.backdrop("any", "still", repo=repo.resolve().name).split('data-backdrop="', 1)[1].split()[0]
    out["backdrop_pick"] = pick
    ask.append("backdrop: should the pictures have a background pattern, and should it move? Propose from what the repository is about: "
               "none (the picture carries itself, or the brand is plain), a still pattern, or a moving one, and the pattern whose subject fits "
               f"(kit.py list says what each suits). When no subject fits, propose {pick!r}, the pick for this repository (kit.py backdrop --kind any "
               "--repo <name>), not dots by habit. The answer goes in the plan as \"backdrop\": \"none\" or \"<kind> <motion>\"")
    out["ask_the_user"] = ask
    return out


# ---- the checks
class Report:
    def __init__(self):
        self.errors, self.warns, self.facts = [], [], {}

    def e(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def w(self, where, msg):
        self.warns.append(f"{where}: {msg}")


TRANSLATION = 1.25  # a translation runs longer than English: its word caps stretch by this much


def check_links(r, name, md, repo):
    """Every relative link, image and picture source points at a file that exists."""
    seen = set()
    refs = re.findall(r"\]\(([^)\s]+)", strip_code(md)) + re.findall(r'(?:href|src|srcset)="([^"]+)"', md)
    for ref in refs:
        path = ref.split("#")[0].split("?")[0]
        if not path or re.match(r"^[a-z][a-z0-9+.-]*:", path, re.I) or path.startswith("//") or path in seen:
            continue
        seen.add(path)
        if not (repo / path.lstrip("/")).exists():
            r.e(name, f"links {path}, which does not exist: write the file, or link one that does")


def check_markdown(r, name, md, plan_sections, audience, repo=None, scale=1.0):
    top, secs = split(md)
    h1 = len(re.findall(r"^#\s+\S", strip_code(md), re.M)) + len(re.findall(r"<h1\b", md, re.I))
    if h1 != 1:
        r.e(name, f"{h1} top-level headings: a README has one (the title)")
    if re.search(r"^####\s", strip_code(md), re.M):
        r.w(name, "#### headings: go two levels deep at most (## and ###); a deeper part belongs in docs/")
    for m in re.finditer(r"^(```|~~~)[ \t]*$", md, re.M):
        before = md[:m.start()]
        if len(re.findall(r"^(```|~~~)", before, re.M)) % 2 == 0:
            r.e(name, f"a code block at line {before.count(chr(10)) + 1} has no language: write ```bash, ```json...; GitHub colours it and the reader knows what it is")
    if re.search(r"<[^>]*\s(style|color)\s*=|<font\b", strip_code(md), re.I):
        r.e(name, "style=, color= or <font>: GitHub removes them. Colour comes from the pictures, the badges and the alerts")
    badges = len(re.findall(r"img\.shields\.io|/badge\.svg|badgen\.net", top))
    r.facts.setdefault(name, {})["badges"] = badges
    if badges > BADGES:
        r.w(name, f"{badges} badges: keep the {BADGES} or fewer a reader acts on (version, licence, what it runs in)")
    for m in re.finditer(r"<img\b[^>]*>", md, re.I):
        if not re.search(r'\balt\s*=\s*"([^"]{2,}|)"', m.group()):  # alt="" marks a decorative image
            r.e(name, f"an image without alt text: {m.group()[:80]}")
    for m in re.finditer(r"!\[([^\]]*)\]\(", md):
        if len(m.group(1)) < 2:
            r.e(name, "a Markdown image without alt text")
    alerts = re.findall(r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]", md, re.M)
    if len(alerts) > ALERTS:
        r.e(name, f"{len(alerts)} alerts: keep {ALERTS} or fewer, or none of them stands out")
    if re.search(r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]", top, re.M):
        r.e(name, "an alert in the lead: the first thing read is what the tool does, not a warning")
    total = words(visible(md))
    r.facts[name]["visible_words"] = total
    r.facts[name]["sections"] = len(secs)
    lo, hi = SECTIONS[audience]
    if not lo <= len(secs) <= hi:
        r.e(name, f"{len(secs)} sections (## headings); a README for a {audience} audience has {lo} to {hi}. Merge, cut, or move parts to docs/")
    if repo is not None:
        check_links(r, name, md, repo)
    if total > WORDS[audience] * scale:
        r.e(name, f"{total} words in plain sight; a {audience} README keeps to {WORDS[audience]}. Put reference parts in <details> or docs/, and cut what repeats")
    lead = lead_of(top)
    lw = words(visible(lead))
    r.facts[name]["lead_words"] = lw
    lmin, lmax = ROLES["lead"]["words"]
    lmax = round(lmax * scale)
    if not lmin <= lw <= lmax:
        r.e(name, f"the lead (the text under the title, before the first ##) has {lw} words; write {lmin} to {lmax}: what it is, for whom, what they get")
    if lead and not re.match(r"^\s*(\*\*|<b>)", lead):
        r.w(name, "the lead starts without a bold first sentence: open with **what it is, in one sentence.**")
    navs = re.findall(r'href="#([\w\-]+)"|\]\(#([\w\-]+)\)', md)
    anchors = {slug(h) for h, _ in secs} | set(re.findall(r'<a (?:name|id)="([^"]+)"', md))
    for a, b in navs:
        if (a or b) not in anchors:
            r.e(name, f"the link #{a or b} goes nowhere: no heading makes that anchor")
    by_heading = {}
    by_name = {norm(s.get("heading", "")): s for s in plan_sections}
    for i, (heading, body) in enumerate(secs):
        plan = by_name.get(norm(heading)) if name == "README.md" else (plan_sections[i] if i < len(plan_sections) else None)
        role = plan.get("role") if plan else None
        if plan is None and name == "README.md":
            r.e(f"{name} § {heading}", "this section is not in the plan: add it with its role, or remove it")
        where = f"{name} § {heading}"
        by_heading[heading] = body
        if emoji(heading):
            r.w(where, "an emoji in the heading: headings are words, the pictures carry the colour")
        if role not in ROLES:
            continue
        rule = ROLES[role]
        # a FAQ or a reference lives in <details> by design: its words are counted open
        v = visible(re.sub(r"</?(details|summary)\b[^>]*>", " ", body, flags=re.I)) if role in ("faq", "reference") else visible(body)
        n = words(v)
        r.facts[name].setdefault("section_words", []).append(n)
        if n < rule["words"][0]:
            r.w(where, f"{n} words; the {role} role has {rule['words'][0]} or more")
        if n > rule["words"][1] * scale:
            moved = plan.get("docs")
            if moved:
                r.e(where, f"{n} words; the {role} role keeps to {rule['words'][1]}. Move the detail to {moved} and keep the summary here")
            else:
                r.e(where, f"{n} words; the {role} role keeps to {rule['words'][1]}. Move the detail to a file in docs/ (name it in the plan as \"docs\") and link it")
        if plan.get("docs") and repo is not None and not (repo / plan["docs"]).exists():
            r.e(where, f"the plan sends the detail of this section to {plan['docs']}, which does not exist: write it from the README's current text")
        if plan.get("docs") and not re.search(r"\]\(\.?/?" + re.escape(plan["docs"]) + r"[)#]|href=\"\.?/?" + re.escape(plan["docs"]), body):
            r.e(where, f"the plan sends the detail of this section to {plan['docs']}, and the section does not link it")
        found = re.findall(r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]", body, re.M)
        if len(found) > 1:
            r.e(where, f"{len(found)} alerts in one section: one at most")
        for a in found:
            if a not in rule["alerts"]:
                ok = ", ".join(rule["alerts"]) or "none"
                r.e(where, f"a [!{a}] alert where the {role} role takes {ok}. NOTE: worth knowing. TIP: a better way. IMPORTANT: needed to succeed. WARNING: can break. CAUTION: can lose data")
        tables = [t for t in re.findall(r"((?:^\|.*\|[ \t]*\n?)+)", strip_code(re.sub(r"<details\b.*?</details>", "", body, flags=re.S | re.I)), re.M)]
        for t in tables:
            rows = [l for l in t.strip().splitlines() if not re.fullmatch(r"\|?[\s:|-]+\|?", l.strip())]
            cols = rows[0].strip().strip("|").count("|") + 1 if rows else 0
            if not rule["table"]:
                r.e(where, f"a table in the {role} role: tables are for comparisons, results, options and requirements; say it as a list or a picture")
            if cols > TABLE_COLUMNS:
                r.w(where, f"a table of {cols} columns: {TABLE_COLUMNS} at most, or it scrolls sideways on a phone")
            if len(rows) - 1 > TABLE_ROWS:
                r.w(where, f"a table of {len(rows) - 1} rows in plain sight: put it in <details> or docs/ past {TABLE_ROWS}")
        outside = re.sub(r"<details\b.*?</details>", "", strip_code(body), flags=re.S | re.I)
        outside = re.sub(r"^>\s?", "", outside, flags=re.M)  # lists inside an alert are lists
        for block in re.split(r"\n\s*\n", outside):
            items = re.findall(r"^\s*(?:[-*+]|\d+\.)\s", block, re.M)
            if len(items) > LIST_ITEMS:
                r.w(where, f"a list of {len(items)} items in plain sight: {LIST_ITEMS} at most, the rest in <details>")
            for item in (re.split(r"^\s*(?:[-*+]|\d+\.)\s", block, flags=re.M) if items else [block]):
                bolds = re.findall(r"\*\*([^*]+)\*\*|<b>(.*?)</b>", item)
                if len(bolds) > 1 and not re.match(r"^\s*[|<]", item):
                    r.w(where, f"{len(bolds)} bold runs in one paragraph or item: one at most, as its lead-in")
                for a, b in bolds:
                    seen = re.sub(r"<[^>]+>", "", a or b)  # the words a reader sees, not the link's address
                    if words(seen) > BOLD_WORDS:
                        r.w(where, f"bold run of {words(seen)} words (\"{seen[:40]}...\"): bold is a lead-in of {BOLD_WORDS} words or fewer")
            if not items and not block.strip().startswith(("|", "<", ">", "#")) and words(visible(block)) > PARAGRAPH_WORDS:
                r.w(where, f"a paragraph of {words(visible(block))} words: {PARAGRAPH_WORDS} at most, break it or make it a list")
        italics = len(re.findall(r"(?<![*\w])\*(?!\*)[^*\n]+\*(?!\*)|(?<![_\w])_(?!_)[^_\n]+_(?!_)|<i>|<em>", outside))
        if italics > ITALICS:
            r.w(where, f"{italics} italic runs: {ITALICS} per section at most, for a term on first use or a title")
        if role == "features":
            items = re.findall(r"^\s*[-*+]\s+(.*)$", outside, re.M)
            if items and sum(1 for i in items if re.match(r"(\*\*|<b>)", i)) < len(items):
                r.w(where, "feature items without a bold lead-in: start each with **what they get.**")
            if items and not FEATURE_ITEMS[0] <= len(items) <= FEATURE_ITEMS[1]:
                r.w(where, f"{len(items)} feature items: {FEATURE_ITEMS[0]} to {FEATURE_ITEMS[1]}, the ones a reader would repeat")
        if role == "how":
            steps = re.findall(r"^\s*\d+\.\s", outside, re.M)
            if not steps and plan.get("picture") is None:
                r.w(where, f"how it works without numbered steps or a picture: give it {HOW_STEPS[0]} to {HOW_STEPS[1]} numbered steps")
            elif steps and not HOW_STEPS[0] <= len(steps) <= HOW_STEPS[1]:
                r.w(where, f"{len(steps)} numbered steps: {HOW_STEPS[0]} to {HOW_STEPS[1]}, the rest in docs/")
        if role == "faq" and re.search(r"^###\s", body, re.M):
            r.w(where, "FAQ questions as ### headings: put each in <details><summary><b>question</b></summary>, so the list reads at a glance")
        if role == "install":
            first = re.search(r"^(```|~~~)|<details", body, re.M | re.I)
            if first and first.group().lower().startswith("<details"):
                r.e(where, "the first install path is hidden in <details>: the shortest path is in plain sight, the others go in <details>")
    return secs


def picture_refs(body):
    """The section scene a section shows: (dark file, light file, alt)."""
    pic = re.search(r'<picture>\s*<source[^>]*srcset="([^"]+)"[^>]*>\s*(<img[^>]*>)', body, re.S)
    if pic:
        src, alt = re.search(r'src="([^"]+)"', pic.group(2)), re.search(r'alt="([^"]*)"', pic.group(2))
        return pic.group(1), src.group(1) if src else "", alt.group(1) if alt else ""
    img = re.search(r'<img[^>]*src="([^"]+\.svg)"', body)
    return (None, img.group(1), "") if img else None


def check_assets(r, repo, plan):
    """Every data-asset in the pictures comes from the family the plan chose for its category, in its variant."""
    import assets as lib
    chosen = plan.get("assets") or {}
    for cat, c in chosen.items():
        f = lib.family(c.get("family", ""))
        if cat not in lib.CATEGORIES or not f or f["category"] != cat:
            r.e(PLAN, f'assets.{cat}: {c.get("family")!r} is not a {cat} family: see `assets.py styles {cat}`')
        elif len((c.get("why") or "").split()) < 6:
            r.e(PLAN, f"assets.{cat}: say why {c['family']} fits this repository, in a sentence (the mark's weight, corners, fill)")
    seen = {}
    for src in sorted(repo.glob("assets/**/*.src.svg")):
        for ref in re.findall(r'data-asset="([^"]+)"', src.read_text(encoding="utf-8")):
            prefix, _, name = ref.partition(":")
            f = lib.family(prefix)
            where = src.relative_to(repo).as_posix()
            if not f:
                r.e(where, f"data-asset {ref!r} names no family in the library")
                continue
            c = chosen.get(f["category"])
            if not c:
                r.e(where, f"uses {f['category']} ({ref}) and the plan chose no {f['category']} family: `assets.py choose` one first")
            elif c["family"] != prefix:
                r.e(where, f"uses {ref} from {prefix}, and the plan chose {c['family']} for {f['category']}: one family per category keeps one look. "
                           f"Take it from {c['family']} (`assets.py search`)")
            elif c.get("variant") and not re.search(f["variants"].get(c["variant"], ""), name):
                r.e(where, f"{ref} is not in the {c['variant']} variant the plan chose for {prefix}")
            if prefix not in seen:
                seen[prefix] = set(lib.names(prefix))
            if name not in seen[prefix]:
                r.e(where, f"{prefix} has no icon named {name!r}")


def check_repo(repo):
    r = Report()
    pf = repo / PLAN
    if not pf.exists():
        r.e(PLAN, "there is no plan: run `readme.py rules`, then write the plan before the README")
        return r
    try:
        plan = json.loads(pf.read_text(encoding="utf-8"))
    except ValueError as x:
        r.e(PLAN, f"not valid JSON: {x}")
        return r
    audience = plan.get("audience")
    if audience not in AUDIENCES:
        r.e(PLAN, f'"audience" is "general" or "technical", not {audience!r}')
        return r
    if not plan.get("audience_confirmed"):
        r.e(PLAN, '"audience_confirmed" is not true: ask the user whether the README is for a general or a technical audience, then set it')
    backdrop = plan.get("backdrop")
    if backdrop is None:
        r.e(PLAN, '"backdrop" is missing: ask the user whether the pictures have a background, still or moving, and which pattern '
                  '(readme.py survey proposes one), then write "none" or "<kind> <motion>" (kit.py backdrop)')
    elif backdrop != "none" and (len(str(backdrop).split()) != 2 or str(backdrop).split()[0] not in list(kit.BACKDROPS) + ["custom"]
                                 or str(backdrop).split()[1] not in kit.MOTIONS):
        r.e(PLAN, f'"backdrop" is "none" or "<kind> <motion>" with a kind of {", ".join(list(kit.BACKDROPS) + ["custom"])} and a motion of '
                  f'{", ".join(kit.MOTIONS)}, not {backdrop!r}')
    for x in plan.get("unfinished", []):
        if x.get("decision") not in ("keep", "drop", "not-a-feature"):
            r.e(PLAN, f"unfinished item {x.get('item')!r} has no decision: ask the user, keep or drop")
    sections = plan.get("sections", [])
    roles = [s.get("role") for s in sections]
    for s in sections:
        if s.get("role") not in ROLES or s.get("role") == "lead":
            r.e(PLAN, f"section {s.get('heading')!r} has role {s.get('role')!r}: use one of {', '.join(k for k in ROLES if k != 'lead')} (the lead is the top block)")
    for need in REQUIRED[audience]:
        if need != "lead" and need not in roles:
            r.e(PLAN, f"no {need} section: a {audience} README has one")
    for group in ONE_OF[audience]:
        if not any(g in roles for g in group):
            r.e(PLAN, f"none of {', '.join(group)}: a {audience} README shows the reader what it does or how to use it")
    pics = [s for s in sections if s.get("picture")]
    lo, hi = PICTURES[audience]
    if not lo <= len(pics) <= hi:
        r.e(PLAN, f"{len(pics)} section scenes; a {audience} README has {lo} to {hi}, on the sections a picture explains best")
    for s in sections:
        rule = ROLES.get(s.get("role"), {}).get("picture", {}).get(audience)
        if rule == "required" and not s.get("picture"):
            r.e(PLAN, f"section {s.get('heading')!r} ({s['role']}) needs a scene for a {audience} audience")
        if rule == "none" and s.get("picture"):
            r.e(PLAN, f"section {s.get('heading')!r} ({s['role']}) takes no scene: it is read, not looked at")
    captures = [s for s in pics if s["picture"].get("type") == "capture"]
    if captures and not plan.get("captures_agreed"):
        r.e(PLAN, "a scene holds a real screenshot and the user has not agreed: ask, then set \"captures_agreed\": true")
    if len(captures) > 1:
        r.w(PLAN, f"{len(captures)} scenes hold screenshots: keep the README drawn, one screenshot at most, where a drawing would explain less")

    # ---- the pictures: they build, each shows something of its own, the hero apart
    hero = repo / (plan.get("hero") or {}).get("file", "assets/hero.src.svg")
    sigs = {}
    if hero.exists():
        ws, sh = stage_signature(hero)
        sigs["the hero"] = (ws, sh, set(map(str.lower, (plan.get("hero") or {}).get("shows", []))))
    else:
        r.e(PLAN, f"no hero at {hero.relative_to(repo).as_posix()}: draw it first (references/hero.md)")
    for s in pics:
        p = s["picture"]
        where = f"scene {p.get('file')}"
        src = repo / p.get("file", "")
        if not p.get("claim") or not p.get("shows"):
            r.e(where, 'a scene says in the plan what it makes the reader understand ("claim", one sentence) and what it draws ("shows", the objects)')
        if not src.exists() or not src.name.endswith(".src.svg"):
            r.e(where, "the source does not exist: scenes live in assets/readme/<name>.src.svg")
            continue
        raw = src.read_text(encoding="utf-8")
        try:
            palette, body = svgcheck.read_source(raw)
            res = svgcheck.check(ET.fromstring(body), palette, "section")
            if res.errors:
                r.e(where, f"{len(res.errors)} error(s) from the build: {res.errors[0]}")
        except Exception as x:  # noqa: BLE001
            r.e(where, f"does not parse: {x}")
        for cmd in invented_commands(repo, raw):
            r.e(where, f"shows the command `{cmd}`, which appears nowhere in the repository's Markdown: draw only what the tool really does")
        ws, sh = stage_signature(src)
        sigs[where] = (ws, sh, set(map(str.lower, p.get("shows", []))))
    names = list(sigs)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            same = max(jaccard(sigs[a][0], sigs[b][0]), jaccard(sigs[a][2], sigs[b][2]))
            if same >= SAME:
                r.e(f"{a} and {b}", f"show {same:.0%} the same things: each picture explains its own part. Change what one of them draws, not its colours")
            elif len(sigs[a][1]) >= 3 and jaccard(sigs[a][1], sigs[b][1]) >= 0.8:
                r.w(f"{a} and {b}", "are laid out with the same large shapes: give each scene its own composition")

    for src in sorted(set(repo.glob("assets/**/readme/*.src.svg")) | set(repo.glob("assets/**/hero.src.svg"))):
        for name in stale(src):
            r.e(src.relative_to(repo).as_posix(), f"{name} is missing or was built from another version of its source: build it")
        check_backdrop(r, src.relative_to(repo).as_posix(), src.read_text(encoding="utf-8"), plan.get("backdrop"))
    hero = repo / "assets/hero.src.svg"
    if hero.exists():
        want = hashlib.sha256(source_bytes(hero)).hexdigest()[:16]
        for social in (hero.parent / "social-preview" / f"social-preview-{t}.{x}" for t in ("dark", "light") for x in ("svg", "png")):
            where = f"assets/social-preview/{social.name}"
            if not social.exists():
                r.w(where, "is missing: build the hero (the PNG needs a Chromium-family browser on this machine), then upload one PNG in Settings > General > Social preview")
            elif social_stamp(social) != want:
                r.e(where, "was built from another version of the hero: build the hero again and upload the new PNG")

    # ---- assets from the library: one family per category, the one the plan names, and names that exist
    check_assets(r, repo, plan)

    # ---- the README and its translations
    md_files = [repo / "README.md"] + sorted(p for p in repo.glob("README.*.md"))
    shapes = {}
    for f in md_files:
        if not f.exists():
            r.e(f.name, "missing")
            continue
        md = f.read_text(encoding="utf-8")
        for x in plan.get("unfinished", []):
            if x.get("decision") == "drop" and x.get("match") and re.search(re.escape(x["match"]), md, re.I):
                r.e(f.name, f"mentions {x['match']!r}, which the user chose to leave out as unfinished")
        secs = check_markdown(r, f.name, md, sections, audience, repo, 1.0 if f.name == "README.md" else TRANSLATION)
        if f.name == "README.md" and len(secs) != len(sections):
            r.e(f.name, f"{len(secs)} sections and the plan has {len(sections)}: the plan lists every ## in order")
        shown = []
        for i, (heading, body) in enumerate(secs):
            refs = picture_refs(body)
            planned = {norm(s.get("heading", "")): s for s in sections}.get(norm(heading)) if f.name == "README.md" else (sections[i] if i < len(sections) else None)
            p = (planned or {}).get("picture")
            if p:
                stem = p.get("file", "").replace(".src.svg", "")
                if not refs or not (refs[0] or "").endswith(Path(stem).name + "-dark.svg") or not refs[1].endswith(Path(stem).name + "-light.svg"):
                    r.e(f"{f.name} § {heading}", f'the scene is not shown as the plan says: <picture><source media="(prefers-color-scheme: dark)" srcset="{stem}-dark.svg"><img src="{stem}-light.svg" alt="..." width="100%"></picture> right under the heading')
                elif len(refs[2]) < 20:
                    r.e(f"{f.name} § {heading}", "the scene's alt text is short: say what the picture shows, for someone who cannot see it")
                if refs:
                    head = body.strip()[:400]
                    if "<picture" not in head and "<img" not in head:
                        r.w(f"{f.name} § {heading}", "the scene is not the first thing in the section: put it right under the heading, the text then says what the picture showed")
            if refs:
                shown.append(Path(refs[1]).name)
        shapes[f.name] = (len(secs), shown, len(re.findall(r"^>\s*\[!", md, re.M)))
    base = shapes.get("README.md")
    for name, sh in shapes.items():
        if base and name != "README.md" and sh != base:
            r.e(name, f"does not match README.md: {sh[0]} sections, {len(sh[1])} pictures, {sh[2]} alerts against {base[0]}, {len(base[1])}, {base[2]}. A translation has the same parts in the same order")

    # ---- the judges: every scene and the whole README were read cold, and passed
    jf = repo / JUDGES
    verdicts = json.loads(jf.read_text(encoding="utf-8")) if jf.exists() else {}
    want = judge_items(repo, plan)
    if not jf.exists():
        r.e(JUDGES, "no judges yet: run `readme.py judge`, give each packet to a fresh agent, and record the verdicts")
    else:
        for item in want:
            v = verdicts.get(item["id"])
            if not v:
                r.e(JUDGES, f"{item['id']} has no verdict")
            elif v.get("sha") != item["sha"]:
                r.e(JUDGES, f"{item['id']} was judged on an older version: judge it again")
            elif not v.get("pass"):
                r.e(JUDGES, f"{item['id']} failed its cold read: {v.get('why', '')[:160].rstrip('.')}. Change the picture or the text, then judge again")
    r.facts["plan"] = {"audience": audience, "sections": len(sections), "scenes": len(pics)}
    return r


# ---- judges
def icons_of(src):
    """(what it means, its box on the canvas) for each icon a source declares with data-icon."""
    if not src.exists():
        return []
    try:
        palette, body = svgcheck.read_source(src.read_text(encoding="utf-8"))
        root = ET.fromstring(body)
        kind = svgcheck.kind_of(src)
        svgcheck.W, svgcheck.H = svgcheck.CANVAS[kind]
        hero = svgcheck.Hero(root, palette, kind)
    except (Exception, SystemExit):  # noqa: BLE001
        return []
    return [(e.get("data-icon").strip(), hero.box[e]) for e in root.iter() if e.get("data-icon") is not None and hero.box.get(e)]


def judge_items(repo, plan):
    """What the judges read, each with a fingerprint of the file it was judged on."""
    items = []
    md = (repo / "README.md").read_text(encoding="utf-8") if (repo / "README.md").exists() else ""
    _, secs = split(md)
    for i, s in enumerate(plan.get("sections", [])):
        p = s.get("picture")
        if not p:
            continue
        dark = repo / p.get("file", "").replace(".src.svg", "-dark.svg")
        source = repo / p.get("file", "")
        pic = source_bytes(source)  # judged on its source: a rebuild of the same source keeps its verdict
        body = next((b for h, b in secs if norm(h) == norm(s.get("heading", ""))), "")
        items.append({"id": f"picture:{Path(p.get('file', '')).name}", "kind": "picture", "sha": sha(pic), "file": str(dark), "claim": p.get("claim", ""),
                      "heading": s.get("heading")})
        items.append({"id": f"section:{s.get('heading')}", "kind": "section", "sha": sha(pic, body), "file": str(dark), "text": body,
                      "claim": p.get("claim", ""), "heading": s.get("heading")})
    # every icon that says what it means is read cold too, at the size a reader sees it
    sources = [repo / s["picture"]["file"] for s in plan.get("sections", []) if s.get("picture")]
    if (repo / "assets/hero.src.svg").exists():
        sources.insert(0, repo / "assets/hero.src.svg")
    for src in sources:
        for k, (means, box) in enumerate(icons_of(src), 1):
            items.append({"id": f"icon:{src.name}#{k}", "kind": "icon", "sha": sha(source_bytes(src), str(k)), "claim": means,
                          "file": str(src.with_name(src.name.replace(".src.svg", "-dark.svg"))), "box": box})
    hero = repo / "assets/hero-dark.svg"
    scenes = [source_bytes(p) for p in sorted(repo.glob("assets/**/*.src.svg"))]
    items.append({"id": "readme", "kind": "readme", "sha": sha(md, *scenes), "file": str(repo / "README.md"), "hero": str(hero),
                  "claim": plan.get("sentence", "")})
    return items


PROMPTS = {
    "blind": ("You are shown pictures from a software project's README, one per section, with nothing else: no headings, no text, "
              "no repository. They are the PNG files in {folder}, named scene-1.png, scene-2.png and so on. Each one shows eight moments "
              "of an animation and, last and larger, its finished frame. For each picture answer in three short lines: 1) what that "
              "section of the README is about, 2) what happens in it, moment by moment, 3) what you could not make out. Say only what "
              "the pictures show; do not guess from outside knowledge, and do not open any other file. When the folder also has "
              "icons.png, it shows small icons cut out of those pictures at the size a reader sees them, each with a number: for each "
              "number say what it depicts, what it would mean on a button or a label in a software tool, and whether you are sure. Reply as JSON: "
              '{{"scenes": [{{"scene": 1, "about": "...", "happens": "...", "unclear": "..."}}], '
              '"icons": [{{"n": 1, "depicts": "...", "means": "...", "sure": true}}]}}'),
    "readme": ("You are a newcomer reading a project's README from top to bottom: {folder}/README.md. Its pictures are the PNG files "
               "next to it. Open nothing outside that folder. For each ## section answer: what it tells you, whether its picture and its "
               "text say the same thing, and what was unclear or used words you did not know. Then: what the project does and for "
               "whom, in one sentence, and how you would start using it. Reply as JSON: "
               '{{"sections": [{{"heading": "...", "tells": "...", "picture_matches": true, "unclear": "..."}}], "project": "...", "start": "..."}}'),
    "grade": ("Grade cold reads. {claims} lists, for each id, what the author meant. The judges' answers follow; an icon:* id is "
              "answered in the blind judge's icons under the number packets.json gives it, and fails when the judge was not sure. For each id reply "
              'pass when the reader understood the same thing in substance, even in other words, and fail when they missed it, got it '
              'wrong or were unsure. Reply as JSON {{"<id>": {{"pass": true, "why": "..."}}, ...}}.'),
}


def strip_text_block(svg):
    """The scene without its eyebrow, title and sub: the picture has to speak for itself."""
    ET.register_namespace("", svgcheck.SVG)
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    root = ET.fromstring(svg)
    parent = {c: p for p in root.iter() for c in p}
    for el in [e for e in root.iter() if e.get("id") in ("eyebrow", "title", "sub", "name", "tagline", "about")]:
        parent[el].remove(el)
    return ET.tostring(root, encoding="unicode")


def strip_of(svg, kind, work, name):
    """A page with eight moments of the loop and the finished frame, large."""
    import build  # noqa: E402  (freeze)
    try:
        cycle = svgcheck.check(ET.fromstring(svg), {}, kind).facts.get("cycle_seconds") or 8
    except Exception:  # noqa: BLE001
        cycle = 8
    frames = []
    for i, t in enumerate([cycle * k / 8 for k in range(8)]):
        f = work / f"{name}-{i}.svg"
        f.write_text(build.freeze(svg, t), encoding="utf-8")
        frames.append(f.name)
    still = work / f"{name}-still.svg"
    still.write_text(svg.replace("</svg>", "<style>*{animation:none!important}</style></svg>"), encoding="utf-8")
    page = work / f"{name}.html"
    page.write_text('<!doctype html><meta charset=utf-8><style>body{margin:0;background:#0d1117;padding:12px}.g{display:grid;'
                    'grid-template-columns:1fr 1fr;gap:8px;width:1296px}img{width:100%;display:block}</style><div class=g>'
                    + "".join(f'<img src="{f}">' for f in frames) + f'</div><img src="{still.name}" style="width:1296px;margin-top:10px">',
                    encoding="utf-8")
    return page, still


def judge(repo):
    import build  # noqa: E402  (its browser finder and screenshot)
    plan = json.loads((repo / PLAN).read_text(encoding="utf-8"))
    items = judge_items(repo, plan)
    if not build.find_browsers():
        sys.exit("error: the judges look at pictures, and no Chrome, Chromium or Edge was found to take them (set JANO_BROWSER)")
    folder = Path(tempfile.mkdtemp(prefix="jano-judge-"))
    work, blind, reader = folder / "work", folder / "blind", folder / "reader"
    for d in (work, blind, reader):
        d.mkdir()
    shots, n, names = [], 0, {}
    for it in items:
        if it["kind"] != "picture":
            continue
        n += 1
        svg = Path(it["file"]).read_text(encoding="utf-8")
        page, _ = strip_of(strip_text_block(svg), "section", work, f"blind-{n}")
        shots.append((page, blind / f"scene-{n}.png", 1520))
        whole = work / f"whole-{n}.html"
        _, still = strip_of(svg, "section", work, f"whole-{n}")
        whole.write_text(f'<!doctype html><body style="margin:0;background:#0d1117"><img src="{still.name}" width="1280">', encoding="utf-8")
        shots.append((whole, reader / f"scene-{n}.png", 470))
        names[Path(it["file"]).relative_to(repo).as_posix()] = f"scene-{n}.png"
        it["blind_png"] = f"scene-{n}.png"
    hero = repo / "assets/hero-dark.svg"
    if hero.exists():
        page = work / "hero.html"
        still = work / "hero-still.svg"
        still.write_text(hero.read_text(encoding="utf-8").replace("</svg>", "<style>*{animation:none!important}</style></svg>"), encoding="utf-8")
        page.write_text(f'<!doctype html><body style="margin:0;background:#0d1117"><img src="{still.name}" width="1280">', encoding="utf-8")
        shots.append((page, reader / "hero.png", 660))
        names["assets/hero-dark.svg"] = "hero.png"
    md = (repo / "README.md").read_text(encoding="utf-8")
    # every other picture the README shows (a showroom, a diagram) is seen too, as the reader would see it
    for k, src in enumerate(dict.fromkeys(re.findall(r'srcset="([^"]+\.svg)"', md)), 1):
        f = (repo / src).resolve()
        if src in names or not f.exists():
            continue
        page, still = work / f"other-{k}.html", work / f"other-{k}-still.svg"
        still.write_text(f.read_text(encoding="utf-8").replace("</svg>", "<style>*{animation:none!important}</style></svg>"), encoding="utf-8")
        page.write_text(f'<!doctype html><body style="margin:0;background:#0d1117"><img src="{still.name}" width="1280">', encoding="utf-8")
        shots.append((page, reader / f"picture-{k}.png", 660))
        names[src] = f"picture-{k}.png"
    # the icons, each cut out of its finished frame at the size a README shows it (65%)
    icons = [it for it in items if it["kind"] == "icon"]
    if icons:
        k, pad, cells = 838 / 1280, 6, []  # as a README shows it on an ordinary screen: the hardest case
        for i, it in enumerate(icons, 1):
            src = Path(it["file"])
            still = work / f"icon-{i}-still.svg"
            still.write_text(src.read_text(encoding="utf-8").replace("</svg>", "<style>*{animation:none!important}</style></svg>"), encoding="utf-8")
            x0, y0, x1, y1 = it["box"]
            w, h = (x1 - x0 + 2 * pad) * k, (y1 - y0 + 2 * pad) * k
            cells.append(f'<div class=c><b>{i}</b><div style="width:{w:.0f}px;height:{h:.0f}px;overflow:hidden;position:relative">'
                         f'<img src="{still.name}" style="position:absolute;left:{-(x0 - pad) * k:.0f}px;top:{-(y0 - pad) * k:.0f}px;width:{1280 * k:.0f}px"></div></div>')
            it["n"] = i
        page = work / "icons.html"
        page.write_text('<!doctype html><meta charset=utf-8><style>body{margin:0;padding:16px;background:#0d1117;color:#f0f6fc;font:16px system-ui}'
                        '.g{display:flex;flex-wrap:wrap;gap:28px;width:1200px}.c{display:flex;align-items:center;gap:10px}</style><div class=g>'
                        + "".join(cells) + "</div>", encoding="utf-8")
        shots.append((page, blind / "icons.png", 120 + 70 * (len(icons) // 8 + 1)))
    if not build.take_pictures(shots):
        sys.exit(f"error: the pictures for the judges could not be taken; open the pages in {work} with a browser tool")

    def swap(m):  # a <picture> becomes the PNG the reader judge sees, matched by its whole path
        block = m.group(0)
        alt = re.search(r'alt="([^"]*)"', block)
        src = re.search(r'srcset="([^"]+)"', block)
        png = names.get(src.group(1)) if src else None
        return f'<img src="{png}" alt="{alt.group(1) if alt else ""}" width="100%">' if png else block

    md = re.sub(r"<picture>.*?</picture>", swap, md, flags=re.S)
    (reader / "README.md").write_text(md, encoding="utf-8")
    claims = {it["id"]: it["claim"] for it in items}
    (folder / "claims.json").write_text(json.dumps(claims, indent=2, ensure_ascii=False), encoding="utf-8")
    packets = {"blind": {"folder": str(blind), "prompt": PROMPTS["blind"].format(folder=blind),
                         "ids": {it["id"]: it["blind_png"] for it in items if it["kind"] == "picture"},
                         "icons": {it["id"]: it["n"] for it in icons}},
               "reader": {"folder": str(reader), "prompt": PROMPTS["readme"].format(folder=reader),
                          "ids": [it["id"] for it in items if it["kind"] in ("section", "readme")]},
               "grade": {"prompt": PROMPTS["grade"].format(claims=folder / "claims.json")},
               "sha": {it["id"]: it["sha"] for it in items}}
    (folder / "packets.json").write_text(json.dumps(packets, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"packets {folder / 'packets.json'}")
    print(f"blind judge: {len(packets['blind']['ids'])} scene(s) without their text and {len(icons)} icon(s) at README size, in {blind}")
    print(f"reader judge: the README with its pictures as PNGs, in {reader}")
    print("1. give the blind prompt to one fresh agent, and the reader prompt to another; neither has seen the repository, the plan or this skill")
    print("2. give the grade prompt, claims.json and both answers to a third")
    print(f'3. record in {JUDGES}, per id, with the sha from packets.json: {{"<id>": {{"sha": "...", "pass": true, "answer": "...", "why": "..."}}}}')


def rules():
    print("README rules (readme.py check measures each one)\n")
    print("audience  sections  words in sight  section scenes")
    for a in AUDIENCES:
        print(f"{a:9} {SECTIONS[a][0]}-{SECTIONS[a][1]:<7} {WORDS[a]:<14} {PICTURES[a][0]}-{PICTURES[a][1]}")
    print("\nrole          words    scene general/technical   alerts allowed              table  what it holds")
    for k, v in ROLES.items():
        print(f"{k:13} {v['words'][0]:>3}-{v['words'][1]:<4} {v['picture']['general']:>9}/{v['picture']['technical']:<9}       "
              f"{','.join(v['alerts']) or '-':27} {'yes' if v['table'] else 'no':6} {v['what']}")
    print(f"\nrequired: lead, install, license; general also one of demo/features; technical one of demo/features/how and one of use/reference")
    print(f"Markdown: one H1; ## and ### only; code blocks name their language; {ALERTS} alerts at most, one per section, none in the lead;")
    print(f"  bold: one lead-in per paragraph or item, {BOLD_WORDS} words at most; italics {ITALICS} per section; paragraphs {PARAGRAPH_WORDS} words;")
    print(f"  lists {LIST_ITEMS} items in sight; tables {TABLE_COLUMNS} columns and {TABLE_ROWS} rows in sight, only where the role allows;")
    print(f"  {BADGES} badges at most; every image has alt text; no style=, color= or <font> (GitHub removes them);")
    print("  <details><summary><b>...</b></summary> for FAQ entries, other install paths, long reference; <kbd> for keys.")
    print("a section over its words sends the detail to docs/<file>.md and links it; the plan names the file in \"docs\".")
    print(f"two pictures that share {SAME:.0%} of what they show are the same picture: the build refuses it.")
    print("""
plan.json:
{
  "audience": "general" | "technical", "audience_confirmed": true,
  "sentence": "who uses it, when, and what they get, in plain words",
  "language": "en", "translations": ["README.es.md"],
  "unfinished": [{"item": "...", "source": "file:line", "match": "words to look for", "decision": "keep" | "drop" | "not-a-feature"}],
  "captures_agreed": false,
  "hero": {"file": "assets/hero.src.svg" (or "assets/hero-dark.svg" when only the built files exist), "shows": ["the objects the hero draws"]},
  "sections": [
    {"heading": "What you get", "role": "features", "docs": null,
     "picture": {"file": "assets/readme/features.src.svg", "type": "drawn" | "capture",
                 "claim": "what the reader understands from the picture alone", "shows": ["the objects it draws"]}}
  ]
}""")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    cmd = args[0]
    if cmd == "rules":
        return rules()
    if len(args) < 2:
        sys.exit(__doc__)
    repo = Path(args[1]).resolve()
    if cmd == "survey":
        print(json.dumps(survey(repo), indent=2, ensure_ascii=False))
    elif cmd == "judge":
        judge(repo)
    elif cmd == "check":
        r = check_repo(repo)
        if "--json" in sys.argv:
            print(json.dumps({"errors": r.errors, "warnings": r.warns, "measured": r.facts}, indent=2, ensure_ascii=False))
        else:
            print("\n".join(["error: " + e for e in r.errors] + ["warning: " + w for w in r.warns]) or "checks passed")
            print("measured: " + json.dumps(r.facts, ensure_ascii=False))
        sys.exit(1 if r.errors else 0)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
