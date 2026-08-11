.PHONY: install install-prereqs install-deps install-hooks serve build test lint lint-fix markdownlint markdownlint-fix snapshot-sitemap verify-sitemap validate-articles validate-promotions validate-site extract-resume extract-resume-linkedin sync-resume lint-resume nudge-test nudge-lint nudge-fix banner banner-default banner-rangelink banner-network-nudge banner-rabbit-maximizer

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

test: validate-articles validate-promotions
	uv run python -m unittest discover -s scripts/tests -v
	bats tests/*.bats

lint: build nudge-lint
	bundle exec htmlproofer _site --disable-external
	uv run ruff check scripts/*.py scripts/tests/*.py

lint-fix: nudge-fix
	uv run ruff check --fix scripts/*.py scripts/tests/*.py
	uv run ruff format scripts/*.py scripts/tests/*.py

markdownlint:
	markdownlint-cli2 "**/*.md"

markdownlint-fix:
	markdownlint-cli2 --fix "**/*.md"

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

validate-articles:
	uv run python scripts/validate-articles.py

validate-promotions:
	uv run python scripts/validate-promotions.py

TARGET ?= ouimet.info

validate-site:
	uv run python scripts/validate-site-semantics.py --target $(TARGET)

extract-resume:
	uv run python scripts/extract-resume-text.py

extract-resume-linkedin:
	uv run python scripts/extract-resume-linkedin.py

sync-resume:
	./scripts/sync-resume.sh

lint-resume:
	@if [ -z "$(DOCX)" ]; then \
		echo "Usage: make lint-resume DOCX=path/to/resume.docx"; \
		exit 1; \
	fi
	uv run python scripts/lint-resume-docx.py "$(DOCX)"

nudge-test:
	cd micro-projects/network-nudge && pnpm test

nudge-lint:
	cd micro-projects/network-nudge && pnpm lint && pnpm format

nudge-fix:
	cd micro-projects/network-nudge && pnpm fix

banner: banner-default banner-rangelink banner-network-nudge banner-rabbit-maximizer

banner-default:
	cd scripts/social-banner && uv run python generate.py

banner-rangelink:
	cd scripts/social-banner && uv run python generate_rangelink.py

banner-network-nudge:
	cd scripts/social-banner && uv run python generate_network_nudge.py

banner-rabbit-maximizer:
	cd scripts/social-banner && uv run python generate_rabbit_maximizer.py
