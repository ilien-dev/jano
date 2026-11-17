# /// script
# requires-python = ">=3.9"
# dependencies = ["fonttools", "brotli"]
# ///
"""Tests for skills/jano/scripts/build.py and .github/scripts/check-pr.js.

    uv run tests/run.py
"""
import re, shutil, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "skills/jano/scripts/build.py"
FIXTURE = (ROOT / "tests/fixture/assets/hero.src.svg").read_text(encoding="utf-8")
failed = []


def build(source):
    """Builds `source` in a fresh folder. Returns (exit code, output, folder)."""
    folder = Path(tempfile.mkdtemp()) / "repo" / "assets"
    folder.mkdir(parents=True)
    (folder / "hero.src.svg").write_text(source, encoding="utf-8")
    run = subprocess.run([sys.executable, str(BUILD), str(folder / "hero.src.svg")], capture_output=True, text=True, encoding="utf-8")
    return run.returncode, run.stdout + run.stderr, folder


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

# ---- moving text becomes outlines, still text stays text
test("text that travels is outlined", "first line" not in dark and "third line" not in dark and "<use" in dark)
test("text that stays still is kept", "still title" in dark)
test("text that only changes opacity is kept", "pulses, does not travel" in dark)
test("three moving text elements are reported", "3 moving text element(s)" in out, out)
root = ET.fromstring(dark) if dark else None
uses = [u.get("href") for u in root.iter("{http://www.w3.org/2000/svg}use")] if root is not None else []
ids = {p.get("id") for p in root.iter("{http://www.w3.org/2000/svg}path")} if root is not None else set()
test("every outlined glyph has its shape", bool(uses) and all(u[1:] in ids for u in uses))
test("outlines use the font of each run", any(u.startswith("#gm") for u in uses) and any(u.startswith("#gs") for u in uses) and any(u.startswith("#gb") for u in uses))

# ---- sources the build must refuse
def refused(name, source, expect):
    code, out, _ = build(source)
    test(name, code != 0 and expect in out, out)

refused("an animation that plays once is refused", FIXTURE.replace("scroll 8s linear infinite", "scroll 8s linear"), "infinite")
refused("a script is refused", FIXTURE.replace("</svg>", "<script>1</script></svg>"), "<script")
refused("an external image is refused", FIXTURE.replace("</svg>", '<image href="https://example.com/a.png"/></svg>'), "<image")
refused("an unknown palette role is refused", FIXTURE.replace('fill="$ink"', 'fill="$nope"'), "$nope")
refused("a different canvas is refused", FIXTURE.replace("0 0 1280 640", "0 0 800 400"), "viewBox")
refused("a source without a palette is refused", re.sub(r"<!--palette.*?-->", "", FIXTURE, flags=re.S), "palette")

# ---- sources the build must warn about
def warned(name, source, expect):
    code, out, _ = build(source)
    test(name, code == 0 and "warning" in out and expect in out, out)

warned("small text is warned about", FIXTURE.replace('font-size="14"', 'font-size="10"'), "font-size below 13")
warned("low contrast is warned about", FIXTURE.replace("muted  #A3A8B0", "muted  #2A2F37"), "contrast")
warned("a positive delay is warned about", FIXTURE.replace(".pulse{", ".pulse{animation-delay:1s;"), "animation-delay")

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
