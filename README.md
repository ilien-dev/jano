<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <img src="assets/hero-light.svg" alt="Jano: a wall of eight small moving pictures, each for a different project (an app, a way past a wall, a chat, a memory, a sound tool, a book converter, a map, a game), around the Jano mark and the line: every project gets its own moving picture." width="100%">
  </picture>
</p>

<p align="center"><b>English</b> · <a href="README.es.md">Español</a></p>

<h1 align="center">Jano: an animated SVG hero for your GitHub README</h1>

<p align="center"><b>An agent skill that draws your repository a looping animated hero,<br>
so the first screen of the README shows what the project does.</b></p>

<p align="center">Jano reads your repository, decides which picture explains it, and draws that picture as an animated SVG in dark and light. A terminal tool gets its real commands, an app gets a small version of its screen, a converter gets the thing it converts. It adds a logo if you have none, and it leaves the text of your README alone. It works in Claude Code, Codex and any agent that reads the Agent Skills format.</p>

<p align="center">
  <a href="#install"><img alt="Agent skill for Claude Code, Codex and others" src="https://img.shields.io/badge/agent%20skill-Claude%20Code%20%C2%B7%20Codex-1D6A99?style=flat-square&labelColor=0F1115"></a>
  <a href="#what-the-build-does"><img alt="Output: animated SVG in dark and light" src="https://img.shields.io/badge/output-animated%20SVG%2C%20dark%20%2B%20light-1D6A99?style=flat-square&labelColor=0F1115"></a>
  <a href="https://github.com/ilien-dev/jano/releases"><img alt="Latest release" src="https://img.shields.io/github/v/release/ilien-dev/jano?style=flat-square&label=version&color=0F1115"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-0F1115?style=flat-square"></a>
</p>

<p align="center">
  <a href="#showroom"><b>Showroom</b></a> ·
  <a href="#install"><b>Install</b></a> ·
  <a href="#use"><b>Use</b></a> ·
  <a href="#what-you-get"><b>What you get</b></a> ·
  <a href="#the-rules-it-follows"><b>Rules</b></a> ·
  <a href="#what-the-build-does"><b>Build</b></a> ·
  <a href="#limits"><b>Limits</b></a>
</p>

---

## Showroom

Heroes made with Jano for real repositories. Each one was drawn by an agent that had only the repository and the skill. Open a repository to see its hero in place.

**[Svipall](https://github.com/ilien-dev/svipall)**: Your assistant reads the real page, not the “checking your browser” screen.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="examples/svipall/hero-dark.svg">
    <img src="examples/svipall/hero-light.svg" alt="Svipall: an assistant asks a website for a price. Without Svipall a waiting screen comes back; with it, the real page arrives." width="100%">
  </picture>
</p>

**[Muninn](https://github.com/ilien-dev/muninn)**: Your assistant remembers your decisions, and lets go of the ones you changed.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="examples/muninn/hero-dark.svg">
    <img src="examples/muninn/hero-light.svg" alt="Muninn: notes travel from a person to their assistant through a ring called the memory; a replaced decision is crossed out and put away." width="100%">
  </picture>
</p>

**[Anzu](https://github.com/ilien-dev/anzu)**: Your Kindle books, open on any reader.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="examples/anzu/hero-dark.svg">
    <img src="examples/anzu/hero-light.svg" alt="Anzu: locked Kindle books pass under the Anzu mark, lose their padlock and reach an e-reader, a phone and a tablet." width="100%">
  </picture>
</p>

**[Quirón](https://github.com/ilien-dev/quiron)**: Makes a chatbot's draft read like a person wrote it, and measures it.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="examples/quiron/hero-dark.svg">
    <img src="examples/quiron/hero-light.svg" alt="Quirón: pages written by a chatbot cross a line under a star and come out rewritten; a ruler goes from 13 of 23 to 23 of 23." width="100%">
  </picture>
</p>

**[themis](https://github.com/ilien-dev/themis)**: The page of rules you give your AI assistants, kept short and identical in both copies.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="examples/themis/hero-dark.svg">
    <img src="examples/themis/hero-light.svg" alt="themis: a long page of rules is filtered line by line; only the lines that matter come out, as two short identical pages." width="100%">
  </picture>
</p>

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
README.md               the hero placed on top, the rest untouched
```

Jano makes the image and nothing else. Your title, description, badges and links stay as you wrote them.

## The rules it follows

Two heroes made with Jano should look nothing alike, because the composition comes from the project. What they share is these rules.

- **The picture explains the repository.** The hero shows what the project does as a flow: what goes in, the steps it passes through, what comes out. An app is drawn as its own screen in skeleton form with its main flow playing, a command-line tool as its terminal and what the command causes, a service as one request followed from end to end. Someone who reads no text should still know what it does. Only facts the repository backs go in, never an invented number.
- **The logo and the name come first, and do not shout.** They sit together and stay still. The name is the largest text on the canvas, within a set range of sizes.
- **It never stops and never rewinds.** Every animation loops forever and closes on itself. A flow runs as a short cycle that ends where it began, and things leave by finishing, so it reads as a place that is running and not as a video.
- **One thing leads.** What travels through the flow carries the motion and the rest stays quiet.
- **Text stays readable.** The title and tagline stay still. Text that scrolls does it at a constant, slow speed.
- **Your identity wins.** An existing logo and colors are reused. If there are none, it picks one accent and keeps the rest neutral.

The motion rules come from people who animate SVG and interfaces for a living. They are listed with their sources in [`skills/jano/references/motion.md`](skills/jano/references/motion.md), and what to draw for each kind of repository is in [`skills/jano/references/pictures.md`](skills/jano/references/pictures.md).

## What the build does

GitHub shows an SVG as an image, so scripts and external files do not load, and a browser draws slow-moving text in small jumps. `build.py` takes care of both:

- It writes the dark and the light file from one source with a palette of named colors.
- It embeds only the letters used of Space Grotesk and JetBrains Mono, so the hero looks the same on every machine.
- It turns text that moves into outlines, which glide where live text would stutter.
- It adds the rule that stops the motion for people who ask their system for reduced motion.
- It measures the drawing before it writes anything: where each shape and each line of text lands on the canvas (text is measured with the real fonts), how far and how fast each animation travels, and whether each loop closes on itself.
- It refuses what is certainly wrong: text that runs out of its box, off the canvas or over other text, a loop that jumps back in plain sight, flashing, an animation that plays once, scripts and external files.
- It warns, with the fix, about what is probably wrong: small or low-contrast text, a name that is too large or too small, a picture that takes too little of the canvas, too many words, motion too fast to follow or too small to see, and heavy files.
- It prints the measured figures of the hero: the sizes of the name, the logo and the tagline, the share of the canvas the picture takes, the words, the loop lengths and the top speed.
- It takes two pictures when the machine has Chrome, Chromium or Edge: the loop stopped at eight moments, and the hero as GitHub shows it (both themes, a phone, blurred, and with motion off). The agent reads them, so it checks its own motion and not only one still frame.
- It writes a preview page with both themes at README width and at phone width.

`check.py`, next to it, runs the measurements alone: `uv run skills/jano/scripts/check.py assets/hero.src.svg --json`.

A hero built this way weighs between 50 and 80 KB.

## Limits

- It is an early version. It has been tried on three repositories, by one person.
- The result depends on the model that runs it. A weaker model draws a weaker hero.
- The agent sees the loop as eight stopped frames, not as motion. You are the one who judges how it feels, in the preview.
- The checks measure positions, sizes and timing. They cannot tell whether the picture is a good explanation of your project; that is still the model's work and yours.
- The pictures need a Chromium-family browser on the machine. Without one, the agent opens the preview pages with a browser tool, or you look at them.
- The fonts are fixed: Space Grotesk and JetBrains Mono. A project with its own typefaces does not get them in the hero.
- The hero is in English. The Spanish README shares it.

## Contributing

Issues and pull requests are welcome, one change at a time. [CONTRIBUTING.md](CONTRIBUTING.md) has the rules. Versions are numbered by the release workflow from the pull request titles, so nobody writes a version number.

## License

MIT, see [LICENSE](LICENSE). The two bundled fonts are under the SIL Open Font License, and their license files sit next to them in `skills/jano/assets`.
