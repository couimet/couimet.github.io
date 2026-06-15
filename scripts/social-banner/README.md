# social-banner

Reproducible social banner generation for ouimet.info. Two scripts produce
the JPGs that show up as `og:image` previews when pages are shared.

| Script | Output |
| --- | --- |
| `generate.py` | `img/social-banner.jpg` — the default banner using `_data/bio.json` |
| `generate_rangelink.py` | `img/social-banner-rangelink.jpg` — the project-specific banner for `projects/rangelink-extension.md` |

## Setup

Requires [uv](https://docs.astral.sh/uv/) (one-line installer at the link).
`uv` reads `.python-version` and installs Python 3.12 automatically if
needed.

From this directory:

```sh
uv sync --extra dev
```

That creates `.venv/` with the exact dependency tree captured in `uv.lock`.

## Regenerate banners

```sh
uv run python generate.py
uv run python generate_rangelink.py
```

The scripts write to `../../img/` (repo root `img/`).

## Run tests

```sh
uv run pytest tests/
```

The suite covers helpers (`derive_bannertitle`, `wrap_line`, `load_font`),
end-to-end banner generation against fixtures, and an image diff against
committed golden banners.

## Update golden images

When the banner design intentionally changes (new palette, layout, font
size), regenerate the goldens once and commit them:

```sh
UPDATE_GOLDEN=1 uv run pytest tests/
```

The `assert_matches_golden` helper sees the env var and overwrites the
golden files instead of comparing. Re-run without the flag to confirm the
new goldens stick.

## CI

`.github/workflows/python-tests.yml` runs the same `uv sync --frozen` and
`uv run pytest tests/` on every PR and on push to `main`, gated on changes
under `scripts/social-banner/**`.
