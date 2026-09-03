# Repo conventions for Claude

<meta>
  <purpose>Project-specific instructions for Claude Code</purpose>
  <project>couimet.github.io - Professional portfolio</project>
  <version>2.1 - XML-structured format</version>
</meta>

---

<critical-rules>

<!-- rule-id: couimet-actions-main -->
<rule id="couimet-actions-main" priority="critical">
  <title>couimet/* GitHub Actions always use @main</title>
  <never>Pin a `couimet/*` GitHub Action to a commit SHA in workflows or composite action definitions</never>
  <do>Always reference `couimet/*` actions with `@main` to get the latest version</do>
  <rationale>The author wants these actions to auto-update across all repos</rationale>
</rule>

<!-- rule-id: tests-pin-github-actions-env -->
<rule id="tests-pin-github-actions-env" priority="critical">
  <title>Tests running scripts that read GitHub Actions ambient env vars must pin them</title>
  <never>Let a test run a script that consumes `GITHUB_REF_NAME` (or any other Actions ambient variable) without controlling that variable in the harness</never>
  <do>Unset or explicitly set the variable in the test helper (e.g. `env -u GITHUB_REF_NAME`) so the test behaves identically on every branch</do>
  <rationale>GitHub Actions exports `GITHUB_REF_NAME`: `&lt;pr_number&gt;/merge` on `pull_request` runs (the source branch lives in `GITHUB_HEAD_REF`), and `main` on push-to-main. A script that branches on it passes a strict test on the PR and silently flips to the lenient path on main, turning a green PR into a broken main (PR #194, fixed in PR #195).</rationale>
</rule>

<!-- rule-id: third-party-actions-pinned-to-sha -->
<rule id="third-party-actions-pinned-to-sha" priority="high">
  <title>Third-party GitHub Actions are pinned to a full commit SHA</title>
  <never>Use floating refs like `@v4` or `@main` for third-party actions (e.g. `actions/checkout`)</never>
  <do>Always pin third-party actions to a full commit SHA</do>
  <rationale>Version comments are omitted — Dependabot updates the SHA but not the comment, producing stale drift</rationale>
</rule>

<!-- rule-id: first-party-actions-main -->
<rule id="first-party-actions-main" priority="high">
  <title>First-party couimet/github-actions actions use @main</title>
  <do>Reference `couimet/*` actions with `@main` per the couimet-actions-main rule</do>
  <rationale>We control the repo, so breaking changes are intentional and versioned; SHAs add pin-update churn with no benefit for actions we own</rationale>
</rule>

</critical-rules>

---

<project-overview>
This repo is a Jekyll site on the Techfolio theme: the professional portfolio of Charles Ouimet. Two deployment targets share one source tree: the canonical site at https://ouimet.info (served by the couimet/ouimet.info Apache host) and https://couimet.github.io (GitHub Pages), which serves redirect stubs that forward every page to the matching ouimet.info path. Content types: articles, follow-alongs, project pages, the career changelog, and the resume. See README.md for the local-development walkthrough; the sections below carry the build, test, and deployment mechanics.
</project-overview>

---

<article-sources>
`articles/_sources/` is only for articles that were drafted **in this repo**. If an article was authored in a different repo (where it has its richer context, diagrams, history, and review), do **not** copy or mirror the markdown source here. Just add the published URL to `_data/articles.yml`.

The site links out to the canonical published URL either way, so mirroring an externally-authored source here only creates a stale duplicate.
</article-sources>

---

<tooling>

<subsection name="python">
Python packages are managed with `uv`, not `pip`. The repo-root `pyproject.toml` declares dev dependencies (currently `ruff`). `uv run &lt;tool&gt;` creates a project-local venv and runs the tool from there — each project gets its own isolated environment, and the version is pinned in `pyproject.toml`. `uv` itself must be installed and on `PATH`; `make install` validates this before proceeding.

Python linting and formatting uses `ruff` via `uv run`:

- `uv run ruff check &lt;paths&gt;` — lint (replaces py_compile, flake8, isort)
- `uv run ruff check --fix &lt;paths&gt;` — auto-fix lint violations
- `uv run ruff format &lt;paths&gt;` — format (replaces black)
</subsection>

<subsection name="linting">
```text
make lint              # build + nudge-lint + htmlproofer + ruff check
make lint-fix          # nudge-fix + ruff check --fix + ruff format
make markdownlint      # markdownlint-cli2 across all *.md
make markdownlint-fix  # markdownlint-cli2 --fix
```

- `make lint` builds `_site`, runs the `micro-projects/network-nudge` pnpm lint/format checks (`nudge-lint`), then validates the built site with `htmlproofer` (Gemfile) for broken links, missing images, missing alt attributes, and lints the Python with `uv run ruff check`.
- `make lint-fix` applies the auto-fixers: `nudge-fix`, `uv run ruff check --fix`, and `uv run ruff format`.
- Markdown is a separate target: `make markdownlint` / `make markdownlint-fix` (markdownlint-cli2, npm global, `.markdownlint-cli2.jsonc` config; MD013/MD033/MD034 are disabled — line length, inline HTML, and bare URLs match prose-style conventions).

CI runs the lint job in `.github/workflows/ci.yml` on every PR and push to main: the `couimet/github-actions/markdownlint@main` step plus `make lint`.
</subsection>

</tooling>

---

<build-and-test>
All commands run from the repo root. `make install` bootstraps a fresh checkout: verifies rbenv, uv, pre-commit, and markdownlint-cli2 are installed, runs `bundle install` (Ruby 3.4.4 per `.ruby-version`), and installs the pre-commit hooks. Day-to-day commands:

- `make serve` / `make build` — Jekyll serve/build (set `JEKYLL_ENV=production` for the production build; default is development)
- `make test` — `test-python` (validators, Python unittest, coverage lcov) followed by the bats suite over `bats-tests/*.bats`
- `make test-python` — `uv run coverage run -m unittest discover -s scripts/tests` plus coverage lcov
- `make validate-articles` / `make validate-featured-in` / `make validate-promotions` — Python validators over `_data/articles.yml`, featured-in fields, and `_data/promotions.yml`
- `make validate-site TARGET=ouimet.info` / `make validate-site TARGET=github.io` — semantic validation of a built `_site/`
- `make markdownlint` / `make markdownlint-fix` — see the tooling section
- Subprojects: `scripts/social-banner/` and `scripts/ghpages-redirect/` run pytest under `uv sync`; `micro-projects/network-nudge` runs pnpm tests via `make nudge-test`

CI (`ci.yml`) runs schema validation, `make test-python`, bats, the subproject pytest suites, network-nudge `pnpm test:coverage`, the markdownlint action plus `make lint`, and dual-config build validation — so the local pre-finish gate is `make lint` + `make test` + `make markdownlint`.
</build-and-test>

---

<config-and-deploy>
Two Jekyll configs share one source tree. `_config.yml` is canonical (url https://ouimet.info, baseurl ""). `_config_ghpages.yml` is an overlay setting `ghpages_redirect: true`, layered only in the GitHub Pages build via `bundle exec jekyll build --config _config.yml,_config_ghpages.yml --baseurl <pages-base-path>`; with that flag set, `_layouts/default.html` emits a tiny redirect stub per page instead of the full markup, preserving the path on ouimet.info. The github.io build also removes `_site/resume-full.html` and `_site/sitemap.xml` — resume-full.html has no Jekyll frontmatter, so it cannot flow through the redirect-stub layout.

Workflow roles: `ci.yml` (test/lint/build/validation gates), `main.yml` (Pages deploy, chained after `sync-resume.yml` via workflow_run so the freshest resume-full.html ships), `deploy-ouimet-info.yml` (canonical ouimet.info host), `sync-resume.yml` (regenerates `resume.yml` and `resume-full.html` from `resume.json`), `verify-sitemap.yml` (snapshot gate), `submit-sitemap.yml` (IndexNow submission), `sitemap-fix.yml` (snapshot auto-fix).
</config-and-deploy>

---

<directory-layout>
Hand-curated unless noted:

- articles/ — markdown sources; `_sources/` holds in-repo drafts only (see the article-sources rule)
- follow-alongs/ — markdown walkthrough posts
- projects/ — markdown rendered to `.html` pages (see the project-pages rule for the .htaccess 301 redirects)
- career/ — career page; `_includes/career/changelog.html` is the hand-curated per-role narrative in Keep-a-Changelog format (no generator script; `resume.json:work[]` carries the compact recruiter-facing distillation)
- _data/ — articles.yml, promotions.yml, bio.json, each with a JSON schema used by CI validation
- _layouts/ — default.html (emits redirect stubs when `ghpages_redirect` is set), home.html, project.html, follow-along.html, missingpage.html
- scripts/ — Python validators and shell scripts (sync-resume.sh, sync-ouimet-info.sh); scripts/tests/ is the Python unittest suite; scripts/social-banner/ and scripts/ghpages-redirect/ are pytest subprojects with their own uv venvs
- bats-tests/ — bats suite run by `make test`
- micro-projects/network-nudge — pnpm project with its own lint/test (`make nudge-test`)
- .snapshots/ — golden sitemap.xml refreshed by `make snapshot-sitemap` (see the sitemap rule)
- img/, css/techfolio-theme/ — site assets and theme
</directory-layout>

---

<workflow>
Work happens on `issues/<N>` branches cut from main; ephemeral working files live under `.claude-work/issues/<N>/` (gitignored — never commit or reference them in commit messages or PR descriptions). The chain: `/start-issue <url>` fetches the issue and writes an implementation plan; the user reviews the plan before any implementation; `/finish-issue` runs verification and generates the PR description. Never auto-commit — stage changes and let the user review and commit. Design questions go to a questions file via `/question`, not inline in chat.
</workflow>

---

<sitemap>
When a change adds, removes, or renames a page, run `make snapshot-sitemap` and commit the updated `.snapshots/sitemap.xml`. CI and pre-commit enforce it.
</sitemap>

---

<project-pages>
Project pages use `.html` extensions (e.g. `/projects/network-nudge.html`). Server-level 301 redirects handle the directory-style URLs (`/projects/network-nudge/`) via `.htaccess` on the `couimet/ouimet.info` Apache host.

When adding a new project page to this repo, use `/create-github-issue` to create a corresponding issue on `couimet/ouimet.info` for the `.htaccess` redirect entry. When running `/finish-issue`, explicitly link that ouimet.info issue so the redirect work isn't forgotten.
</project-pages>

---

<short-urls>
`_data/short-urls.yml` is the single source of truth for the `/s/<ID>` share pages and their social banners. Edit it, then run `make sync-short-urls` to regenerate the `s/<ID>.md` pages and `make banner-share` to redraw banners. IDs are exactly 2 base62 characters, and an ID is stable once shared — never rename or reuse one. The registry stays sorted alphabetically in base62 order; `make validate-short-urls` (part of `make test-python`) enforces the sort, the exactly-2-char charset, the `same_as` alias rules, and agreement with the generated pages.

**When adding new short IDs, defer `make banner-share` until the copy in `_data/short-urls.yml` is settled and staged.** Adding entries and running `make sync-short-urls` is cheap, but `make banner-share` renders each banner JPEG with the registry text baked in (`bannertagline` defaults to `title`), so generating banners before that text is final spends tokens and CPU on images that any later wording change forces to be redrawn and re-verified. Create the entries, regenerate the `s/<ID>.md` pages, then let the titles, descriptions, and taglines be reviewed and staged before running `make banner-share`.

**Role share-card copy conventions.** A role title reads `New role at <Company>` with the company name written exactly as it appears in the role header, since a Major or Minor changelog version is the start of a role. The description is one short line that names the role and carries only the qualifier that entry already has, either a sector (`in fulfillment and logistics`) or a team or system clause (`on the shop.app Buyer Acquisition team`, `on network management systems`); it never repeats the company the title just named and never adds a qualifier to an entry that lacks one. Descriptions feed only the `/s/<ID>.md` pages, never the banner, so a wording-only change needs `make sync-short-urls` but not `make banner-share`.

The exceptions are deliberate: the live to-Present entry may keep a present-tense product clause (Staff Backend Software Developer on the Platform team, building the platform behind agentic procurement), item-level anchors migrated in a later issue get copy framed around the item rather than the role, and The Beginning (0.1.0) stays bespoke because it is not a company role.

Sections that render on both the home page and a dedicated page (like the career changelog) carry two entries: a regular canonical ID plus a mnemonic landing alias. `_includes/heading-anchor.html` carries both via `shareId` + `homeShareId` and exposes the matching one per page; the alias inherits the canonical's title, description, and banner via `same_as` while keeping its own local `redirect_to` pointing at the home anchor.
</short-urls>

---

<resume-files>
`resume.json` (source of truth for the downloadable PDF, ATS-focused) and `_data/bio.json` (drives the Jekyll `/resume.html` page, casual/personal tone) share overlapping fields: `basics.summary`/`summaryLong`, `basics.label`, interests, and skills. When updating one, check the other for consistency. They use different tones (formal vs. casual) but should agree on facts: job titles, industry domains, years of experience, and technology keywords. The CI pipeline (`scripts/sync-resume.sh`, triggered on push to main) auto-generates `resume.yml` and `resume-full.html` from `resume.json` — never edit those generated files directly.
</resume-files>
