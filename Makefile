.PHONY: install install-prereqs install-deps install-hooks serve build test lint lint-fix snapshot-sitemap verify-sitemap extract-resume lint-resume

install: install-prereqs install-deps install-hooks

install-prereqs:
	@ok=true; \
	which uv >/dev/null 2>&1 || { echo "Missing: uv — install it: brew install uv   (or: curl -LsSf https://astral.sh/uv/install.sh | sh)"; ok=false; }; \
	which pre-commit >/dev/null 2>&1 || { echo "Missing: pre-commit — install it: brew install pre-commit   (or: pipx install pre-commit)"; ok=false; }; \
	which markdownlint-cli2 >/dev/null 2>&1 || { echo "Missing: markdownlint-cli2 — install it: npm install -g markdownlint-cli2@0.22.1"; ok=false; }; \
	$$ok || { echo; echo "Install the missing prerequisites above, then re-run make install."; exit 1; }

install-deps:
	bundle install

install-hooks:
	pre-commit install

serve:
	bundle exec jekyll serve

build:
	bundle exec jekyll build

test:
	uv run python -m unittest discover -s scripts/tests -v
	bats tests/*.bats

lint: build
	bundle exec htmlproofer _site --disable-external
	markdownlint-cli2 "**/*.md"
	uv run ruff check scripts/*.py scripts/tests/*.py

lint-fix:
	markdownlint-cli2 --fix "**/*.md"
	uv run ruff check --fix scripts/normalize-sitemap.py scripts/tests/test_normalize_sitemap.py
	uv run ruff format scripts/normalize-sitemap.py scripts/tests/test_normalize_sitemap.py

snapshot-sitemap: build
	@mkdir -p .snapshots
	cp _site/sitemap.xml .snapshots/sitemap.xml
	uv run python scripts/normalize-sitemap.py .snapshots/sitemap.xml

verify-sitemap: build
	cp .snapshots/sitemap.xml /tmp/snap-sitemap.xml
	cp _site/sitemap.xml /tmp/built-sitemap.xml
	uv run python scripts/normalize-sitemap.py --strip-lastmod /tmp/snap-sitemap.xml
	uv run python scripts/normalize-sitemap.py --strip-lastmod /tmp/built-sitemap.xml
	diff /tmp/snap-sitemap.xml /tmp/built-sitemap.xml

extract-resume:
	uv run python scripts/extract-resume-text.py

lint-resume:
	@if [ -z "$(DOCX)" ]; then \
		echo "Usage: make lint-resume DOCX=path/to/resume.docx"; \
		exit 1; \
	fi
	uv run python scripts/lint-resume-docx.py "$(DOCX)"
