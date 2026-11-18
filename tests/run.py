# /// script
# requires-python = ">=3.9"
# dependencies = ["fonttools", "brotli"]
# ///
"""Tests for skills/jano/scripts/build.py, check.py and .github/scripts/check-pr.js.

    uv run tests/run.py
"""
import json, re, shutil, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "skills/jano/scripts/build.py"
CHECK = ROOT / "skills/jano/scripts/check.py"
FIXTURE = (ROOT / "tests/fixture/assets/hero.src.svg").read_text(encoding="utf-8")
failed = []


def build(source, pictures=False):
    """Builds `source` in a fresh folder. Returns (exit code, output, folder)."""
    folder = Path(tempfile.mkdtemp()) / "repo" / "assets"
    folder.mkdir(parents=True)
    (folder / "hero.src.svg").write_text(source, encoding="utf-8")
    cmd = [sys.executable, str(BUILD), str(folder / "hero.src.svg")] + ([] if pictures else ["--no-pictures"])
    run = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return run.returncode, run.stdout + run.stderr, folder


def swap(old, new, source=FIXTURE):
    """The fixture with one piece changed. Fails loudly when the piece is not there, so a test cannot pass by accident."""
    assert old in source, f"the fixture no longer contains: {old}"
    return source.replace(old, new)


def test(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name)
    if not ok:
        failed.append(name)
        if detail:
            print("      " + detail.strip().replace("\n", "\n      "))


# ---- the fixture builds, in both themes
code, out, folder = build(FIXTURE)
test("fixture builds without errors", code == 0, out)
test("fixture builds without warnings", "checks passed" in out, out)
dark = (folder / "hero-dark.svg").read_text(encoding="utf-8") if code == 0 else ""
light = (folder / "hero-light.svg").read_text(encoding="utf-8") if code == 0 else ""
test("both themes are well-formed XML", bool(dark) and all(ET.fromstring(s) is not None for s in (dark, light)))
test("palette roles are replaced per theme", "$" not in re.sub(r"base64,[^)]+", "", dark) and "#0F1115" in dark and "#F0F5FB" in light)
test("fonts are embedded", dark.count("@font-face") == 3)
test("reduced motion rule is added", "prefers-reduced-motion" in dark)
test("no external file is referenced", not [u for u in re.findall(r"https?://[^\"')\s]+", dark) if "w3.org" not in u])

# ---- two repositories with the same folder name keep separate preview pages
other = build(FIXTURE)[1]
previews = [re.search(r"^preview (.+)$", o, re.M) for o in (out, other)]
test("each source gets its own preview page", all(previews) and previews[0].group(1) != previews[1].group(1), out + other)

# ---- moving text becomes outlines, still text stays text
test("text that travels is outlined", "first line" not in dark and "third line" not in dark and "<use" in dark)
test("text that stays still is kept", "still title" in dark)
test("text that only changes opacity is kept", "pulses, stays put" in dark)
test("nine moving text elements are reported", "9 moving text element(s)" in out, out)
test("the measured figures are printed", "measured: name 36 px · logo 48 px · tagline 52 px, 7 words" in out, out)
root = ET.fromstring(dark) if dark else None
uses = [u.get("href") for u in root.iter("{http://www.w3.org/2000/svg}use")] if root is not None else []
ids = {p.get("id") for p in root.iter("{http://www.w3.org/2000/svg}path")} if root is not None else set()
test("every outlined glyph has its shape", bool(uses) and all(u[1:] in ids for u in uses))
test("outlines use the font of each run", any(u.startswith("#gm") for u in uses) and any(u.startswith("#gs") for u in uses) and any(u.startswith("#gb") for u in uses))

# ---- a web address shown as text loads nothing, so it builds
code, out, _ = build(swap("pulses, stays put", "https://a.io/x"))
test("an address written as text is allowed", code == 0 and "external URL" not in out, out)

# ---- sources the build must refuse
def refused(name, source, expect):
    code, out, _ = build(source)
    test(name, code != 0 and expect in out, out)

refused("an animation that plays once is refused", swap("scroll 8s linear infinite", "scroll 8s linear"), "infinite")
refused("a script is refused", swap("</svg>", "<script>1</script></svg>"), "<script")
refused("an external image is refused", swap("</svg>", '<image href="https://example.com/a.png"/></svg>'), "<image")
refused("an external reference is refused", swap("</svg>", '<use href="https://example.com/a.svg#x"/></svg>'), "external URL")
refused("an unknown palette role is refused", swap('fill="$ink"', 'fill="$nope"'), "$nope")
refused("a different canvas is refused", swap("0 0 1280 640", "0 0 800 400"), "viewBox")
refused("a source without a palette is refused", re.sub(r"<!--palette.*?-->", "", FIXTURE, flags=re.S), "palette")
# the parts every hero has
refused("a hero without a marked name is refused", swap('<text id="name"', "<text"), 'id="name"')
refused("a hero without a marked stage is refused", swap('<g id="stage">', "<g>"), 'id="stage"')
refused("a name that moves is refused", swap('id="name" x="136" y="98" class="b"', 'id="name" x="136" y="98" class="b pulse"'), "the name is animated")
# where things land
refused("text that runs out of its box is refused", swap("pulses, stays put", "pulses and then stays where it was put"), "out of its box")
refused("text that runs off the canvas is refused", swap('id="about" x="72"', 'id="about" x="1000"'), "off the canvas")
refused("two lines of text on top of each other are refused", swap('id="about" x="72" y="306"', 'id="about" x="136" y="96"'), "overlap")
# loops that do not close
refused("a scroll that jumps back is refused", swap("translateY(-96px)", "translateY(-80px)"), "jumps back in plain sight")
refused("a parcel that jumps back in view is refused", swap("translateX(60px);opacity:0", "translateX(60px);opacity:1"), "jumps back in plain sight")
refused("dashes that do not come round are refused", swap("stroke-dashoffset:-24", "stroke-dashoffset:-20"), "dashes repeat every 24")
refused("an animated element with its own transform is refused", swap('<rect class="send"', '<rect transform="translate(2 2)" class="send"'), "its own transform attribute")
refused("animated geometry is refused", swap("50%{opacity:1}", "50%{opacity:1;width:9px}"), "geometry does not animate")
refused("flashing is refused", swap("pulse 2s ease-in-out", "pulse .2s ease-in-out"), "WCAG 2.3.1")

# a conveyor whose repeated content sits behind a <use> closes its loop too
belt = swap("</defs>", '<g id="row"><rect x="620" y="240" width="40" height="20" fill="$muted"/><rect x="620" y="336" width="40" height="20" fill="$muted"/></g></defs>')
belt = swap("</g></g>\n</g>", '</g><g class="scroll"><use href="#row"/></g></g>\n</g>', belt)
code, out, _ = build(belt)
test("content repeated inside a <use> counts as a repeat", code == 0 and "jumps back" not in out, out)

# ---- sources the build must warn about
def warned(name, source, expect):
    code, out, _ = build(source)
    test(name, code == 0 and "warning" in out and expect in out, out)

warned("small text is warned about", swap('font-size="14"', 'font-size="10"'), "font-size below 13")
warned("low contrast is warned about", swap("muted  #A3A8B0", "muted  #2A2F37"), "contrast")
code, out, _ = build(swap('class="m pulse" font-size="14"', 'class="m pulse" opacity="0" font-size="14"'))
test("text hidden at rest and shown by its animation is measured as shown", code == 0 and "contrast" not in out, out)
code, out, _ = build(swap('<rect x="600" y="72" width="200" height="484" rx="16" fill="$panel"/>', '<rect class="breathe" x="600" y="72" width="200" height="484" rx="16" fill="$ink"/>'))
test("a label is measured against the box behind it even when the box moves", "on $ink has contrast" in out, out)
warned("a positive delay is warned about", swap(".pulse{", ".pulse{animation-delay:1s;"), "animation-delay")
warned("text as large as the key phrase is warned about", swap('class="b" font-size="32"', 'class="b" font-size="56"'), "the tagline is the largest text")
warned("a name that shouts is warned about", swap('class="b" font-size="36"', 'class="b" font-size="120"'), "it signs the poster")
warned("a logo far from the name is warned about", swap('id="name" x="136"', 'id="name" x="700"'), "from the name")
warned("a small picture is warned about", swap('<g id="stage">', '<g id="stage" transform="translate(300 200) scale(.5)">'), "of the canvas; give it at least")
warned("text at the canvas edge is warned about", swap('id="about" x="72"', 'id="about" x="10"'), "from the canvas edge")
warned("text tight in its box is warned about", swap("pulses, stays put", "pulses, then stays here"), "from the side of its box")
warned("a sentence on the canvas is warned about", swap("pulses, stays put", "a b c d e f g h i j k"), "is a sentence of 11 words")
warned("text in a system font is warned about", swap('class="s" font-size="20"', 'font-size="20"'), "system font")
warned("motion too small to see is warned about", swap("scale(.8)", "scale(.99)"), "too small to read as motion")
warned("motion too fast to follow is warned about", swap("tick 12s linear", "tick .5s linear"), "too fast to follow")
warned("a scale without an origin is warned about", swap(";transform-box:fill-box;transform-origin:center", ""), "transform-origin")
warned("an opacity that pops is warned about", swap("0%,100%{opacity:.55}50%{opacity:1}", "0%{opacity:.55}100%{opacity:1}"), "pops when the loop restarts")
warned("a parcel left frozen when motion is off is warned about", swap(' opacity="0" width="28"', ' width="28"'), "with motion off it sits frozen")
warned("a travelling thing too small to see is warned about", swap('width="28" height="28" rx="6"', 'width="12" height="12" rx="6"').replace('<g class="scroll" ', "<g "), "the largest thing that travels")
warned("a faint connector is warned about", swap('stroke="$muted" stroke-width="2"', 'stroke="$panel" stroke-width="2"'), "it disappears at README width")
warned("a thin connector is warned about", swap('stroke="$muted" stroke-width="2"', 'stroke="$muted" stroke-width="1"'), "px thick")
warned("mostly small text is warned about", swap('font-size="16"', 'font-size="15"').replace('class="s" font-size="20"', 'class="s" font-size="15"'), "say less and say it larger")
# the parts of the poster
code, out, _ = build(re.sub(r'<g id="logo">.*?</g>\n', "", FIXTURE, flags=re.S))
test("a hero without a logo builds", code == 0 and "logo" not in out, out)
warned("a hero without a description is warned about", swap('<text id="about"', "<text"), 'id="about"')
code, out, _ = build(re.sub(r'<g id="facts">.*?</g>\n', "", FIXTURE, flags=re.S))
test("a hero without highlights builds clean", code == 0 and "checks passed" in out, out)
warned("too many figures are warned about", swap('<text x="352" y="400"', '<text x="72" y="470" class="b" font-size="32" fill="$ink">2</text><text x="212" y="470" class="b" font-size="32" fill="$ink">5</text><text x="352" y="400"'), "#facts shows 5 figures")
code, out, _ = build(re.sub(r'<g id="ticker">.*?</g></g></g>\n', "", FIXTURE, flags=re.S))
test("a hero without a strip builds clean", code == 0 and "checks passed" in out and "ticker" not in out, out)
code, out, folder = build(swap("<!--palette", "<!--brief\nsentence: a test hero <script>\n-->\n<!--palette"))
page = Path(re.search(r"^preview (.+)$", out, re.M).group(1)).read_text(encoding="utf-8") if code == 0 else ""
test("the brief is on the preview page and not in the outputs", "a test hero &lt;script&gt;" in page and "a test hero" not in (folder / "hero-dark.svg").read_text(encoding="utf-8"), out)
flagged = Path(tempfile.mkdtemp()) / "hero.src.svg"
flagged.write_text(swap("<!--palette", "<!--brief\nleft out: --permission-mode agent-default\n-->\n<!--palette"), encoding="utf-8")
run = subprocess.run([sys.executable, str(CHECK), str(flagged), "--json"], capture_output=True, text=True, encoding="utf-8")
test("a brief with -- in it is checked like any source", run.returncode == 0 and '"errors": []' in run.stdout, run.stdout + run.stderr)
options = Path(tempfile.mkdtemp())
(options / "a").mkdir()
(options / "a" / "hero.src.svg").write_text(FIXTURE, encoding="utf-8")
(options / "b").mkdir()  # letters the first option does not have: each option gets the whole font
(options / "b" / "hero.src.svg").write_text(swap(">still title", ">quick wavy jazz"), encoding="utf-8")
(options / "c").mkdir()
(options / "c" / "hero.src.svg").write_text(swap('id="name"', 'id="nombre"'), encoding="utf-8")
run = subprocess.run([sys.executable, str(BUILD), str(options / "*" / "hero.src.svg"), "--no-pictures"], capture_output=True, text=True, encoding="utf-8")
page = re.search(r"^options (.+)$", run.stdout, re.M)
page = Path(page.group(1)).read_text(encoding="utf-8") if page else ""
test("several sources build each one and share one options page", run.returncode == 1 and (options / "b" / "hero-light.svg").exists()
     and page.count("<h2>") == 3 and "did not build" in page, run.stdout + run.stderr)
alone = build(swap(">still title", ">quick wavy jazz"))[1]
second = run.stdout.split("== ")[2] if run.stdout.count("== ") >= 2 else ""
test("an option built after another is measured as if built alone", ("checks passed" in alone) == ("checks passed" in second) and "jazz" not in second, second)
warned("a strip without running text is warned about", re.sub(r'<g clip-path="url\(#strip\)">.*?</g></g></g>', "</g>", FIXTURE, flags=re.S), "no text travels in #ticker")
warned("a background that stands still is warned about", swap('<rect class="drift" ', "<rect "), "nothing in #backdrop is animated")
warned("a text block lost beside the picture is warned about", swap('<g id="stage">', '<g id="stage"><rect x="560" y="0" width="720" height="596" fill="$bg"/>').replace('id="about"', 'id="x"').replace('<g id="facts">', "<g>"), "the text block is too small")
warned("a bare picture is warned about", re.sub(r'<g id="stage">.*</g>\s*</svg>', '<g id="stage"><rect x="600" y="72" width="608" height="484" rx="16" fill="$panel"/><g transform="translate(700 300)"><rect class="send" opacity="0" width="28" height="28" rx="6" fill="$accent"/></g></g></svg>', FIXTURE, flags=re.S), "it reads as empty")
warned("SMIL is warned about", swap('rx="6" fill="$accent"/>', 'rx="6" fill="$accent"><animate attributeName="rx" values="6;9;6" dur="2s" repeatCount="indefinite"/></rect>'), "SMIL")
warned("a stage where nothing travels is warned about", swap("@keyframes send{0%{transform:translateX(0);opacity:0}10%,90%{opacity:1}100%{transform:translateX(60px);opacity:0}}", "@keyframes send{0%,100%{opacity:.6}50%{opacity:1}}").replace('class="flow" ', "").replace("translateY(-96px)", "translateY(-.1px)"), "nothing in #stage travels")

# ---- the checks on their own
run = subprocess.run([sys.executable, str(CHECK), str(ROOT / "tests/fixture/assets/hero.src.svg"), "--json"], capture_output=True, text=True, encoding="utf-8")
try:
    report = json.loads(run.stdout)
except ValueError:
    report = {}
test("check.py reports the measured figures as JSON", run.returncode == 0 and report.get("errors") == [] and report.get("warnings") == []
     and report.get("measured", {}).get("name_px") == 36 and report["measured"].get("stage_share", 0) >= 0.3, run.stdout + run.stderr)

# ---- the devices in references/pictures.md build as they are written
guide = (ROOT / "skills/jano/references/pictures.md").read_text(encoding="utf-8")
devices = re.findall(r"```svg\n(.*?)```", guide, re.S)
for i, device in enumerate(devices):
    letter = "ABCDEFGHIJ"[i]
    css = "".join(re.findall(r"<style>(.*?)</style>", device, re.S))
    defs = "".join(re.findall(r"<defs>(.*?)</defs>", device, re.S))
    shapes = re.sub(r"<style>.*?</style>|<defs>.*?</defs>", "", device, flags=re.S)
    hero = swap("</style>", css + "</style>")
    hero = swap("</defs>", defs + "</defs>", hero)
    hero = re.sub(r'<text id="about".*?</text>\n|<g id="facts">.*?</g>\n', "", hero, flags=re.S)  # the devices are drawn where the fixture has its text
    if letter == "I":  # the features take turns in the text block, not in the picture
        hero = swap('<g id="stage">', '<g id="facts">' + shapes + '</g>\n<g id="stage">', hero)
    else:
        hero = re.sub(r'<g id="stage">.*</g>\s*</svg>', lambda m: '<g id="stage">' + shapes + "</g></svg>", hero, flags=re.S)
    code, out, _ = build(hero)
    noise = [l for l in out.splitlines() if l.startswith(("error", "warning")) and not any(x in l for x in ("#stage", "text and picture are", "no element with id=", "say less and say it larger"))]
    test(f"device {letter} of pictures.md builds clean", code == 0 and not noise, out)
test("pictures.md has its nine devices", len(devices) == 9)

# ---- pictures of the loop
preview = Path(previews[0].group(1)).parent if previews[0] else Path("missing")
frames = [(preview / f"frame-{i}.svg").read_text(encoding="utf-8") if (preview / f"frame-{i}.svg").exists() else "" for i in range(8)]
test("eight frozen frames are written", all("animation-play-state:paused" in f for f in frames))
test("each frame is stopped at its own moment", "animation-delay:-0.500s" in frames[1] and "animation-delay:-1.000s" in frames[2], frames[1][-300:])
test("a finished frame without motion is written for each theme", all("animation:none!important}</style></svg>" in ((preview / f"still-{t}.svg").read_text(encoding="utf-8") if (preview / f"still-{t}.svg").exists() else "") for t in ("dark", "light")))
sys.path.insert(0, str(BUILD.parent))
import build as build_module  # noqa: E402

if build_module.find_browsers():
    code, out, _ = build(FIXTURE, pictures=True)
    shots = re.search(r"^pictures (.+\.png) (.+\.png)$", out, re.M)
    test("pictures of the loop and the look are taken", bool(shots) and all(Path(p).stat().st_size > 5000 for p in shots.groups()), out)
else:
    print("skip  pictures (no Chromium-family browser on this machine)")

# ---- section scenes
SCENE = (ROOT / "tests/fixture/assets/readme/demo.src.svg").read_text(encoding="utf-8")


def build_scene(source, name="demo"):
    folder = Path(tempfile.mkdtemp()) / "repo" / "assets" / "readme"
    folder.mkdir(parents=True)
    (folder / f"{name}.src.svg").write_text(source, encoding="utf-8")
    run = subprocess.run([sys.executable, str(BUILD), str(folder / f"{name}.src.svg"), "--no-pictures"], capture_output=True, text=True, encoding="utf-8")
    return run.returncode, run.stdout + run.stderr, folder


code, out, folder = build_scene(SCENE)
test("a scene builds clean", code == 0 and "checks passed" in out, out)
scene_dark = (folder / "demo-dark.svg").read_text(encoding="utf-8") if code == 0 else ""
test("a scene is written as <name>-dark.svg and <name>-light.svg", bool(scene_dark) and (folder / "demo-light.svg").exists())
test("a scene's palette roles are replaced", "$" not in re.sub(r"base64,[^)]+", "", scene_dark))
test("the scene's figures are printed", "title 44 px, 6 words" in out, out)
code, out, _ = build_scene(SCENE.replace("0 0 1280 448", "0 0 1280 640"))
test("a scene on the hero's canvas is refused", code != 0 and '"0 0 1280 448"' in out, out)
code, out, _ = build_scene(SCENE.replace('<text id="title"', "<text"))
test("a scene without a title is refused", code != 0 and 'id="title"' in out, out)
code, out, _ = build_scene(SCENE.replace('id="title" x="72" y="116" class="b"', 'id="title" x="72" y="116" class="b light"'))
test("a title that moves is refused", code != 0 and "the title is animated" in out, out)
code, out, _ = build_scene(SCENE.replace("Cards go in, done comes out", "Cards go in and then after a while done comes out"))
test("a long title is warned about", "the title has 11 words" in out, out)
code, out, _ = build_scene(SCENE.replace('<g transform="translate(400 280)"><rect class="carry" opacity="0"', '<g transform="translate(400 280)"><rect class="carry"'))
test("a parcel left frozen when motion is off is warned about in a scene", "sits frozen" in out and "data-rest" in out, out)
code, out, _ = build_scene(SCENE.replace('<g transform="translate(400 280)"><rect class="carry" opacity="0"', '<g transform="translate(400 280)" data-rest="shown"><rect class="carry"'))
test("something that rests where it is drawn on purpose is not warned about", "sits frozen" not in out, out)
pixel = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
shot = f'<image x="900" y="210" width="200" height="120" href="data:image/png;base64,{pixel}"/></g>\n</svg>'
code, out, _ = build_scene(SCENE.replace("</g>\n</svg>", shot))
test("a scene may embed a real screenshot", code == 0 and "<image" not in out, out)
code, out, _ = build(swap("</svg>", f'<image width="10" height="10" href="data:image/png;base64,{pixel}"/></svg>'))
test("the hero may not embed a screenshot", code != 0 and "<image" in out, out)

# ---- readme.py: the plan, the README and the judges
READMEPY = ROOT / "skills/jano/scripts/readme.py"
sys.path.insert(0, str(READMEPY.parent))
import readme as readme_module  # noqa: E402


def built(src_file, stale=False):
    """Stand-in outputs that carry their source's fingerprint, as build.py writes it."""
    import hashlib
    mark = "0" * 16 if stale else hashlib.sha256(src_file.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:16]
    stem = src_file.name.replace(".src.svg", "")
    for t in ("dark", "light"):
        (src_file.parent / f"{stem}-{t}.svg").write_text(f'<svg data-jano-src="{mark}">{stem}{t}</svg>', encoding="utf-8")


def repo_with(readme, plan, scenes=("demo",), judges=None, scene=None, stale=False):
    repo = Path(tempfile.mkdtemp()) / "proj"
    (repo / "assets/readme").mkdir(parents=True)
    (repo / "assets/hero.src.svg").write_text(FIXTURE, encoding="utf-8")
    built(repo / "assets/hero.src.svg")
    for i, s in enumerate(scenes):
        src = (scene if scene and i == 0 else SCENE).replace("Cards go in, done comes out", ["Cards go in, done comes out", "Install it in one line", "Three ways people use it"][i % 3])
        if i:
            src = src.replace(">inbox<", f">queue{i}<").replace(">done<", f">shelf{i}<")
        (repo / f"assets/readme/{s}.src.svg").write_text(src, encoding="utf-8")
        built(repo / f"assets/readme/{s}.src.svg", stale and i == 0)
    (repo / "README.md").write_text(readme, encoding="utf-8")
    (repo / "assets/readme/plan.json").write_text(json.dumps(plan), encoding="utf-8")
    if judges is not None:
        (repo / "assets/readme/judges.json").write_text(json.dumps(judges(repo, plan) if callable(judges) else judges), encoding="utf-8")
    run = subprocess.run([sys.executable, str(READMEPY), "check", str(repo)], capture_output=True, text=True, encoding="utf-8")
    return run.returncode, run.stdout + run.stderr


def pic(name):
    return (f'<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/readme/{name}-dark.svg">'
            f'<img src="assets/readme/{name}-light.svg" alt="A card travels from the inbox to the done panel while rows light up" width="100%"></picture></p>\n\n')


WORDS20 = "It does one plain thing for the people who use it, every day, and it does it well enough that they keep it. "
GOOD = ("<h1 align=\"center\">Proj</h1>\n\n**Proj sorts your cards for you.** " + WORDS20 * 2 + "\n\n"
        "## What you get\n\n" + pic("demo") + "- **Sorted cards.** " + WORDS20 + "\n- **Less work.** " + WORDS20 + "\n- **Calm.** " + WORDS20 + "\n\n"
        "## Install\n\n" + pic("install") + "Run this in a terminal and you are done with it in a minute or so.\n\n```bash\npip install proj\n```\n\n"
        "## Who it is for\n\n" + pic("people") + WORDS20 + WORDS20 + "\n\n"
        "## Questions\n\n<details><summary><b>Is it free?</b></summary>\n\nYes.\n\n</details>\n\n" + WORDS20 + WORDS20 + "\n\n"
        "## License\n\nMIT, see the LICENSE file in this folder.\n")
PLAN_OK = {"audience": "general", "audience_confirmed": True, "sentence": "sorts cards", "unfinished": [],
           "hero": {"file": "assets/hero.src.svg", "shows": ["lines", "parcel"]},
           "sections": [
               {"heading": "What you get", "role": "features", "picture": {"file": "assets/readme/demo.src.svg", "claim": "cards get sorted", "shows": ["inbox", "done", "card"]}},
               {"heading": "Install", "role": "install", "picture": {"file": "assets/readme/install.src.svg", "claim": "one line installs it", "shows": ["terminal"]}},
               {"heading": "Who it is for", "role": "audience", "picture": {"file": "assets/readme/people.src.svg", "claim": "three people use it", "shows": ["people"]}},
               {"heading": "Questions", "role": "faq"},
               {"heading": "License", "role": "license"}]}
SCENES = ("demo", "install", "people")


def passing(repo, plan):
    return {i["id"]: {"sha": i["sha"], "pass": True} for i in readme_module.judge_items(repo, plan)}


code, out = repo_with(GOOD, PLAN_OK, SCENES, judges=passing)
test("readme.py: a README that keeps its plan passes", code == 0 and "checks passed" in out, out)
code, out = repo_with(GOOD, PLAN_OK, SCENES, judges=passing, stale=True)
test("readme.py: a picture built from another version of its source fails", code == 1 and "built from another version of its source" in out, out)
test("the build writes its source's fingerprint into each output", 'data-jano-src="' in scene_dark)
_, _, again = build_scene(SCENE)
test("the same source builds the same bytes", (again / "demo-dark.svg").read_text(encoding="utf-8") == scene_dark)
marks = []
for ending in (b"\n", b"\r\n"):  # the same source as git stores it and as a Windows checkout writes it
    folder = Path(tempfile.mkdtemp()) / "repo" / "assets" / "readme"
    folder.mkdir(parents=True)
    (folder / "demo.src.svg").write_bytes(SCENE.replace("\r\n", "\n").encode("utf-8").replace(b"\n", ending))
    subprocess.run([sys.executable, str(BUILD), str(folder / "demo.src.svg"), "--no-pictures"], capture_output=True)
    out_file = folder / "demo-dark.svg"
    found = re.search(r'data-jano-src="([0-9a-f]+)"', out_file.read_text(encoding="utf-8")) if out_file.exists() else None
    marks.append(found.group(1) if found else None)
test("a source with Windows line endings has the fingerprint git will see", marks[0] is not None and marks[0] == marks[1], str(marks))
code, out = repo_with(GOOD, PLAN_OK, SCENES)
test("readme.py: a README nobody judged fails", code == 1 and "no judges yet" in out, out)
code, out = repo_with(GOOD, PLAN_OK, SCENES, judges=lambda r, p: {**passing(r, p), "readme": {"sha": "old", "pass": True}})
test("readme.py: a verdict on an older version does not count", code == 1 and "judged on an older version" in out, out)
code, out = repo_with(GOOD, PLAN_OK, SCENES, judges=lambda r, p: {**passing(r, p), "readme": {"sha": passing(r, p)["readme"]["sha"], "pass": False, "why": "unclear"}})
test("readme.py: a failed cold read fails the README", code == 1 and "failed its cold read" in out, out)
code, out = repo_with(GOOD, {**PLAN_OK, "audience_confirmed": False}, SCENES, judges=passing)
test("readme.py: an audience nobody confirmed fails", code == 1 and "audience_confirmed" in out, out)
code, out = repo_with(GOOD, {**PLAN_OK, "audience": "technical"}, SCENES, judges=passing)
test("readme.py: a technical README needs a section on how to use it", code == 1 and "none of use, reference" in out, out)
code, out = repo_with(GOOD.replace("```bash", "```"), PLAN_OK, SCENES, judges=passing)
test("readme.py: a code block without a language fails", code == 1 and "has no language" in out, out)
code, out = repo_with(GOOD.replace("**Proj sorts", "> [!NOTE]\n> Hi.\n\n**Proj sorts"), PLAN_OK, SCENES, judges=passing)
test("readme.py: an alert in the lead fails", code == 1 and "an alert in the lead" in out, out)
code, out = repo_with(GOOD.replace("Run this in a terminal", "> [!CAUTION]\n> Careful.\n\nRun this in a terminal"), PLAN_OK, SCENES, judges=passing)
test("readme.py: an alert the role does not take fails", code == 1 and "[!CAUTION] alert where the install role takes" in out, out)
code, out = repo_with(GOOD.replace("- **Calm.**", "| a | b |\n|---|---|\n| 1 | 2 |\n\n- **Calm.**"), PLAN_OK, SCENES, judges=passing)
test("readme.py: a table where the role takes none fails", code == 1 and "a table in the features role" in out, out)
code, out = repo_with(GOOD.replace("- **Calm.** ", "- **Calm.** x\n- **Quiet.** x\n- **Fast.** x\n- **Small.** x\n- **Kind.** "), PLAN_OK, SCENES, judges=passing)
test("readme.py: more feature items than the role holds are warned about", "feature items: 3 to 6" in out, out)
test("readme.py: three feature items are fine", "feature items: 3 to 6" not in repo_with(GOOD, PLAN_OK, SCENES, judges=passing)[1])
code, out = repo_with(GOOD.replace("## Who it is for\n\n", "## Who it is for\n\n" + WORDS20 * 8), PLAN_OK, SCENES, judges=passing)
test("readme.py: a section over its words is sent to docs/", code == 1 and "Move the detail to a file in docs/" in out, out)
SCENE_CMD = SCENE.replace(">inbox<", ">proj frobnicate<")
code, out = repo_with(GOOD, PLAN_OK, SCENES, judges=passing, scene=SCENE_CMD)
test("readme.py: a picture that draws a command the repo never mentions fails", code == 1 and "proj frobnicate" in out, out)
code, out = repo_with(GOOD.replace("pip install proj", "pip install proj\nproj frobnicate"), PLAN_OK, SCENES, judges=passing, scene=SCENE_CMD)
test("readme.py: a picture may draw a command the README documents", "proj frobnicate" not in out, out)
code, out = repo_with(GOOD.replace("MIT, see", '<img src="assets/readme/demo-dark.svg" alt=""> MIT, see'), PLAN_OK, SCENES, judges=passing)
test("readme.py: a decorative image may have an empty alt text", "without alt text" not in out, out)
code, out = repo_with(GOOD.replace('<h1 align="center">Proj</h1>', '<h1 align="center" style="color:red">Proj</h1>'), PLAN_OK, SCENES, judges=passing)
test("readme.py: style= fails, GitHub removes it", code == 1 and "GitHub removes them" in out, out)
same = json.loads(json.dumps(PLAN_OK))
same["sections"][2]["picture"]["shows"] = ["inbox", "done", "card"]
code, out = repo_with(GOOD, same, SCENES, judges=passing)
test("readme.py: two pictures that show the same things fail", code == 1 and "the same things" in out, out)
dropped = {**PLAN_OK, "unfinished": [{"item": "sync", "match": "cloud sync", "decision": "drop"}]}
code, out = repo_with(GOOD.replace("Less work.", "Cloud sync."), dropped, SCENES, judges=passing)
test("readme.py: an unfinished feature the user dropped may not appear", code == 1 and "chose to leave out" in out, out)
code, out = repo_with(GOOD.replace(pic("install"), ""), PLAN_OK, SCENES, judges=passing)
test("readme.py: a scene the plan names must be shown under its heading", code == 1 and "the scene is not shown as the plan says" in out, out)
captured = json.loads(json.dumps(PLAN_OK))
captured["sections"][0]["picture"]["type"] = "capture"
code, out = repo_with(GOOD, captured, SCENES, judges=passing)
test("readme.py: a screenshot the user did not agree to fails", code == 1 and "captures_agreed" in out, out)
code, out = repo_with(GOOD.replace("see the LICENSE file", "see [the details](docs/licence.md)"), PLAN_OK, SCENES, judges=passing)
test("readme.py: a link to a file that does not exist fails", code == 1 and "docs/licence.md, which does not exist" in out, out)
run = subprocess.run([sys.executable, str(READMEPY), "rules"], capture_output=True, text=True, encoding="utf-8")
test("readme.py rules prints every role", run.returncode == 0 and all(k in run.stdout for k in readme_module.ROLES), run.stderr)

# ---- skill files: a ": " in an unquoted YAML value makes installers skip the skill
for skill in sorted(ROOT.glob("**/SKILL.md")):
    head = skill.read_text(encoding="utf-8").split("---")[1]
    bad = [l for l in head.splitlines() if re.match(r"^\w[\w-]*: [^\"'].*: ", l)]
    test(f"{skill.relative_to(ROOT).as_posix()} has valid frontmatter", not bad, " | ".join(bad))

# ---- the pull request check
node = shutil.which("node")
if node:
    body = "## What\nOne change.\n## Why\nA problem.\n## How\nAn approach.\n## Evidence\nTests.\n## Checklist\n- [x] one thing\n"
    pr = Path(tempfile.mkdtemp()) / "pr.md"

    def check(branch, title, text):
        pr.write_text(text, encoding="utf-8")
        return subprocess.run([node, str(ROOT / ".github/scripts/check-pr.js"), "--branch", branch, "--title", title, "--body-file", str(pr)], capture_output=True, text=True).returncode

    test("a correct pull request passes", check("feature/outline-rotated-text", "fix: outline text inside rotated groups", body) == 0)
    test("a wrong branch name fails", check("fix/rotated", "fix: outline text", body) == 1)
    test("an unticked checklist fails", check("feature/outline-rotated-text", "fix: outline text", body.replace("[x]", "[ ]")) == 1)
    test("a missing section fails", check("feature/outline-rotated-text", "fix: outline text", body.replace("## Why\nA problem.\n", "")) == 1)
else:
    print("skip  pull request check (node is not installed)")

print(f"\n{len(failed)} failed" if failed else "\nall passed")
sys.exit(1 if failed else 0)
