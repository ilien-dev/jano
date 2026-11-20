## Notes for Jano

- **Evidence for heroes.** A change to how heroes look or move needs a GIF or a screenshot of a
  hero built with it, before and after when something changed. Build one with
  `uv run skills/jano/scripts/build.py tests/fixture/assets/hero.src.svg`.
- **`skills/jano/SKILL.md` is short on purpose.** It is loaded whole every time someone runs the
  skill, so a PR that adds a rule says what went wrong without it. A change to it is a `feat` or
  a `fix`, never `docs`.
- **Tests.** A change to a script in `skills/jano/scripts/` comes with a test in `tests/run.py`.
- **Languages.** Code, comments and docs are in English. A change to `README.md` goes with the
  same change in `README.es.md` and its scenes in `assets/es/`.
