#!/usr/bin/env bats

# Tests for scripts/extract-resume-text.py

setup() {
  REPO_ROOT="$(cd "$(dirname "$BATS_TEST_DIRNAME")" && pwd)"
  SCRIPT="$REPO_ROOT/scripts/extract-resume-text.py"
  RESUME_JSON="$REPO_ROOT/resume.json"
  OUTPUT="$BATS_TEST_TMPDIR/output.txt"
}

run_extract() {
  run uv run python "$SCRIPT" --input "$RESUME_JSON" --output "$OUTPUT"
}

# --- Basic output ---

@test "extract-resume-text produces output file" {
  run_extract
  [ "$status" -eq 0 ]
  [ -f "$OUTPUT" ]
}

@test "extract-resume-text output contains all required section headers" {
  run_extract
  for section in "Header" "Keyword Sub-Tag" "Summary" "Technical Skills" \
                 "Work Experience" "Education & Credentials" \
                 "Volunteer" "Awards" "Personal Projects"; do
    run grep -c "^# ${section}$" "$OUTPUT"
    [ "$status" -eq 0 ]
    [ "$output" -ge 1 ]
  done
}

@test "extract-resume-text output contains name and contact" {
  run_extract
  run grep -c "Charles Ouimet" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "extract-resume-text output contains skills" {
  run_extract
  run grep -c "^Backend & Languages:" "$OUTPUT"
  [ "$status" -eq 0 ]
}

@test "extract-resume-text output contains full-bullet jobs" {
  run_extract
  for company in "Shopify" "Octav" "Flexport" "Shopify Logistics" "Deliverr" "SSENSE"; do
    run grep -c "${company}," "$OUTPUT"
    [ "$status" -eq 0 ]
    [ "$output" -ge 1 ]
  done
}

# --- Earlier Experience cutoff (marker on SSENSE) ---

@test "extract-resume-text output contains Earlier Experience section" {
  run_extract
  run grep -c "^# Earlier Experience" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "extract-resume-text lists earlier roles as plain lines, not job headers" {
  run_extract
  for company in "Zola" "AFS Technologies Inc." "Vidéotron Ltée" "Markzware Software"; do
    run grep -c "${company}" "$OUTPUT"
    [ "$status" -eq 0 ]
    [ "$output" -ge 1 ]
  done
  # Earlier roles should NOT have ## headers
  run grep -c "^## .*Zola" "$OUTPUT" || true
  [ "$status" -eq 1 ] || [ "$output" -eq 0 ]
}

@test "extract-resume-text includes AI prompt template in Earlier Experience" {
  run_extract
  run grep -c "RANGELINK" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
  run grep -c "Style reference:" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# --- Marker validation: multiple markers ---

@test "extract-resume-text fails when multiple entries have the marker" {
  # Build a temp resume.json with two markers
  python3 -c "
import json
with open('$RESUME_JSON') as f:
    data = json.load(f)
data['work'][0]['docxLastRoleBeforeEarlierExperience'] = True
data['work'][1]['docxLastRoleBeforeEarlierExperience'] = True
with open('$BATS_TEST_TMPDIR/bad-resume.json', 'w') as f:
    json.dump(data, f, indent=2)
"
  run uv run python "$SCRIPT" --input "$BATS_TEST_TMPDIR/bad-resume.json" --output "$OUTPUT"
  [ "$status" -eq 1 ]
  [[ "$output" == *"multiple work entries have docxLastRoleBeforeEarlierExperience"* ]]
}

# --- No-marker fallback: all roles get full treatment ---

@test "extract-resume-text extracts everything when no marker is set" {
  python3 -c "
import json
with open('$RESUME_JSON') as f:
    data = json.load(f)
for w in data['work']:
    w.pop('docxLastRoleBeforeEarlierExperience', None)
with open('$BATS_TEST_TMPDIR/no-marker-resume.json', 'w') as f:
    json.dump(data, f, indent=2)
"
  run uv run python "$SCRIPT" --input "$BATS_TEST_TMPDIR/no-marker-resume.json" --output "$OUTPUT"
  [ "$status" -eq 0 ]
  # Earlier Experience section should NOT appear
  run grep -c "^# Earlier Experience" "$OUTPUT" || true
  [ "$status" -eq 1 ] || [ "$output" -eq 0 ]
  # All companies should appear as ## job headers
  for company in "Zola" "Markzware Software"; do
    run grep -c "${company}," "$OUTPUT"
    [ "$status" -eq 0 ]
    [ "$output" -ge 1 ]
  done
}

# --- docxSkip: entries marked docxSkip are excluded ---

@test "extract-resume-text excludes certificates marked docxSkip" {
  run_extract
  # Claude 101 has docxSkip: true and should not appear
  run grep -c "Claude 101" "$OUTPUT" || true
  [ "$status" -eq 1 ] || [ "$output" -eq 0 ]
  # Other certificates should still appear
  run grep -c "Certified Cloud Practitioner" "$OUTPUT"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

@test "extract-resume-text includes all certificates when none are marked docxSkip" {
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
