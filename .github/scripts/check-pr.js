#!/usr/bin/env node
// Checks a pull request against CONTRIBUTING.md: branch name, title length and description.
//
// In CI (.github/workflows/pr-rules.yml) they come from the PR_BRANCH, PR_TITLE and
// PR_BODY environment variables. Locally, before opening a PR:
//
//   node .github/scripts/check-pr.js --branch feat/outline-rotated-text \
//     --title "fix: outline text inside rotated groups" --body-file pr.md
//
// Exits with 1 and lists every problem when something does not follow the rules.

'use strict';

const fs = require('fs');

// A Conventional Commit type + / + 1 to 4 lowercase words (letters and digits) joined by
// single hyphens. The types are the ones pr-title.yml accepts in the title.
const TYPES = ['feat', 'fix', 'perf', 'refactor', 'docs', 'test', 'build', 'ci', 'chore', 'style', 'revert'];
const BRANCH = new RegExp(`^(${TYPES.join('|')})/[a-z0-9]+(-[a-z0-9]+){0,3}$`);

// Sections of .github/pull_request_template.md, in order, with their character limits.
// The limit of Evidence leaves out images, GIFs and links.
const SECTIONS = [
  { name: 'What', max: 280 },
  { name: 'Why', max: 280 },
  { name: 'How', max: 500 },
  { name: 'Evidence', max: 300, media: true },
  { name: 'Checklist' },
];

function stripComments(text) {
  return text.replace(/<!--[\s\S]*?-->/g, '');
}

function stripMedia(text) {
  return text
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '') // ![alt](url)
    .replace(/<img\b[^>]*>/gi, '') // <img src="...">
    .replace(/<video\b[\s\S]*?<\/video>/gi, '')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1') // [text](url) counts as its text
    .replace(/https?:\/\/\S+/g, ''); // bare URLs, such as uploaded attachments
}

/** Splits the body into its `## Heading` sections. */
function sections(body) {
  const found = new Map();
  let current = null;
  for (const line of stripComments(body).replace(/\r\n/g, '\n').split('\n')) {
    const heading = line.match(/^##\s+(.+?)\s*$/);
    if (heading) {
      current = heading[1];
      found.set(current, []);
    } else if (current) {
      found.get(current).push(line);
    }
  }
  return new Map([...found].map(([k, v]) => [k, v.join('\n').trim()]));
}

// The title is also checked as a Conventional Commit by pr-title.yml.
const TITLE_MAX = 72;

function check({ branch, title, body }) {
  const problems = [];

  if (title !== undefined && title.length > TITLE_MAX) {
    problems.push(`The title has ${title.length} characters; the limit is ${TITLE_MAX}.`);
  }

  if (!BRANCH.test(branch || '')) {
    problems.push(
      `Branch "${branch}" must be a type (${TYPES.join(', ')}), a slash and 1 to 4 lowercase ` +
        'words joined by hyphens, for example feat/outline-rotated-text.',
    );
  }

  const found = sections(body || '');
  for (const { name, max, media } of SECTIONS) {
    if (!found.has(name)) {
      problems.push(`The description has no "## ${name}" section. Start from .github/pull_request_template.md.`);
      continue;
    }
    const text = found.get(name);
    if (name === 'Checklist') {
      const boxes = text.match(/^\s*[-*]\s+\[[ xX]\]/gm) || [];
      const open = text.match(/^\s*[-*]\s+\[ \]/gm) || [];
      if (boxes.length === 0) problems.push('The Checklist has no boxes.');
      if (open.length > 0) problems.push(`${open.length} box(es) of the Checklist are not ticked.`);
      continue;
    }
    const counted = media ? stripMedia(text).trim() : text;
    if (text.length === 0) {
      problems.push(`"## ${name}" is empty.`);
    } else if (counted.length > max) {
      const what = media ? ' (not counting images, GIFs and links)' : '';
      problems.push(`"## ${name}" has ${counted.length} characters${what}; the limit is ${max}.`);
    }
  }

  return problems;
}

function arg(name) {
  const i = process.argv.indexOf(name);
  return i > 0 ? process.argv[i + 1] : undefined;
}

if (require.main === module) {
  const bodyFile = arg('--body-file');
  const branch = arg('--branch') ?? process.env.PR_BRANCH ?? '';
  const title = arg('--title') ?? process.env.PR_TITLE;
  const body = bodyFile ? fs.readFileSync(bodyFile, 'utf8') : process.env.PR_BODY ?? '';
  const problems = check({ branch, title, body });
  if (problems.length > 0) {
    console.error('This pull request does not follow CONTRIBUTING.md:\n');
    for (const p of problems) console.error(`- ${p}`);
    process.exit(1);
  }
  console.log('Branch name and description follow CONTRIBUTING.md.');
}

module.exports = { check, BRANCH, TYPES, SECTIONS };
