.PHONY: install install-ruby install-prereqs install-deps install-hooks serve build test test-python lint lint-fix markdownlint markdownlint-fix snapshot-sitemap verify-sitemap validate-articles validate-promotions validate-site extract-resume extract-resume-linkedin sync-resume lint-resume check-resume-tool-versions resume-tool-version-json2yamlresume resume-tool-version-yamlresume nudge-test nudge-lint nudge-fix banner banner-default banner-rangelink banner-network-nudge banner-rabbit-maximizer

install: install-prereqs install-deps install-hooks

RUBY_VERSION := $(shell cat .ruby-version)

# Repo root resolved from the Makefile's own location, so the resume-tool-version-*
# targets work regardless of the directory make is invoked from.
REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

install-ruby:
	@which rbenv >/dev/null 2>&1 || { echo "Missing: rbenv — install it: brew install rbenv"; exit 1; }
	@which ruby-build >/dev/null 2>&1 || { echo "Missing: ruby-build — install it: brew install ruby-build"; exit 1; }
	@rbenv install -s $(RUBY_VERSION)
	@rbenv local $(RUBY_VERSION)

install-prereqs:
	@ok=true; \
	which uv >/dev/null 2>&1 || { echo "Missing: uv — install it: brew install uv   (or: curl -LsSf https://astral.sh/uv/install.sh | sh)"; ok=false; }; \
	which pre-commit >/dev/null 2>&1 || { echo "Missing: pre-commit — install it: brew install pre-commit   (or: pipx install pre-commit)"; ok=false; }; \
	which markdownlint-cli2 >/dev/null 2>&1 || { echo "Missing: markdownlint-cli2 — install it: npm install -g markdownlint-cli2@0.22.1"; ok=false; }; \
	if command -v nvm >/dev/null 2>&1; then \
		:; \
	elif [ -s "$${NVM_DIR:-$$HOME/.nvm}/nvm.sh" ]; then \
		. "$${NVM_DIR:-$$HOME/.nvm}/nvm.sh"; \
	else \
		echo "Missing: nvm — install it: brew install nvm (the .nvmrc file dictates the Node version)"; ok=false; \
	fi; \
	$$ok || { echo; echo "Install the missing prerequisites above, then re-run make install."; exit 1; }; \
	nvm use

install-deps:
	bundle install

install-hooks:
	pre-commit install

serve:
	bundle exec jekyll serve

build:
	bundle exec jekyll build

test: test-python
	bats bats-tests/*.bats

test-python: validate-articles validate-featured-in validate-promotions
	uv run coverage run -m unittest discover -s scripts/tests -v
	uv run coverage lcov

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
	uv run python scripts/validate-anchors.py _data/articles.yml

validate-featured-in:
	uv run python scripts/validate-featured-in.py

validate-promotions:
	uv run python scripts/validate-anchors.py _data/promotions.yml

TARGET ?= ouimet.info

validate-site:
	uv run python scripts/validate-site-semantics.py --target $(TARGET)

extract-resume:
	uv run python scripts/extract-resume-text.py

extract-resume-linkedin:
	uv run python scripts/extract-resume-linkedin.py

# Print a pinned resume tool version from package.json (exact-pinned
# devDependencies). Single source for scripts/sync-resume.sh,
# scripts/check-resume-tool-versions.sh, and the bats fixtures.
resume-tool-version-json2yamlresume:
	@node -p "require('$(REPO_ROOT)/package.json').devDependencies['json2yamlresume']"

resume-tool-version-yamlresume:
	@node -p "require('$(REPO_ROOT)/package.json').devDependencies['yamlresume']"

sync-resume:
	./scripts/sync-resume.sh

lint-resume:
	@if [ -z "$(DOCX)" ]; then \
		echo "Usage: make lint-resume DOCX=path/to/resume.docx"; \
		exit 1; \
	fi
	uv run python scripts/lint-resume-docx.py "$(DOCX)"

check-resume-tool-versions:
	./scripts/check-resume-tool-versions.sh

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
