.PHONY: install install-deps install-hooks serve build test snapshot-sitemap verify-sitemap

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

snapshot-sitemap: build
	@mkdir -p .snapshots
	cp _site/sitemap.xml .snapshots/sitemap.xml
	python3 scripts/normalize-sitemap.py .snapshots/sitemap.xml

verify-sitemap: snapshot-sitemap
	cp .snapshots/sitemap.xml /tmp/snap-sitemap.xml
	cp _site/sitemap.xml /tmp/built-sitemap.xml
	python3 scripts/normalize-sitemap.py --strip-lastmod /tmp/snap-sitemap.xml
	python3 scripts/normalize-sitemap.py --strip-lastmod /tmp/built-sitemap.xml
	diff /tmp/snap-sitemap.xml /tmp/built-sitemap.xml
