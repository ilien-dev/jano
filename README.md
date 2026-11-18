<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <img src="assets/hero-light.svg" alt="Jano: your repo in, a finished README out. A repository travels a route of six stations, read the repo, ask you, plan, draw, check and cold read, leaving a tick at each one, and arrives as a finished README.md." width="100%">
  </picture>
</p>

<p align="center"><b>English</b> · <a href="README.es.md">Español</a></p>

<h1 align="center">Jano: a README that explains your repository</h1>

<p align="center"><b>Your repo goes in. A README that a stranger understands comes out,<br>
with a moving picture at the top and over each part that needs one.</b></p>

<p align="center">
  <a href="#install"><img alt="Agent skill for Claude Code, Codex and others" src="https://img.shields.io/badge/agent%20skill-Claude%20Code%20%C2%B7%20Codex-1D6A99?style=flat-square&labelColor=0F1115"></a>
  <a href="#what-you-get"><img alt="Output: README text and animated SVG pictures in dark and light" src="https://img.shields.io/badge/output-README%20%2B%20animated%20SVG-1D6A99?style=flat-square&labelColor=0F1115"></a>
  <a href="https://github.com/ilien-dev/jano/releases"><img alt="Latest release" src="https://img.shields.io/github/v/release/ilien-dev/jano?style=flat-square&label=version&color=0F1115"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-0F1115?style=flat-square"></a>
</p>

<p align="center">
  <a href="#how-it-works"><b>How it works</b></a> ·
  <a href="#what-you-get"><b>What you get</b></a> ·
  <a href="#made-with-jano"><b>Made with Jano</b></a> ·
  <a href="#install"><b>Install</b></a> ·
  <a href="#use"><b>Use</b></a> ·
  <a href="#limits"><b>Limits</b></a>
</p>

---

**Jano is a skill for your AI agent that writes and draws your repository's README.** It is for people who own a project and want its front page to explain itself. You call it once, answer a few questions, and it takes your repo along a fixed route: it reads the project, plans each section, writes the text to a size, draws a picture at the top and over the parts that need one, and checks the result before you see it.

## How it works

<p align="center"><picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/readme/coldread-dark.svg">
  <img src="assets/readme/coldread-light.svg" alt="The last check: a section picture has its words cut away, only the picture goes to a blind reader that never saw the project, the reader writes what it shows, and that answer is held against what the picture was meant to say. It matches, so the picture passes; a miss would send it back to be redrawn." width="100%">
</picture></p>

The picture above is the last stop on the route. Here is the whole of it:

1. **It reads your project.** The README, the docs and the code, until it can say who it is for and what it does, in one plain sentence.
2. **It asks you, once.** Who reads the README, what to do with anything marked unfinished and, if your project has a screen, whether one section may show a real screenshot. Then it stops asking.
3. **It plans every section.** Each one gets a job, a word budget and, if it helps, a picture.
4. **It draws and writes, then measures.** Scripts check text size, contrast, smooth loops, section length and links, and Jano fixes what they find.
5. **A stranger reads it cold.** Fresh agents that never saw your project look at each picture without its words, and at the whole README. What they get wrong is redrawn or rewritten.

## What you get

<p align="center"><picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/readme/plan-dark.svg">
  <img src="assets/readme/plan-light.svg" alt="The plan: a plan.json sheet lists the sections one per row, each with its job, a word budget bar and a mark for a picture or none. One row lights at a time, and a card names it, fills its word budget and shows whether it has a picture." width="100%">
</picture></p>

- **A README planned section by section.** Kept in `assets/readme/plan.json`, so you can read why each part is there.
- **Text sized to fit.** Each section stays within its word budget; depth that does not fit moves to a page in `docs/`.
- **A moving picture at the top**, the hero, that shows what your project does before a word is read.
- **A picture over each section that needs one**, each showing something of its own.
- **Dark and light versions of every picture.** GitHub shows each visitor the one that matches their theme.
- **Your logo and colours kept**, when you have them.

The pictures are plain SVG files that play on GitHub with nothing to install or host.

## Made with Jano

Heroes Jano drew for other projects: [Anzu](https://github.com/ilien-dev/anzu), [Sharur](https://github.com/ilien-dev/sharur) and [Svipall](https://github.com/ilien-dev/svipall). No two look alike, because no two projects do the same thing.

<p align="center">
<a href="https://github.com/ilien-dev/anzu"><picture><source media="(prefers-color-scheme: dark)" srcset="examples/anzu/hero-dark.svg"><img src="examples/anzu/hero-light.svg" alt="Anzu hero: locked Kindle books pass through the app and come out as EPUB files." width="32%"></picture></a>
<a href="https://github.com/ilien-dev/sharur"><picture><source media="(prefers-color-scheme: dark)" srcset="examples/sharur/hero-dark.svg"><img src="examples/sharur/hero-light.svg" alt="Sharur hero: one instruction file cuts a long assistant reply down to a few lines." width="32%"></picture></a>
<a href="https://github.com/ilien-dev/svipall"><picture><source media="(prefers-color-scheme: dark)" srcset="examples/svipall/hero-dark.svg"><img src="examples/svipall/hero-light.svg" alt="Svipall hero: an AI agent is turned away at a wall, gets through with a browser and receives the page." width="32%"></picture></a>
</p>

<p align="center"><b><a href="https://jano.ilien.dev/#gallery">See all seven, moving, on jano.ilien.dev</a></b></p>

The name: Jano is Spanish for Janus, the Roman god of doors, drawn with two faces. A README is the door to a repository, and every picture Jano draws has two faces too, one for dark and one for light.

## Install

One command, for Claude Code, Codex, Cursor, Gemini CLI and the other agents the [skills](https://skills.sh) CLI supports:

```sh
npx skills add ilien-dev/jano
```

Or, inside Claude Code, as a plugin:

```text
/plugin marketplace add ilien-dev/jano
/plugin install jano@jano
```

> [!IMPORTANT]
> Jano needs Python 3.9 or later. With [uv](https://docs.astral.sh/uv/) that is all; without it, run `pip install fonttools brotli` once.

## Use

<p align="center"><picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/readme/ask-dark.svg">
  <img src="assets/readme/ask-light.svg" alt="In the agent's chat you type /jano make this repository's README. Jano asks three questions one after another, each with the answer it suggests marked; you pick, a counter fills one, two, three, and a bar shows Jano carrying on alone." width="100%">
</picture></p>

Open your agent in the project and call Jano (`/jano` in Claude Code, `/jano:jano` as a plugin, `$jano` in Codex):

```text
/jano make this repository's README
```

It asks a few questions, each with the answer it would pick and why. After that it works on its own and tells you what it did; it never commits anything.

You can also ask for less:

```text
/jano make a hero for this repository
/jano make 4 alternatives for this repository's hero
```

The first draws only the picture at the top and leaves the rest of your README alone. The second opens four different heroes side by side on one page; you keep one, or say what to take from several.

## Limits

- The result depends on the AI model that runs it: a stronger model draws better pictures.
- The cold read needs an agent that can start other agents. Without one, Jano tells you the check did not run.
- Every picture uses the same two typefaces, Space Grotesk and JetBrains Mono.
- It has been used on a handful of projects so far, by one person.

## Contributing

Issues and pull requests are welcome, one change at a time. [CONTRIBUTING.md](CONTRIBUTING.md) has the rules.

## License

MIT, see [LICENSE](LICENSE). The two bundled fonts are under the SIL Open Font License, and the icon, logo and flag sets Jano draws with (Lucide, Tabler, Phosphor, Fluent, Simple Icons and more) are under MIT, ISC or CC0: every set and its notice are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
