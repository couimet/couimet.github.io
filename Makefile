.PHONY: install install-deps install-hooks serve build test lint lint-fix snapshot-sitemap verify-sitemap

install: install-deps install-hooks

install-deps:
	bundle install

install-hooks:
	pre-commit install

serve:
	bundle exec jekyll serve

build:
	bundle exec jekyll build

test:
	python3 -m unittest discover -s scripts/tests -v

lint: build
	bundle exec htmlproofer _site --disable-external
	markdownlint-cli2 "**/*.md"
	uv run ruff check scripts/normalize-sitemap.py scripts/tests/test_normalize_sitemap.py

lint-fix:
	markdownlint-cli2 --fix "**/*.md"
	uv run ruff check --fix scripts/normalize-sitemap.py scripts/tests/test_normalize_sitemap.py
	uv run ruff format scripts/normalize-sitemap.py scripts/tests/test_normalize_sitemap.py

snapshot-sitemap: build
	@mkdir -p .snapshots
	cp _site/sitemap.xml .snapshots/sitemap.xml
	python3 scripts/normalize-sitemap.py .snapshots/sitemap.xml

verify-sitemap: build
	cp .snapshots/sitemap.xml /tmp/snap-sitemap.xml
	cp _site/sitemap.xml /tmp/built-sitemap.xml
	python3 scripts/normalize-sitemap.py --strip-lastmod /tmp/snap-sitemap.xml
	python3 scripts/normalize-sitemap.py --strip-lastmod /tmp/built-sitemap.xml
	diff /tmp/snap-sitemap.xml /tmp/built-sitemap.xml
