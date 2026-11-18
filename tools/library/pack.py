"""Packs Iconify's packaging of each upstream set into Jano's asset library: one gzip JSON per family,
manifest.json, and the upstream licence texts.

    bash tools/library/fetch.sh [work]       downloads the sets and the licences into work/ (default tools/library/work)
    python tools/library/pack.py [work]      writes skills/jano/assets/library/

Licences are the ones read in each project's own LICENSE file, never Iconify's label; only MIT, ISC and CC0 sets
are packed. work/info.json holds each package's version, work/simple-icons-data.json the per-icon licences of
Simple Icons (only CC0 icons are kept), work/lucide/tags.json Lucide's search tags.
"""
import gzip, hashlib, json, re, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "work"
PKG, LIC = WORK / "pkg", WORK / "licenses"
DEST = HERE.parents[1] / "skills" / "jano" / "assets" / "library"
_lt = WORK / "lucide" / "tags.json"
LUCIDE_TAGS = json.loads(_lt.read_text(encoding="utf-8")) if _lt.exists() else {}

# family -> what the agent needs to choose it. Licences are the ones read in each project's own LICENSE file,
# never Iconify's label (several are wrong). attrs describe the look, so a family is picked by fit, not by order.
F = {}


def fam(prefix, category, title, licence, holder, repo, licence_file, attrs, about, variants=None, recolor="mono", drop=None, notes=""):
    F[prefix] = dict(prefix=prefix, category=category, title=title, licence=licence, holder=holder, repo=repo, licence_file=licence_file,
                     attrs=attrs, about=about, variants=variants or {}, recolor=recolor, drop=drop, notes=notes)


ICON_WEIGHTS = r"-(thin|light|bold|fill|duotone)$"
# ---- icons: line, glyph, duotone, pixel, multicolour
fam("lucide", "icons", "Lucide", "ISC AND MIT", "Lucide Contributors; Cole Bemis (Feather, MIT)", "https://github.com/lucide-icons/lucide", "lucide",
    {"fill": "line", "stroke": "regular", "corners": "round", "grid": 24}, "Clean 2 px line icons with round caps; the default look of modern developer tools.")
fam("tabler", "icons", "Tabler Icons", "MIT", "Paweł Kuna", "https://github.com/tabler/tabler-icons", "tabler",
    {"fill": "line", "stroke": "regular", "corners": "round", "grid": 24}, "6,500 line icons, the widest line vocabulary; a filled variant for many.",
    {"outline": r"^(?!.*-filled$)", "filled": r"-filled$"})
fam("ph", "icons", "Phosphor", "MIT", "Phosphor Icons", "https://github.com/phosphor-icons/core", "ph",
    {"fill": "line", "stroke": "any", "corners": "round", "grid": 24}, "One drawing in six weights: thin, light, regular, bold, fill and duotone; pick the weight that matches the mark.",
    {"regular": r"^(?!.*" + ICON_WEIGHTS[1:] + ")", "thin": r"-thin$", "light": r"-light$", "bold": r"-bold$", "fill": r"-fill$", "duotone": r"-duotone$"})
fam("heroicons", "icons", "Heroicons", "MIT", "Tailwind Labs, Inc.", "https://github.com/tailwindlabs/heroicons", "heroicons",
    {"fill": "line", "stroke": "regular", "corners": "round", "grid": 24}, "Tailwind's set: 1.5 px outline and solid; restrained and product-like.",
    {"outline": r"^(?!.*-(solid|20-solid|16-solid)$)", "solid": r"(?<!-20)(?<!-16)-solid$", "mini": r"-20-solid$", "micro": r"-16-solid$"})
fam("iconoir", "icons", "Iconoir", "MIT", "Luca Burgio", "https://github.com/iconoir-icons/iconoir", "iconoir",
    {"fill": "line", "stroke": "light", "corners": "round", "grid": 24}, "Thin 1.5 px line icons with an airy, editorial feel; solid variants for some.",
    {"regular": r"^(?!.*-solid$)", "solid": r"-solid$"})
fam("pixelarticons", "icons", "Pixelarticons", "MIT", "Gerrit Halfmann", "https://github.com/halfmage/pixelarticons", "pixelarticons",
    {"fill": "pixel", "stroke": "none", "corners": "sharp", "grid": 24}, "Pixel-art icons on a 24 px grid: retro, games, terminals, playful tools.")
fam("fluent", "icons", "Fluent UI System Icons", "MIT", "Microsoft Corporation", "https://github.com/microsoft/fluentui-system-icons", "fluent",
    {"fill": "line", "stroke": "regular", "corners": "round", "grid": 24}, "Microsoft's 20,000 product icons, regular and filled, in several sizes; soft and friendly.",
    {"regular": r"-regular$", "filled": r"-filled$"})
fam("fluent-color", "icons", "Fluent UI Color Icons", "MIT", "Microsoft Corporation", "https://github.com/microsoft/fluentui-system-icons", "fluent",
    {"fill": "color", "stroke": "none", "corners": "round", "grid": 24}, "Fluent's multicolour icons: soft gradients, keep their colours or tint them to one role.", recolor="keep")
fam("octicon", "icons", "Octicons", "MIT", "GitHub Inc.", "https://github.com/primer/octicons", "octicon",
    {"fill": "glyph", "stroke": "regular", "corners": "round", "grid": 16, "domain": "github"}, "GitHub's own UI glyphs (16 and 24 px): repos, branches, PRs, issues. GitHub's logos are removed.",
    {"16": r"-16$", "24": r"-24$"}, drop=r"(github|gist|copilot|logo|mark-)")
fam("hugeicons", "icons", "Hugeicons Free", "MIT", "Hugeicons", "https://hugeicons.com", "hugeicons",
    {"fill": "line", "stroke": "light", "corners": "round", "grid": 24}, "The free stroke-rounded style of Hugeicons: 6,000 friendly, rounded line icons.")
fam("bi", "icons", "Bootstrap Icons", "MIT", "The Bootstrap Authors", "https://github.com/twbs/icons", "bi",
    {"fill": "line", "stroke": "regular", "corners": "mixed", "grid": 16}, "Bootstrap's 16 px icons, outline and -fill: crisp at small sizes.",
    {"outline": r"^(?!.*-fill$)", "fill": r"-fill$"})
fam("radix-icons", "icons", "Radix Icons", "MIT", "WorkOS", "https://github.com/radix-ui/icons", "radix-icons",
    {"fill": "line", "stroke": "thin", "corners": "sharp", "grid": 15}, "332 crisp 15 px icons for interfaces: precise, technical, small.")
fam("healthicons", "icons", "Health Icons", "CC0-1.0", "Resolve to Save Lives", "https://github.com/resolvetosavelives/healthicons", "healthicons",
    {"fill": "line", "stroke": "regular", "corners": "round", "grid": 24, "domain": "health"}, "Health and medicine: devices, people, places, conditions; outline, filled and negative.",
    {"outline": r"-outline$", "filled": r"^(?!.*-(outline|negative)$)", "negative": r"-negative$"})
fam("akar-icons", "icons", "Akar Icons", "MIT", "Arturo Wibawa", "https://github.com/artcoholic/akar-icons", "akar-icons",
    {"fill": "line", "stroke": "regular", "corners": "round", "grid": 24}, "Rounded line icons with a hand-made warmth.")
fam("majesticons", "icons", "Majesticons", "MIT", "Gerrit Halfmann", "https://github.com/halfmage/majesticons", "majesticons",
    {"fill": "line", "stroke": "regular", "corners": "round", "grid": 24}, "Balanced line and solid pairs for product interfaces.",
    {"line": r"-line$", "solid": r"^(?!.*-line$)"})
fam("eva", "icons", "Eva Icons", "MIT", "Akveo", "https://github.com/akveo/eva-icons", "eva",
    {"fill": "solid", "stroke": "regular", "corners": "round", "grid": 24}, "Soft outline and fill pairs with rounded ends (no longer maintained).",
    {"outline": r"-outline$", "fill": r"^(?!.*-outline$)"})
fam("mynaui", "icons", "Myna UI Icons", "MIT", "Praveen Juge", "https://github.com/praveenjuge/mynaui-icons", "mynaui",
    {"fill": "line", "stroke": "regular", "corners": "round", "grid": 24}, "Neutral line and solid icons made for interfaces.",
    {"line": r"^(?!.*-solid$)", "solid": r"-solid$"})
fam("humbleicons", "icons", "Humbleicons", "MIT", "Jiří Zralý", "https://github.com/zraly/humbleicons", "humbleicons",
    {"fill": "line", "stroke": "regular", "corners": "round", "grid": 24}, "A small, minimal line set: few strokes, very calm.")
fam("zondicons", "icons", "Zondicons", "MIT", "Steve Schoger", "https://github.com/dukestreetstudio/zondicons", "zondicons",
    {"fill": "glyph", "stroke": "none", "corners": "sharp", "grid": 20}, "Solid 20 px glyphs: bold silhouettes that read at small sizes.")
fam("simple-line-icons", "icons", "Simple Line Icons", "MIT", "Sabbir Ahmed", "https://github.com/thesabbir/simple-line-icons", "simple-line-icons",
    {"fill": "line", "stroke": "thin", "corners": "round", "grid": 32}, "Thin, light line icons from the 2010s web; delicate (no longer maintained).")
fam("bx", "icons", "Boxicons 2", "MIT", "Atisa", "https://github.com/box-icons/boxicons", "bx",
    {"fill": "line", "stroke": "regular", "corners": "mixed", "grid": 24}, "Regular and solid Boxicons (the brand logos, bxl, are removed).",
    {"regular": r"^(?!bxs-)", "solid": r"^bxs-"}, drop=r"^bxl-")
# ---- objects
fam("fluent-emoji-flat", "objects", "Fluent Emoji Flat", "MIT", "Microsoft Corporation", "https://github.com/microsoft/fluentui-emoji", "fluent-emoji",
    {"fill": "color", "stroke": "none", "corners": "round", "grid": 32}, "3,000 flat objects, people-free things and symbols with few solid fills: easy to tint.", recolor="keep")
fam("fluent-emoji-high-contrast", "objects", "Fluent Emoji High Contrast", "MIT", "Microsoft Corporation", "https://github.com/microsoft/fluentui-emoji", "fluent-emoji",
    {"fill": "glyph", "stroke": "none", "corners": "round", "grid": 32}, "Monochrome objects: one role colours them, they sit well beside line icons.")
# ---- logos: mono sets take the palette, colour sets keep the brand
fam("simple-icons", "logos", "Simple Icons", "CC0-1.0", "Simple Icons Collaborators", "https://github.com/simple-icons/simple-icons", "simple-icons",
    {"fill": "glyph", "stroke": "none", "corners": "any", "grid": 24}, "3,400 brand marks as one-colour silhouettes: take any role from the palette.",
    notes="Only icons whose own licence is CC0 are kept; brands remain trademarks of their owners.")
fam("devicon-plain", "logos", "Devicon Plain", "MIT", "konpa and contributors", "https://github.com/devicons/devicon", "devicon",
    {"fill": "glyph", "stroke": "none", "corners": "any", "grid": 32}, "Programming languages and tools as one-colour marks.")
fam("cib", "logos", "CoreUI Brands", "CC0-1.0", "creativeLabs Łukasz Holeczek", "https://github.com/coreui/coreui-icons", "coreui",
    {"fill": "glyph", "stroke": "none", "corners": "any", "grid": 32}, "830 one-colour brand marks, a little heavier than Simple Icons.")
fam("logos", "logos", "SVG Logos (gilbarbara)", "CC0-1.0", "Gil Barbara", "https://github.com/gilbarbara/logos", "logos",
    {"fill": "color", "stroke": "none", "corners": "any", "grid": 0}, "2,000 logos in their brand colours, many with wordmarks.", recolor="keep")
fam("devicon", "logos", "Devicon Colour", "MIT", "konpa and contributors", "https://github.com/devicons/devicon", "devicon",
    {"fill": "color", "stroke": "none", "corners": "any", "grid": 32}, "Programming languages and tools in their own colours.", recolor="keep")
fam("skill-icons", "logos", "Skill Icons", "MIT", "tandpfun", "https://github.com/tandpfun/skill-icons", "skill-icons",
    {"fill": "color", "stroke": "none", "corners": "round", "grid": 24}, "Tech logos set on rounded tiles, light and dark: a badge look.", recolor="keep")
# ---- flags keep their real colours
fam("flag", "flags", "flag-icons", "MIT", "Panayiotis Lipiridis", "https://github.com/lipis/flag-icons", "flag",
    {"fill": "color", "stroke": "none", "corners": "sharp", "grid": 0}, "Rectangular flags in 4:3 and 1:1 for every country.", {"4x3": r"-4x3$", "1x1": r"-1x1$"}, recolor="never")
fam("circle-flags", "flags", "Circle Flags", "MIT", "HatScripts", "https://github.com/HatScripts/circle-flags", "circle-flags",
    {"fill": "color", "stroke": "none", "corners": "round", "grid": 32}, "Round flags: friendly, sit well in chips and avatars.", recolor="never")
fam("cif", "flags", "CoreUI Flags", "CC0-1.0", "creativeLabs Łukasz Holeczek", "https://github.com/coreui/coreui-icons", "coreui",
    {"fill": "color", "stroke": "none", "corners": "sharp", "grid": 0}, "Plain rectangular flags.", recolor="never")
fam("flagpack", "flags", "Flagpack", "MIT", "Yummygum", "https://github.com/Yummygum/flagpack-core", "flagpack",
    {"fill": "color", "stroke": "none", "corners": "round", "grid": 24}, "Flags with rounded corners and a soft frame.", recolor="never")
# ---- files
fam("catppuccin", "files", "Catppuccin Icons", "MIT", "Catppuccin", "https://github.com/catppuccin/vscode-icons", "catppuccin",
    {"fill": "line", "stroke": "regular", "corners": "round", "grid": 16}, "File and folder icons by type (json, md, py, folder-src), pastel line style.", recolor="keep")


def tags_for(prefix, data):
    tags = {}
    for cat, names in (data.get("categories") or {}).items():
        for n in names:
            tags.setdefault(n, []).append(cat.lower())
    if prefix == "lucide":
        for n, t in LUCIDE_TAGS.items():
            tags.setdefault(n, []).extend(t)
    return tags


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / "licenses").mkdir(exist_ok=True)
    info = {r["prefix"]: r for r in json.loads((WORK / "info.json").read_text(encoding="utf-8"))} if (WORK / "info.json").exists() else {}
    si_licence = {}
    si = WORK / "simple-icons-data.json"
    if si.exists():  # per-icon licences of Simple Icons: keep the CC0 ones only
        for item in json.loads(si.read_text(encoding="utf-8")):
            slug = item.get("slug") or re.sub(r"[^a-z0-9]", "", item["title"].lower())
            si_licence[slug] = (item.get("license") or {}).get("type")
    manifest, total = {"sets": []}, 0
    for prefix, f in F.items():
        src = PKG / f"{prefix}.json"
        raw = src.read_bytes()
        data = json.loads(raw)
        icons = {n: v["body"] for n, v in data["icons"].items()}
        aliases = {a: v["parent"] for a, v in (data.get("aliases") or {}).items() if v.get("parent") in icons and not set(v) - {"parent"}}
        dropped = 0
        if f["drop"]:
            for n in [n for n in icons if re.search(f["drop"], n)]:
                del icons[n]
                dropped += 1
        if prefix == "simple-icons":
            for n in [n for n in icons if si_licence.get(n) not in (None, "CC0-1.0")]:
                del icons[n]
                dropped += 1
        aliases = {a: p for a, p in aliases.items() if p in icons}
        sizes = {n: [v.get("width", data.get("width", 16)), v.get("height", data.get("height", 16))] for n, v in data["icons"].items() if n in icons
                 and (v.get("width") or v.get("height"))}
        pack = {"prefix": prefix, "width": data.get("width", 16), "height": data.get("height", 16), "icons": icons, "sizes": sizes,
                "aliases": aliases, "tags": {n: t for n, t in tags_for(prefix, data).items() if n in icons}}
        out = DEST / f"{prefix}.json.gz"
        out.write_bytes(gzip.compress(json.dumps(pack, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), 9, mtime=0))
        lic_src = LIC / f"{f['licence_file']}.txt"
        lic_dest = DEST / "licenses" / f"{f['licence_file']}.txt"
        if lic_src.exists():
            shutil.copyfile(lic_src, lic_dest)
        entry = {k: f[k] for k in ("prefix", "category", "title", "licence", "holder", "repo", "attrs", "about", "variants", "recolor", "notes")}
        entry.update(count=len(icons), dropped=dropped, version=info.get(prefix, {}).get("version"),
                     source=f"@iconify-json/{prefix} (Iconify's packaging of {f['repo']})", sha256=hashlib.sha256(raw).hexdigest(),
                     licence_text=f"licenses/{f['licence_file']}.txt", kb=out.stat().st_size // 1024)
        manifest["sets"].append(entry)
        total += out.stat().st_size
        print(f"{prefix:28} {len(icons):6} icons  dropped {dropped:4}  {out.stat().st_size // 1024:6} KB  licence text {'ok' if lic_src.exists() else 'MISSING'}")
    (DEST / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"total {total // 1024} KB")


if __name__ == "__main__":
    main()
