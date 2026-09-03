# Professional Portfolio

For details on this professional portfolio, please see https://ouimet.info.

[![CI](https://github.com/couimet/couimet.github.io/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/couimet/couimet.github.io/actions/workflows/ci.yml) [![codecov](https://codecov.io/gh/couimet/couimet.github.io/branch/main/graph/badge.svg)](https://codecov.io/gh/couimet/couimet.github.io)

![Jekyll](https://img.shields.io/badge/Jekyll-CC0000?logo=jekyll&logoColor=white) ![Ruby](https://img.shields.io/badge/Ruby-CC342D?logo=ruby&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![Node.js](https://img.shields.io/badge/Node.js-5FA04E?logo=nodedotjs&logoColor=white) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)

## Local Development

See more details at https://techfolios.github.io/docs/user-guide/local-development.

Install dependencies:

```bash
make install-ruby
make install
```

Run the server:

```bash
make serve
```

### Sitemap snapshot

`.snapshots/sitemap.xml` is a tracked copy of the rendered `/sitemap.xml` so the page graph's evolution shows up in git history. CI runs `make verify-sitemap` on every PR and push to `main`, which rebuilds the site, refreshes the snapshot, and fails on `git diff --exit-code` if the build no longer matches the tracked file.

When a change adds, removes, or renames a page, refresh the snapshot before committing:

```bash
make snapshot-sitemap
```

Then commit the updated `.snapshots/sitemap.xml` alongside the page change.

The pre-commit hook (`.pre-commit-config.yaml`) runs `make snapshot-sitemap` automatically when a commit touches a sitemap-affecting path.

## Career Changelog

`_includes/career/changelog.html` is the source-of-truth narrative for my career experience, organized per role using the Keep-a-Changelog format. `resume.json:work[]` carries the compact, recruiter-facing distillation that the [Resume](#resume) pipeline converts into `resume.yml` and `resume-full.html`.

The intended editing flow is changelog-first: changes land in `_includes/career/changelog.html`, then the matching `resume.json:work[]` entry gets a synced summary and highlights per the "summary is a compact distillation of self-sufficient highlights" rule.

To enrich one role at a time, invoke the project-local skill:

```text
/career-role-enrich <role-slug>
```

Slugs match the role's `resume.json:work[].name` field with lowercase + hyphenation: `ssense`, `deliverr`, `shopify-logistics`, `flexport`, `octav`, `shopify`.

The skill walks 7 phases: resolve target → audit → intake (via `/question`) → draft (via `/note`) → review iteration → apply edits → wrap up. Style conventions (additive `Use of X` rule, role-scoped IDs, role-voice) live in the `career-style` helper skill, auto-consulted during the draft phase.

Skill files (project-local):

- `.claude/skills/career-role-enrich/SKILL.md`
- `.claude/skills/career-style/SKILL.md`

## Short URLs

`_data/short-urls.yml` is the single source of truth for the `/s/<ID>` share pages: each entry maps a base62 ID to the path it redirects to, plus the OG title/description for the share card and the optional tagline drawn on the social banner (`bannertagline` defaults to `title`). Heading anchors carry the IDs via `shareId` / `homeShareId` (see `_includes/heading-anchor.html`), and `_includes/copy-link.html` turns the emitted attribute into the share URL.

Regenerate the `s/<ID>.md` share pages from the registry (CI's `check-generated` job fails on drift):

```bash
make sync-short-urls
```

Scaffold a new registry entry with placeholder values — the ID is optional, and when omitted the script generates a random base62 ID that doesn't collide with existing entries (fill the values in, then re-run `make sync-short-urls`):

```bash
make new-short-url               # auto-generates a free base62 ID
make new-short-url ID=<base62-id>  # or choose one yourself
```

To reuse another entry's metadata and banner for a second redirect target, alias it instead: `same_as: <target-id>` — only `redirect_to` stays local. Regenerate the banner images with `make banner-share`.

## Resume

`resume.json` (JSON Resume format) is the single source of truth for the downloadable PDF, the `/resume.html` page, and the formatted `.docx` resume. Three scripts support the workflow:

### Sync pipeline

Converts `resume.json` → `resume.yml` (YAMLResume) → `resume-full.html` (styled HTML). Runs automatically on push to `main` via `.github/workflows/sync-resume.yml`. The script validates that pinned tool versions match the latest npm releases and transforms `countryCode: "CA"` to `country: Canada` on the fly for yamlresume compatibility.

```bash
./scripts/sync-resume.sh          # requires Docker and Node
```

### Docx text extraction

Generates a plain-text file from `resume.json` for copy-paste into a formatted `.docx` resume. Sections are delimited with `#`-prefixed comments. Work roles up to and including the `lastRoleBeforeEarlierExperience` marker get full bullet treatment; older roles appear in an Earlier Experience summary block with a CTA placeholder for an AI-generated narrative.

```bash
make extract-resume                # → resume-docx-content-YYYYMMDD-HHMMSS.txt
```

### Docx linting

Compares a formatted `.docx` resume against `resume.json` and flags typos, date mismatches, missing content, double punctuation, trailing whitespace, and structural issues. Uses python-docx to extract text directly from the `.docx` file.

```bash
make lint-resume DOCX=~/Desktop/.../resume.docx
```

### Tests

```bash
make test
```

Runs Python unit tests and BATS tests covering the other tools/scripts.

## Deployment

Pushes to `main` are automatically deployed to ouimet.info via `.github/workflows/deploy-ouimet-info.yml` (SSH keypair auth). See the workflow file header for required repository secrets.

The `scripts/sync-ouimet-info.sh` script is kept as a manual recovery tool for rollbacks and direct-from-release syncs.

The site is built twice from the same source: once for ouimet.info (the canonical host) and once for couimet.github.io, which only emits redirect stubs. The github.io build is triggered by `.github/workflows/main.yml` and uses the `_config_ghpages.yml` overlay to enable the `ghpages_redirect` flag, which causes `_layouts/default.html` to emit a meta-refresh + canonical-link stub instead of the full page. The ouimet.info build does not pass the overlay, so it emits the real site.

## Coverage

CI generates a coverage report for each test stack and uploads it to Codecov under a per-stack flag:

- `python` — root Python unit tests (`make test-python` → `coverage.lcov`)
- `social-banner` — pytest tests in `scripts/social-banner` (→ `coverage.lcov`)
- `ghpages-redirect` — pytest tests in `scripts/ghpages-redirect` (→ `coverage.lcov`)
- `network-nudge` — vitest tests in `micro-projects/network-nudge` (→ `coverage/lcov.info`)

Uploads run through `couimet/github-actions/codecov-upload@main` in `.github/workflows/ci.yml`. `CODECOV_TOKEN` is already configured as a repository secret; the Codecov integration must be enabled on the repo for PR status checks and comments to render.
