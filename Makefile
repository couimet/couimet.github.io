.PHONY: install install-deps install-hooks serve build snapshot-sitemap verify-sitemap

install: install-deps install-hooks

install-deps:
	bundle install

install-hooks:
	pre-commit install

serve:
	bundle exec jekyll serve

build:
	bundle exec jekyll build

snapshot-sitemap: build
	@mkdir -p .snapshots
	cp _site/sitemap.xml .snapshots/sitemap.xml
	python3 scripts/sort-sitemap.py .snapshots/sitemap.xml

verify-sitemap: snapshot-sitemap
	git diff --exit-code .snapshots/sitemap.xml
