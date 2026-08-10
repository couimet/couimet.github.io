#!/usr/bin/env bats

# Tests for scripts/validate-site-semantics.py

setup() {
  REPO_ROOT="$(cd "$(dirname "$BATS_TEST_DIRNAME")" && pwd)"
  SCRIPT="$REPO_ROOT/scripts/validate-site-semantics.py"
  SITE_DIR="$BATS_TEST_TMPDIR/_site"
  mkdir -p "$SITE_DIR"
}

run_validate() {
  run uv run python "$SCRIPT" --target "$1" --site-dir "$SITE_DIR"
}

# Helper: write a minimal valid HTML page
write_page() {
  local rel="$1"
  local title="${2:-Page}"
  local canonical="${3:-}"
  local og_desc="${4:-}"
  local extra="${5:-}"

  mkdir -p "$(dirname "$SITE_DIR/$rel")"
  cat > "$SITE_DIR/$rel" <<HTML
<!DOCTYPE html>
<html>
<head>
  <title>$title</title>
HTML
  if [ -n "$canonical" ]; then
    echo "  <link rel=\"canonical\" href=\"$canonical\">" >> "$SITE_DIR/$rel"
  fi
  if [ -n "$og_desc" ]; then
    echo "  <meta property=\"og:description\" content=\"$og_desc\">" >> "$SITE_DIR/$rel"
  fi
  if [ -n "$extra" ]; then
    echo "$extra" >> "$SITE_DIR/$rel"
  fi
  cat >> "$SITE_DIR/$rel" <<HTML
</head>
<body>$extra</body>
</html>
HTML
}

# Helper: write robots.txt
write_robots() {
  echo "$1" > "$SITE_DIR/robots.txt"
}

# Helper: write sitemap.xml
write_sitemap() {
  cat > "$SITE_DIR/sitemap.xml" <<XML
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
$1
</urlset>
XML
}

# Helper: write every page the validator expects, with unique titles and
# canonicals. $1: optional redirect stub markup (for the github.io build).
write_required_pages() {
  local redirect="$1"
  write_page "index.html" "Home" "https://ouimet.info/" "Site description" "$redirect"
  write_page "404.html" "Not Found" "" "" "$redirect"
  write_page "resume.html" "Resume" "https://ouimet.info/resume" "" "$redirect"
  for p in projects/network-nudge projects/rabbit-maximizer projects/rangelink-extension; do
    write_page "$p.html" "${p##*/}" "" "" "$redirect"
  done
  write_page "articles/index.html" "Articles" "" "" "$redirect"
  write_page "projects/index.html" "Projects" "" "" "$redirect"
}

# --- Clean site passes ---

@test "validate-site: clean ouimet.info site passes all checks" {
  write_required_pages
  write_robots "User-agent: *\nAllow: /"
  write_sitemap "<url><loc>https://ouimet.info/</loc></url>"

  run_validate "ouimet.info"
  [ "$status" -eq 0 ]
}

@test "validate-site: clean github.io site passes all checks" {
  redirect='<meta http-equiv="refresh" content="0; url=https://ouimet.info/page">'
  write_required_pages "$redirect"
  write_robots "User-agent: *\nDisallow: /"

  run_validate "github.io"
  [ "$status" -eq 0 ]
}

# --- Dev URLs ---

@test "validate-site: localhost URL is caught" {
  write_page "index.html" "Home"
  echo '<a href="http://localhost:4000/">link</a>' >> "$SITE_DIR/index.html"

  run_validate "ouimet.info"
  [ "$status" -ne 0 ]
  [[ "$output" == *"localhost"* ]]
}

@test "validate-site: bare http:// URL is caught" {
  write_page "index.html" "Home"
  echo '<img src="http://example.com/img.png">' >> "$SITE_DIR/index.html"

  run_validate "ouimet.info"
  [ "$status" -ne 0 ]
  [[ "$output" == *"http://"* ]]
}

# --- Unrendered Liquid ---

@test "validate-site: unrendered Liquid markups are caught" {
  write_page "index.html" "Home"
  echo '<p>{{ page.title }}</p>' >> "$SITE_DIR/index.html"

  run_validate "ouimet.info"
  [ "$status" -ne 0 ]
  [[ "$output" == *"{{"* || "$output" == *"Liquid"* ]]
}

@test "validate-site: unrendered Liquid tags are caught" {
  write_page "index.html" "Home"
  echo '<div>{% include foo.html %}</div>' >> "$SITE_DIR/index.html"

  run_validate "ouimet.info"
  [ "$status" -ne 0 ]
  [[ "$output" == *"{%"* || "$output" == *"Liquid"* ]]
}

# --- Missing expected pages ---

@test "validate-site: missing expected page is caught" {
  write_page "index.html" "Home"
  write_robots "Allow: /"
  write_sitemap "<url><loc>https://ouimet.info/</loc></url>"

  run_validate "ouimet.info"
  [ "$status" -ne 0 ]
  [[ "$output" == *"missing expected page"* ]]
}

@test "validate-site: missing sitemap.xml on ouimet.info is caught" {
  write_required_pages
  write_robots "Allow: /"

  run_validate "ouimet.info"
  [ "$status" -ne 0 ]
  [[ "$output" == *"sitemap.xml"* ]]
}

@test "validate-site: sitemap.xml present on github.io is caught" {
  redirect='<meta http-equiv="refresh" content="0; url=https://ouimet.info/page">'
  write_required_pages "$redirect"
  write_robots "Disallow: /"
  write_sitemap "<url><loc>https://ouimet.info/</loc></url>"

  run_validate "github.io"
  [ "$status" -ne 0 ]
  [[ "$output" == *"sitemap.xml"* ]]
}

# --- Duplicate meta tags ---

@test "validate-site: duplicate titles are caught" {
  write_page "index.html" "Same Title"
  write_page "404.html" "Same Title"
  write_robots "Allow: /"
  write_sitemap "<url><loc>https://ouimet.info/</loc></url>"

  run_validate "ouimet.info"
  [ "$status" -ne 0 ]
  [[ "$output" == *"duplicate title"* ]]
}

@test "validate-site: duplicate canonical URLs are caught" {
  write_page "index.html" "Home" "https://ouimet.info/"
  write_page "404.html" "Not Found" "https://ouimet.info/"
  write_robots "Allow: /"
  write_sitemap "<url><loc>https://ouimet.info/</loc></url>"

  run_validate "ouimet.info"
  [ "$status" -ne 0 ]
  [[ "$output" == *"duplicate canonical URL"* ]]
}

# --- Target-specific checks ---

@test "validate-site: ouimet.info robots.txt with Disallow: / is caught" {
  write_page "index.html" "Home" "https://ouimet.info/" ""
  write_robots "User-agent: *\nDisallow: /"
  write_sitemap "<url><loc>https://ouimet.info/</loc></url>"

  run_validate "ouimet.info"
  [ "$status" -ne 0 ]
  [[ "$output" == *"robots.txt"* || "$output" == *"Disallow"* ]]
}

@test "validate-site: github.io robots.txt without Disallow: / is caught" {
  redirect='<meta http-equiv="refresh" content="0; url=https://ouimet.info/page">'
  write_page "index.html" "Redirect" "" "" "$redirect"
  write_robots "User-agent: *\nAllow: /"

  run_validate "github.io"
  [ "$status" -ne 0 ]
  [[ "$output" == *"robots.txt"* || "$output" == *"Disallow"* ]]
}

@test "validate-site: github.io page missing redirect stub is caught" {
  redirect='<meta http-equiv="refresh" content="0; url=https://ouimet.info/page">'
  write_required_pages "$redirect"
  # Overwrite one page without the redirect marker
  write_page "index.html" "Home" "https://ouimet.info/" ""

  write_robots "Disallow: /"
  run_validate "github.io"
  [ "$status" -ne 0 ]
  [[ "$output" == *"redirect stub"* ]]
}

@test "validate-site: sitemap.xml URLs not starting with canonical host are caught" {
  write_page "index.html" "Home" "https://ouimet.info/" ""
  write_robots "Allow: /"
  write_sitemap "<url><loc>https://wrong.example.com/page</loc></url>"

  run_validate "ouimet.info"
  [ "$status" -ne 0 ]
  [[ "$output" == *"ouimet.info"* ]]
}

@test "validate-site: page canonical URL not matching target host is caught" {
  write_page "index.html" "Home" "https://wrong.example.com/" ""
  write_robots "Allow: /"
  write_sitemap "<url><loc>https://ouimet.info/</loc></url>"

  run_validate "ouimet.info"
  [ "$status" -ne 0 ]
  [[ "$output" == *"canonical URL"* ]]
}

@test "validate-site: duplicate og:descriptions are caught" {
  write_page "index.html" "Home" "" "Same description"
  write_page "404.html" "Not Found" "" "Same description"
  write_robots "Allow: /"
  write_sitemap "<url><loc>https://ouimet.info/</loc></url>"

  run_validate "ouimet.info"
  [ "$status" -ne 0 ]
  [[ "$output" == *"duplicate og:description"* ]]
}

@test "validate-site: missing robots.txt skips target-specific robots check" {
  redirect='<meta http-equiv="refresh" content="0; url=https://ouimet.info/page">'
  write_required_pages "$redirect"
  # Don't write robots.txt — the check_target_specific branch for
  # robots_path.is_file() False should skip without error.

  run_validate "github.io"
  [ "$status" -ne 0 ]
  # check_expected_pages catches the missing file
  [[ "$output" == *"missing expected page: robots.txt"* ]]
  # check_target_specific must NOT add a second robots complaint
  [[ "$output" != *"must contain"* ]]
}

@test "validate-site: non-existent site dir exits non-zero" {
  run uv run python "$SCRIPT" --target ouimet.info --site-dir /nonexistent
  [ "$status" -ne 0 ]
}
