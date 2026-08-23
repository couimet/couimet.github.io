#!/usr/bin/env bats

# Tests for scripts/resume_utils.py

setup() {
  REPO_ROOT="$(cd "$(dirname "$BATS_TEST_DIRNAME")" && pwd)"
  UTILS="$REPO_ROOT/scripts/resume_utils.py"
}

run_util() {
  run env PYTHONPATH="$REPO_ROOT/scripts" uv run python -c "$1"
}

# --- fmt_date ---

@test "fmt_date converts ISO date to Mon YYYY" {
  run_util "from resume_utils import fmt_date; print(fmt_date('2025-08-01'))"
  [ "$status" -eq 0 ]
  [ "$output" = "Aug 2025" ]
}

@test "fmt_date handles January" {
  run_util "from resume_utils import fmt_date; print(fmt_date('2024-01-15'))"
  [ "$status" -eq 0 ]
  [ "$output" = "Jan 2024" ]
}

@test "fmt_date handles December" {
  run_util "from resume_utils import fmt_date; print(fmt_date('2023-12-31'))"
  [ "$status" -eq 0 ]
  [ "$output" = "Dec 2023" ]
}

# --- validate_marker: happy path ---

@test "validate_marker returns empty list when no marker is set" {
  run_util "
from resume_utils import validate_marker
work = [{'name': 'A'}, {'name': 'B'}]
print(validate_marker(work))
"
  [ "$status" -eq 0 ]
  [ "$output" = "[]" ]
}

@test "validate_marker returns index when one marker is set" {
  run_util "
from resume_utils import validate_marker
work = [{'name': 'A'}, {'name': 'B', 'docxLastRoleBeforeEarlierExperience': True}]
print(validate_marker(work))
"
  [ "$status" -eq 0 ]
  [ "$output" = "[1]" ]
}

# --- validate_marker: error path ---

@test "validate_marker exits with error when multiple markers are set" {
  run_util "
from resume_utils import validate_marker
work = [
    {'name': 'A', 'docxLastRoleBeforeEarlierExperience': True},
    {'name': 'B', 'docxLastRoleBeforeEarlierExperience': True},
]
result = validate_marker(work)
"
  [ "$status" -eq 1 ]
  [[ "$output" == *"multiple work entries have docxLastRoleBeforeEarlierExperience"* ]]
}

# --- get_cutoff ---

@test "get_cutoff returns len(work) when no marker is set" {
  run_util "
from resume_utils import get_cutoff
work = [{'name': 'A'}, {'name': 'B'}, {'name': 'C'}]
print(get_cutoff(work))
"
  [ "$status" -eq 0 ]
  [ "$output" = "3" ]
}

@test "get_cutoff returns marker index when one marker is set" {
  run_util "
from resume_utils import get_cutoff
work = [
    {'name': 'A'},
    {'name': 'B', 'docxLastRoleBeforeEarlierExperience': True},
    {'name': 'C'},
    {'name': 'D'},
]
print(get_cutoff(work))
"
  [ "$status" -eq 0 ]
  [ "$output" = "1" ]
}

@test "get_cutoff also validates single-marker invariant" {
  run_util "
from resume_utils import get_cutoff
work = [
    {'name': 'A', 'docxLastRoleBeforeEarlierExperience': True},
    {'name': 'B', 'docxLastRoleBeforeEarlierExperience': True},
]
get_cutoff(work)
"
  [ "$status" -eq 1 ]
  [[ "$output" == *"multiple work entries have docxLastRoleBeforeEarlierExperience"* ]]
}

# --- MONTH_ABBR ---

@test "MONTH_ABBR has 13 entries and correct abbreviations" {
  run_util "
from resume_utils import MONTH_ABBR
print(len(MONTH_ABBR))
print(','.join(MONTH_ABBR[1:]))
"
  [ "$status" -eq 0 ]
  first_line=$(echo "$output" | head -1)
  second_line=$(echo "$output" | tail -1)
  [ "$first_line" = "13" ]
  [ "$second_line" = "Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec" ]
}
