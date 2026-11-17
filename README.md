<p align="center"><b>English</b> · <a href="README.es.md">Español</a></p>

<h1 align="center">Jano: an animated SVG hero for your GitHub README</h1>

<p align="center"><b>An agent skill that draws your repository a looping animated hero and writes the header under it,<br>
so the first screen of the README shows what the project does.</b></p>

<p align="center">Jano reads your repository, decides which picture explains it, and draws that picture as an animated SVG in dark and light. A terminal tool gets its real commands, an app gets a small version of its screen, a converter gets the thing it converts. Then it adds a logo if you have none and the header block: title, slogan, description, badges and menu. It works in Claude Code, Codex and any agent that reads the Agent Skills format.</p>

<p align="center">
  <a href="#install"><img alt="Agent skill for Claude Code, Codex and others" src="https://img.shields.io/badge/agent%20skill-Claude%20Code%20%C2%B7%20Codex-1D6A99?style=flat-square&labelColor=0F1115"></a>
  <a href="#what-the-build-does"><img alt="Output: animated SVG in dark and light" src="https://img.shields.io/badge/output-animated%20SVG%2C%20dark%20%2B%20light-1D6A99?style=flat-square&labelColor=0F1115"></a>
  <a href="CHANGELOG.md"><img alt="Version 0.1.0" src="https://img.shields.io/badge/version-0.1.0-0F1115?style=flat-square"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-0F1115?style=flat-square"></a>
</p>

<p align="center">
  <a href="#install"><b>Install</b></a> ·
  <a href="#use"><b>Use</b></a> ·
  <a href="#what-you-get"><b>What you get</b></a> ·
  <a href="#the-rules-it-follows"><b>Rules</b></a> ·
  <a href="#what-the-build-does"><b>Build</b></a> ·
  <a href="#limits"><b>Limits</b></a>
</p>

---

This README has no hero yet. It will get one made with Jano.

## Install

With the [skills](https://skills.sh) CLI, which installs it for Claude Code, Codex, Cursor, Gemini CLI and the other agents it supports:

```sh
npx skills add ilien-dev/jano
```

As a Claude Code plugin, run these two commands inside Claude Code:

```
/plugin marketplace add ilien-dev/jano
/plugin install jano@jano
```

By hand, copy `skills/jano` to where your agent looks for skills: `~/.claude/skills/jano` for Claude Code, `~/.agents/skills/jano` for Codex and others.

The build script needs Python 3.9 or later. With [uv](https://docs.astral.sh/uv/) it installs its two dependencies by itself. Without uv, run `pip install fonttools brotli` once.

## Use

Jano only runs when you call it. The agent never starts it on its own.

| Agent | How to call it |
|---|---|
| Claude Code | `/jano` (as a plugin: `/jano:jano`) |
| Codex | `$jano` |
| Others | "use the jano skill on this repository" |

Open the agent in the repository you want a hero for and call the skill. You can add what you want to see: `/jano show the sync between the two files, keep our blue`. It writes the files and shows you a preview page. It does not commit.

## What you get

```
assets/logo.svg         the mark, kept if you already have one
assets/hero.src.svg     the source you or the agent edit
assets/hero-dark.svg    built from the source
assets/hero-light.svg   built from the source
README.md               the header replaced, the rest untouched
```

The README header always has the same parts, in this order: the hero, a language switch if there is a Spanish README, the title, a one-sentence slogan, a one-paragraph description, three to five badges and a menu of links to the sections.

## The rules it follows

The header is the same in every repository. The hero is not: two heroes made with Jano should look nothing alike, because the composition comes from the project.

- **The picture explains the tool.** Someone who reads no text should still guess what it does. Only facts the repository backs go in, never an invented number.
- **It never stops and never restarts.** Every animation loops forever and closes on itself. There is no intro or outro, and no scene that builds up and resets, so it reads as a place that is running and not as a video.
- **Something moves everywhere, one thing leads.** The picture of the tool carries the motion and the rest stays quiet.
- **Text stays readable.** The title and tagline stay still. Text that scrolls does it at a constant, slow speed.
- **Your identity wins.** An existing logo and colors are reused. If there are none, it picks one accent and keeps the rest neutral.

## What the build does

GitHub shows an SVG as an image, so scripts and external files do not load, and a browser draws slow-moving text in small jumps. `build.py` takes care of both:

- It writes the dark and the light file from one source with a palette of named colors.
- It embeds only the letters used of Space Grotesk and JetBrains Mono, so the hero looks the same on every machine.
- It turns text that moves into outlines, which glide where live text would stutter.
- It adds the rule that stops the motion for people who ask their system for reduced motion.
- It refuses animations that play once, scripts and external files, and warns about low contrast, small text and heavy files.
- It writes a preview page with both themes at README width and at phone width.

A hero built this way weighs between 50 and 80 KB.

## Limits

- This is version 0.1.0. It has been tried on three repositories, by one person.
- The result depends on the model that runs it. A weaker model draws a weaker hero.
- The agent sees still frames of its own work. You are the one who checks the motion, in the preview.
- The fonts are fixed: Space Grotesk and JetBrains Mono. A project with its own typefaces does not get them in the hero.
- The hero is in English. The Spanish README shares it.

## License

MIT, see [LICENSE](LICENSE). The two bundled fonts are under the SIL Open Font License, and their license files sit next to them in `skills/jano/assets`.
