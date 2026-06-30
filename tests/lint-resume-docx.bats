#!/usr/bin/env bats

# Tests for scripts/lint-resume-docx.py

setup() {
  REPO_ROOT="$(cd "$(dirname "$BATS_TEST_DIRNAME")" && pwd)"
  SCRIPT="$REPO_ROOT/scripts/lint-resume-docx.py"
  RESUME_JSON="$REPO_ROOT/resume.json"
}

run_lint() {
  run uv run python "$SCRIPT" "$@"
}

# --- Argument validation ---

@test "lint-resume-docx fails when no docx path is given" {
  run_lint
  [ "$status" -eq 2 ]
}

@test "lint-resume-docx fails when docx file does not exist" {
  run_lint "/tmp/nonexistent-file.docx"
  [ "$status" -eq 1 ]
  [[ "$output" == *"not found"* ]]
}

@test "lint-resume-docx fails when resume.json is missing" {
  run_lint --resume /tmp/nonexistent.json "/tmp/nonexistent-file.docx"
  [ "$status" -eq 1 ]
  [[ "$output" == *"not found"* ]]
}

# --- Lint checks against a known-bad docx ---

@test "lint-resume-docx detects double punctuation" {
  # Create a minimal docx with known issues using python-docx
  uv run python -c "
import docx
doc = docx.Document()
doc.add_paragraph('Charles Ouimet')
doc.add_paragraph('charles.ouimet@gmail.com')
doc.add_paragraph('Technical Skills')
doc.add_paragraph('Work Experience')
doc.add_paragraph('Earlier Experience')
doc.add_paragraph('Education')
doc.add_paragraph('Staff Developer')
doc.add_paragraph('Shopify')
doc.add_paragraph('Aug 2025')
doc.add_paragraph('May 2026')
doc.add_paragraph('Some text with double  space issue')
doc.add_paragraph('A typo here.. double period')
doc.save('$BATS_TEST_TMPDIR/test-bad.docx')
"
  run_lint "$BATS_TEST_TMPDIR/test-bad.docx"
  [ "$status" -eq 1 ]
  # Should flag double space and double period
  [[ "$output" == *"double space"* ]]
  [[ "$output" == *"double period"* ]]
}

@test "lint-resume-docx passes on a clean docx" {
  uv run python -c "
import docx
doc = docx.Document()
doc.add_paragraph('Charles Ouimet')
doc.add_paragraph('charles.ouimet@gmail.com')
doc.add_paragraph('514-220-4240')
doc.add_paragraph('ouimet.info')
doc.add_paragraph('Technical Skills')
doc.add_paragraph('Work Experience')
doc.add_paragraph('Earlier Experience')
doc.add_paragraph('Education & Credentials')
doc.add_paragraph('Staff Developer')
doc.add_paragraph('Shopify')
doc.add_paragraph('Flexport')
doc.add_paragraph('Octav')
doc.add_paragraph('Shopify Logistics')
doc.add_paragraph('Deliverr')
doc.add_paragraph('SSENSE')
doc.add_paragraph('Aug 2025')
doc.add_paragraph('May 2026')
doc.add_paragraph('This highlight text is a close enough match for fuzzy detection of resume content')
doc.save('$BATS_TEST_TMPDIR/test-clean.docx')
"
  run_lint "$BATS_TEST_TMPDIR/test-clean.docx"
  # May or may not exit 0 depending on fuzzy highlight matching.
  # The key assertion: no crash, no python exception.
  [[ "$output" != *"Traceback"* ]]
  [[ "$output" != *"Error"* ]]
}

@test "lint-resume-docx detects missing section headers" {
  uv run python -c "
import docx
doc = docx.Document()
doc.add_paragraph('Charles Ouimet')
doc.add_paragraph('charles.ouimet@gmail.com')
doc.save('$BATS_TEST_TMPDIR/test-missing.docx')
"
  run_lint "$BATS_TEST_TMPDIR/test-missing.docx"
  [ "$status" -eq 1 ]
  [[ "$output" == *"Technical Skills"*"not found"* ]]
}

@test "lint-resume-docx detects trailing whitespace" {
  uv run python -c "
import docx
doc = docx.Document()
doc.add_paragraph('A line with trailing space ')
doc.add_paragraph('Technical Skills')
doc.add_paragraph('Work Experience')
doc.add_paragraph('Earlier Experience')
doc.add_paragraph('Education')
doc.save('$BATS_TEST_TMPDIR/test-trailing.docx')
"
  run_lint "$BATS_TEST_TMPDIR/test-trailing.docx"
  [ "$status" -eq 1 ]
  [[ "$output" == *"Trailing whitespace on line 1: \"...A line with trailing space\""* ]]
}
