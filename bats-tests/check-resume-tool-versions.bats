#!/usr/bin/env bats

# Tests for scripts/check-resume-tool-versions.sh

setup() {
  REPO_ROOT="$(cd "$(dirname "$BATS_TEST_DIRNAME")" && pwd)"
  CHECK_SCRIPT="$REPO_ROOT/scripts/check-resume-tool-versions.sh"
  MOCK_DIR="$BATS_TEST_TMPDIR/mocks"
  mkdir -p "$MOCK_DIR"
  # Pinned versions come from the same Makefile targets the script under test uses.
  PINNED_J2Y_VERSION="$(make -s -C "$REPO_ROOT" resume-tool-version-json2yamlresume)"
  PINNED_YR_VERSION="$(make -s -C "$REPO_ROOT" resume-tool-version-yamlresume)"
}

# --- Helpers ---

# Create a mock npm that echoes the given versions for json2yamlresume and yamlresume.
# Pass "fail" as a version to make npm exit 1 (simulating offline / registry down).
# Each invocation is logged to $MOCK_DIR/npm-calls.log so tests can assert which
# npm commands were (or were not) called.
mock_npm() {
  local j2y="$1" yr="$2"
  cat > "$MOCK_DIR/npm" << EOF
#!/usr/bin/env bash
echo "\$*" >> "$MOCK_DIR/npm-calls.log"
case "\$*" in
  *json2yamlresume*)
    [ "$j2y" = "fail" ] && exit 1
    echo "$j2y"
    ;;
  *yamlresume*)
    [ "$yr" = "fail" ] && exit 1
    echo "$yr"
    ;;
  *) exit 1 ;;
esac
EOF
  chmod +x "$MOCK_DIR/npm"
}

# Version one patch ahead of the pinned one. The "behind" fixtures use this so
# they stay valid when package.json bumps without editing this file:
# the version check compares strings, and patch+1 keeps the messages readable
# ("pinned at 0.15.0 but 0.15.1 is available").
behind_version() {
  local v="$1"
  echo "${v%.*}.$(( ${v##*.} + 1 ))"
}

run_check_script() {
  # $1 (optional): GITHUB_REF_NAME to export for the run. When omitted, unset it
  # so the strict-default tests are hermetic: CI on main exports
  # GITHUB_REF_NAME=main, which would flip them to non-blocking warnings.
  local ref="${1:-}"
  if [ -n "$ref" ]; then
    run env GITHUB_REF_NAME="$ref" PATH="$MOCK_DIR:$PATH" bash "$CHECK_SCRIPT"
  else
    run env -u GITHUB_REF_NAME PATH="$MOCK_DIR:$PATH" bash "$CHECK_SCRIPT"
  fi
}

# --- Happy path ---

@test "resume tool pins in package.json are exact (no caret or tilde)" {
  [[ "$PINNED_J2Y_VERSION" != *"^"* && "$PINNED_J2Y_VERSION" != *"~"* ]]
  [[ "$PINNED_YR_VERSION" != *"^"* && "$PINNED_YR_VERSION" != *"~"* ]]
}

@test "succeeds when both versions match" {
  mock_npm "$PINNED_J2Y_VERSION" "$PINNED_YR_VERSION"
  run_check_script
  [ "$status" -eq 0 ]
  [[ "$output" == *"pinned at $PINNED_J2Y_VERSION, latest is $PINNED_J2Y_VERSION"* ]]
}

# --- Abort paths ---

@test "fails when json2yamlresume is behind" {
  mock_npm "$(behind_version "$PINNED_J2Y_VERSION")" "$PINNED_YR_VERSION"
  run_check_script
  [ "$status" -eq 1 ]
  [[ "$output" == *"ERROR: json2yamlresume is pinned at $PINNED_J2Y_VERSION but $(behind_version "$PINNED_J2Y_VERSION") is available"* ]]
  [[ "$output" == *"Update PINNED_J2Y_VERSION"* ]]
}

@test "fails when yamlresume is behind" {
  mock_npm "$PINNED_J2Y_VERSION" "$(behind_version "$PINNED_YR_VERSION")"
  run_check_script
  [ "$status" -eq 1 ]
  [[ "$output" == *"ERROR: yamlresume is pinned at $PINNED_YR_VERSION but $(behind_version "$PINNED_YR_VERSION") is available"* ]]
  [[ "$output" == *"Update PINNED_YR_VERSION"* ]]
}

@test "fails on first mismatch when both are behind (short-circuit)" {
  mock_npm "$(behind_version "$PINNED_J2Y_VERSION")" "$(behind_version "$PINNED_YR_VERSION")"
  run_check_script
  [ "$status" -eq 1 ]
  [[ "$output" == *"ERROR: json2yamlresume"* ]]
  [[ "$output" != *"ERROR: yamlresume"* ]]
  # Assert only one npm call was made (json2yamlresume short-circuits before yamlresume).
  # "yamlresume" is a substring of "json2yamlresume", so match the package name with a
  # leading space to avoid false positives.
  run cat "$MOCK_DIR/npm-calls.log"
  [[ "$output" == *" json2yamlresume"* ]]
  [[ "$output" != *" yamlresume "* ]]
}

# --- Main branch: warn, don't fail ---

@test "warns but succeeds on main when json2yamlresume is behind" {
  mock_npm "$(behind_version "$PINNED_J2Y_VERSION")" "$PINNED_YR_VERSION"
  run_check_script main
  [ "$status" -eq 0 ]
  [[ "$output" == *"WARNING"* ]]
  [[ "$output" != *"ERROR"* ]]
}

@test "warns but succeeds on main when yamlresume is behind" {
  mock_npm "$PINNED_J2Y_VERSION" "$(behind_version "$PINNED_YR_VERSION")"
  run_check_script main
  [ "$status" -eq 0 ]
  [[ "$output" == *"WARNING"* ]]
}

@test "still fails on a feature branch when json2yamlresume is behind" {
  mock_npm "$(behind_version "$PINNED_J2Y_VERSION")" "$PINNED_YR_VERSION"
  run_check_script issues/193
  [ "$status" -eq 1 ]
  [[ "$output" == *"ERROR"* ]]
}

# --- Offline fallback ---

@test "succeeds when json2yamlresume npm query fails" {
  mock_npm "fail" "$PINNED_YR_VERSION"
  run_check_script
  [ "$status" -eq 0 ]
}

@test "succeeds when yamlresume npm query fails" {
  mock_npm "$PINNED_J2Y_VERSION" "fail"
  run_check_script
  [ "$status" -eq 0 ]
}

@test "succeeds when both npm queries fail" {
  mock_npm "fail" "fail"
  run_check_script
  [ "$status" -eq 0 ]
}
