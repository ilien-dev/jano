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
