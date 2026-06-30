# Professional Portfolio

For details on this professional portfolio, please see https://ouimet.info.

## Local Development

See more details at https://techfolios.github.io/docs/user-guide/local-development.

Install dependencies:

```bash
rbenv install 3.1.4
rbenv local 3.1.4
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

## Resume

`resume.json` (JSON Resume format) is the single source of truth for the downloadable PDF, the `/resume.html` page, and the formatted `.docx` resume. Three scripts support the workflow:

### Sync pipeline

Converts `resume.json` → `resume.yml` (YAMLResume) → `resume-full.html` (styled HTML). Runs automatically on push to `main` via `.github/workflows/sync-resume.yml`. The script validates that pinned tool versions match the latest npm releases and transforms `countryCode: "CA"` to `country: Canada` on the fly for yamlresume compatibility.

```bash
./scripts/sync-resume.sh          # requires Docker
```

### Docx text extraction

Generates a plain-text file from `resume.json` for copy-paste into a formatted `.docx` resume. Sections are delimited with `# ` comments. Work roles up to and including the `lastRoleBeforeEarlierExperience` marker get full bullet treatment; older roles appear in an Earlier Experience summary block with a CTA placeholder for an AI-generated narrative.

```bash
make extract-resume                # → resume-docx-content.txt
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
