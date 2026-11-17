# Changelog

## [0.4.0](https://github.com/ilien-dev/jano/compare/v0.3.0...v0.4.0) (2026-11-17)


### ⚠ BREAKING CHANGES

* draw the repository's flow and measure the hero in the build ([#8](https://github.com/ilien-dev/jano/issues/8))

### Features

* draw the repository's flow and measure the hero in the build ([#8](https://github.com/ilien-dev/jano/issues/8)) ([1a39e45](https://github.com/ilien-dev/jano/commit/1a39e4568f97c0a59a525efae154ef2c27fde5de))

## [0.3.0](https://github.com/ilien-dev/jano/compare/v0.2.1...v0.3.0) (2026-11-17)


### Features

* draw heroes anyone can follow, technical or not ([#2](https://github.com/ilien-dev/jano/issues/2)) ([af51f35](https://github.com/ilien-dev/jano/commit/af51f356a78097ce88bc6659dedef6ac3ddf9035))


### Bug Fixes

* allow a web address written as text in a hero ([#4](https://github.com/ilien-dev/jano/issues/4)) ([19ea70d](https://github.com/ilien-dev/jano/commit/19ea70db297dca1c452969d490370d4954a560e1))
* give each source its own preview page ([#3](https://github.com/ilien-dev/jano/issues/3)) ([e0ef3a0](https://github.com/ilien-dev/jano/commit/e0ef3a02315f1231348b363082130ed883ea5148))

## [0.2.1](https://github.com/ilien-dev/jano/compare/v0.2.0...v0.2.1) (2026-11-17)


### Bug Fixes

* quote the skill description so installers can read it ([303eac5](https://github.com/ilien-dev/jano/commit/303eac5b240ab70018eb19957ba3c8e164abe6b2))

## 0.2.0

- The skill now makes only the hero image and places it in the README. It no longer writes
  the title, slogan, description, badges or menu.

## 0.1.0

First release.

- The skill: logo, animated SVG hero in dark and light, and the README header.
- `build.py`: one source file becomes both themes, with the fonts embedded, moving text
  turned into outlines, and checks for looping, contrast, size and external files.
