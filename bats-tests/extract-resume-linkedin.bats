#!/usr/bin/env bats

# Tests for scripts/extract-resume-linkedin.py

setup() {
  REPO_ROOT="$(cd "$(dirname "$BATS_TEST_DIRNAME")" && pwd)"
  SCRIPT="$REPO_ROOT/scripts/extract-resume-linkedin.py"
  RESUME_JSON="$REPO_ROOT/resume.json"
  OUTPUT="$BATS_TEST_TMPDIR/output.txt"
}

run_extract() {
  run uv run python "$SCRIPT" --input "$RESUME_JSON" --output "$OUTPUT"
}

# --- Basic output ---

@test "extract-resume-linkedin produces output file" {
  run_extract
  [ "$status" -eq 0 ]
  [ -f "$OUTPUT" ]
}

@test "extract-resume-linkedin output contains all required section headers" {
  run_extract
  for section in "Headline" "About" "Experience" "Skills" \
                 "Education" "Projects" "Volunteer" "Awards"; do
    run grep -c "^# ${section}$" "$OUTPUT"
    [ "$status" -eq 0 ]
    [ "$output" -ge 1 ]
  done
}

@test "extract-resume-linkedin output does NOT contain docx-only sections" {
  run_extract
  for section in "Header" "Keyword Sub-Tag" "Earlier Experience" \
                 "Personal Projects" "Education & Credentials"; do
    run grep -c "^# ${section}$" "$OUTPUT" || true
    [ "$status" -eq 1 ] || [ "$output" -eq 0 ]
  done
}

@test "extract-resume-linkedin output contains headline with basics.label" {
  run_extract
  run grep -c "^Staff Developer$" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "extract-resume-linkedin output contains About summary" {
  run_extract
  run grep -ci "Staff Developer with over" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "extract-resume-linkedin output contains skills" {
  run_extract
  run grep -c "^Backend & Languages:" "$OUTPUT"
  [ "$status" -eq 0 ]
}

# --- Experience: all roles, no cutoff ---

@test "extract-resume-linkedin output contains all work entries including post-marker roles" {
  run_extract
  for company in "Shopify," "Octav," "Flexport," "Shopify Logistics," "Deliverr," \
                 "SSENSE," "Zola," "AFS Technologies Inc." "Vidéotron Ltée" "Markzware Software"; do
    run grep -c "${company}" "$OUTPUT"
    [ "$status" -eq 0 ]
    [ "$output" -ge 1 ]
  done
}

@test "extract-resume-linkedin all work entries have ## position headers" {
  run_extract
  for position in "Staff Developer" "Principal Developer" "Senior Staff Developer" \
                 "Senior Developer" "Tech Lead" "Architect"; do
    run grep -c "^## ${position}$" "$OUTPUT"
    [ "$status" -eq 0 ]
    [ "$output" -ge 1 ]
  done
}

@test "extract-resume-linkedin does NOT contain Earlier Experience section" {
  run_extract
  run grep -c "^# Earlier Experience" "$OUTPUT" || true
  [ "$status" -eq 1 ] || [ "$output" -eq 0 ]
}

@test "extract-resume-linkedin does NOT contain AI prompt template" {
  run_extract
  run grep -c "RANGELINK" "$OUTPUT" || true
  [ "$status" -eq 1 ] || [ "$output" -eq 0 ]
  run grep -c "Style reference:" "$OUTPUT" || true
  [ "$status" -eq 1 ] || [ "$output" -eq 0 ]
}

@test "extract-resume-linkedin experience entries include summary paragraphs" {
  run_extract
  run grep -c "Focused on cross-cutting initiatives across the post-acquisition Flexport" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "extract-resume-linkedin highlights have bullet prefixes" {
  run_extract
  # The script adds bullet prefixes for LinkedIn copy-paste
  run grep -c "^• " "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# --- docxSkip: entries marked docxSkip are excluded ---

@test "extract-resume-linkedin excludes certificates marked docxSkip" {
  run_extract
  run grep -c "Claude 101" "$OUTPUT" || true
  [ "$status" -eq 1 ] || [ "$output" -eq 0 ]
  run grep -c "Certified Cloud Practitioner" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "extract-resume-linkedin includes all certificates when none are marked docxSkip" {
  python3 -c "
import json
with open('$RESUME_JSON') as f:
    data = json.load(f)
for cert in data['certificates']:
    cert.pop('docxSkip', None)
with open('$BATS_TEST_TMPDIR/no-skip-resume.json', 'w') as f:
    json.dump(data, f, indent=2)
"
  run uv run python "$SCRIPT" --input "$BATS_TEST_TMPDIR/no-skip-resume.json" --output "$OUTPUT"
  [ "$status" -eq 0 ]
  run grep -c "Claude 101" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# --- Education, Projects, Volunteer, Awards sections present ---

@test "extract-resume-linkedin output contains education entries" {
  run_extract
  run grep -c "UQAM" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "extract-resume-linkedin output contains project entries" {
  run_extract
  run grep -c "my-claude-skills" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "extract-resume-linkedin output contains volunteer entries" {
  run_extract
  run grep -c "Escadron 96" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "extract-resume-linkedin output contains award entries" {
  run_extract
  run grep -c "Rookie Rockstar" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# --- Timestamped default output filename ---

@test "extract-resume-linkedin default output uses timestamped filename" {
  cd "$BATS_TEST_TMPDIR"
  run uv run python "$SCRIPT" --input "$RESUME_JSON"
  [ "$status" -eq 0 ]
  count=$(find . -maxdepth 1 -name 'resume-linkedin-content-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9].txt' | wc -l)
  [ "$count" -eq 1 ]
}

@test "extract-resume-linkedin default output file has section headers" {
  cd "$BATS_TEST_TMPDIR"
  run uv run python "$SCRIPT" --input "$RESUME_JSON"
  [ "$status" -eq 0 ]
  output_file=$(find . -maxdepth 1 -name 'resume-linkedin-content-*.txt' | head -1)
  [ -n "$output_file" ]
  run grep -c "^# Experience$" "$output_file"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "extract-resume-linkedin explicit --output overrides timestamped default" {
  run_extract
  [ "$status" -eq 0 ]
  [ -f "$OUTPUT" ]
  [ "$(basename "$OUTPUT")" = "output.txt" ]
}

@test "extract-resume-linkedin two runs produce different default filenames" {
  cd "$BATS_TEST_TMPDIR"
  uv run python "$SCRIPT" --input "$RESUME_JSON"
  sleep 1
  uv run python "$SCRIPT" --input "$RESUME_JSON"
  count=$(find . -maxdepth 1 -name 'resume-linkedin-content-*.txt' | wc -l)
  [ "$count" -eq 2 ]
}

# --- Error handling ---

@test "extract-resume-linkedin fails when resume.json is missing" {
  run uv run python "$SCRIPT" --input "$BATS_TEST_TMPDIR/nonexistent.json" --output "$OUTPUT"
  [ "$status" -eq 1 ]
  [[ "$output" == *"ERROR"* ]]
  [[ "$output" == *"not found"* ]]
}

# --- Education output format ---

@test "extract-resume-linkedin education format: area, institution (year)" {
  run_extract
  run grep -c "Computer Science, Université du Québec à Montréal (UQAM) (2001)" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# --- Volunteer output format ---

@test "extract-resume-linkedin volunteer format: organization — position (dates)" {
  run_extract
  run grep -c "CIP4 — Chair of Preflight Sub-committee (Jan 2002 – Dec 2005)" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# --- Awards output format ---

@test "extract-resume-linkedin award format: title, awarder (date)" {
  run_extract
  run grep -c "Rookie Rockstar, Deliverr — Engie Awards (2022)" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}
