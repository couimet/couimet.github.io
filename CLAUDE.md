# Repo conventions for Claude

## Article sources (`articles/_sources/`)

`articles/_sources/` is only for articles that were drafted **in this repo**. If an article was authored in a different repo (where it has its richer context, diagrams, history, and review), do **not** copy or mirror the markdown source here. Just add the published URL to `_data/articles.yml`.

The site links out to the canonical published URL either way, so mirroring an externally-authored source here only creates a stale duplicate.

## Tooling

### Python

Python packages are managed with `uv`, not `pip`. The repo-root `pyproject.toml` declares dev dependencies (currently `ruff`). `uv run <tool>` creates a project-local venv and runs the tool from there — each project gets its own isolated environment, and the version is pinned in `pyproject.toml`. `uv` itself must be installed and on `PATH`; `make install` validates this before proceeding.

Python linting and formatting uses `ruff` via `uv run`:

- `uv run ruff check <paths>` — lint (replaces py_compile, flake8, isort)
- `uv run ruff check --fix <paths>` — auto-fix lint violations
- `uv run ruff format <paths>` — format (replaces black)

### Linting

```text
make lint      # htmlproofer + markdownlint-cli2 + ruff check
make lint-fix  # markdownlint-cli2 --fix + ruff check --fix + ruff format
```

- HTML: `htmlproofer` (Gemfile) validates built `_site/` for broken links, missing images, missing alt attributes.
- Markdown: `markdownlint-cli2` (npm global) with `.markdownlint-cli2.jsonc` config. MD013/MD033/MD034 are disabled (line length, inline HTML, and bare URLs match prose-style conventions).
- Python: `ruff` via `uv run` (repo-local venv, version pinned in `pyproject.toml`).

CI runs `make lint` on every PR and push to main via `.github/workflows/lint.yml`.

### Sitemap

When a change adds, removes, or renames a page, run `make snapshot-sitemap` and commit the updated `.snapshots/sitemap.xml`. CI and pre-commit enforce it.

### Resume files

`resume.json` (source of truth for the downloadable PDF, ATS-focused) and `_data/bio.json` (drives the Jekyll `/resume.html` page, casual/personal tone) share overlapping fields: `basics.summary`/`summaryLong`, `basics.label`, interests, and skills. When updating one, check the other for consistency. They use different tones (formal vs. casual) but should agree on facts: job titles, industry domains, years of experience, and technology keywords. The CI pipeline (`scripts/sync-resume.sh`, triggered on push to main) auto-generates `resume.yml` and `resume-full.html` from `resume.json` — never edit those generated files directly.
