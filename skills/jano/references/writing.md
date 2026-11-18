# Writing the README

`readme.py rules` has the numbers; this file has the reasons and the forms. The README is read
by someone who arrived from a link, has never seen the project, and decides in a minute whether
to keep reading. Each section answers one question they have, in the order they have it: what is
it, what do I get, does it work, how do I start, what if.

## Voice

Plain words for a general audience: the words the reader would use for their own problem, not the
project's internal names. For a technical audience the trade's words are fine, still in short
sentences. Say what it does, not how good it is: "cuts each reply to a few lines" over "a
powerful, blazing-fast solution". A figure only when the repo backs it, with where it comes from.
Every claim in a section is one its scene or its code backs.

Keep the README's language. A translation says the same things in the same order, with the same
pictures and alerts, in that language's own words.

## The top block

In this order, centred:

```html
<p align="center"><picture>...the hero...</picture></p>
<p align="center"><b>English</b> · <a href="README.es.md">Español</a></p>   (only with translations)
<h1 align="center">Name: what it is, in a few words</h1>
<p align="center"><b>The key phrase of the hero, or the sentence of step 1.</b></p>
<p align="center">badges: what it runs in, version, licence; one style; 6 at most</p>
<p align="center"><a href="#...">Section</a> · ... </p>   (a link row to the sections, when there are 6 or more)
```

Then the lead, not centred: 30 to 110 words, starting with a bold sentence that says what it is
(**Svipall reads any web page for your AI agent.**), then for whom and what they get. No alert
and no picture in the lead; the hero was the picture. The bold line under the title says
what the title does not; when the hero's key phrase would repeat the title, write another.

The text may name real sites and products when it links them; the pictures never draw a real
third party (`example.com`, `news.example`).

## A section

```markdown
## Heading in plain words

<p align="center"><picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/readme/<name>-dark.svg">
  <img src="assets/readme/<name>-light.svg" alt="What the picture shows, step by step" width="100%">
</picture></p>

Text that says what the picture showed, and what it could not.
```

The heading names the reader's question or what they get ("What you get", "How it works",
"Install"), not the project's internals. No emoji in headings: the colour is in the pictures.

## The Markdown elements, and when

| Element | Use it for | Not for |
|---|---|---|
| **bold** | the lead-in of a list item or a paragraph, 8 words at most, one per paragraph | emphasis scattered through sentences |
| *italic* | a term on first use, a title; two per section at most | emphasis |
| `code` | what a person types or sees: commands, file names, flags, keys of a config | product names, ordinary words |
| fenced code with a language | every command and every snippet: ```bash, ```json, ```python | output that is prose |
| numbered list | steps in an order (install, how it works) | things without order |
| bulleted list | features, audiences, limits, 7 items at most in sight | one or two items (write a sentence) |
| table | comparisons, results, options, requirements, 6 columns and 10 rows at most in sight | features, steps, prose |
| `> [!NOTE]` | worth knowing and easy to miss | anything decorative |
| `> [!TIP]` | a better or faster way | the main path |
| `> [!IMPORTANT]` | what the reader needs to succeed (a requirement) | marketing |
| `> [!WARNING]` | what can break, and how to avoid it | limits stated plainly in their section |
| `> [!CAUTION]` | what can lose data or cost money | anything milder |
| `<details><summary><b>...</b></summary>` | FAQ entries, other install paths, full lists of commands or options | the main install path, anything every reader needs |
| `<kbd>` | keys to press: <kbd>Ctrl</kbd>+<kbd>C</kbd> | commands |
| `<p align="center">` | the top block and the pictures | body text |
| `---` | once, between the top block and the lead | between every section |
| link to `docs/` | depth a section cannot hold: architecture, every option, full benchmarks | the main path |

Three alerts in the whole README at most, one per section, each in a role that allows it; an
alert that shows up everywhere stops being read. GitHub removes `style=`, `color=` and `<font>`:
colour comes from the scenes, the badges and the alerts, never from the text.

## When the detail goes to docs/

A section keeps what every reader of this audience needs; the rest moves. When the true content
of a section is longer than its role allows, keep a summary of three to six lines and a link:
"The full list of options is in [docs/options.md](docs/options.md)." When a file in `docs/` already covers that topic, extend
it; otherwise write a new one, as a page
of its own (a title, a sentence that says what it covers, then the content), from the README's
current text, so nothing true is lost. Typical moves: architecture and internals, every command
or option, benchmarks in full, the long FAQ, development and release notes. A technical audience
keeps more in the README than a general one, and still sends the reference to docs/.

## Before you check

Read the README from top to bottom as the stranger of the judges' step: is any section there
for the project rather than for the reader? Does any picture say what its section's text then
says again in full? Does every claim have its file? Then run `readme.py check`.
