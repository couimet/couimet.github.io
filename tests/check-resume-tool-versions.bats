#!/usr/bin/env bats

# Tests for scripts/check-resume-tool-versions.sh

setup() {
  REPO_ROOT="$(cd "$(dirname "$BATS_TEST_DIRNAME")" && pwd)"
  CHECK_SCRIPT="$REPO_ROOT/scripts/check-resume-tool-versions.sh"
  MOCK_DIR="$BATS_TEST_TMPDIR/mocks"
  mkdir -p "$MOCK_DIR"
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

run_check_script() {
  run env PATH="$MOCK_DIR:$PATH" bash "$CHECK_SCRIPT"
}

# --- Happy path ---

@test "succeeds when both versions match" {
  mock_npm "0.14.2" "0.14.2"
  run_check_script
  [ "$status" -eq 0 ]
  [[ "$output" == *"pinned at 0.14.2, latest is 0.14.2"* ]]
}

# --- Abort paths ---

@test "fails when json2yamlresume is behind" {
  mock_npm "0.15.0" "0.14.2"
  run_check_script
  [ "$status" -eq 1 ]
  [[ "$output" == *"ERROR: json2yamlresume is pinned at 0.14.2 but 0.15.0 is available"* ]]
  [[ "$output" == *"Update PINNED_J2Y_VERSION"* ]]
}

@test "fails when yamlresume is behind" {
  mock_npm "0.14.2" "0.15.0"
  run_check_script
  [ "$status" -eq 1 ]
  [[ "$output" == *"ERROR: yamlresume is pinned at 0.14.2 but 0.15.0 is available"* ]]
  [[ "$output" == *"Update PINNED_YR_VERSION"* ]]
}

@test "fails on first mismatch when both are behind (short-circuit)" {
  mock_npm "0.15.0" "0.15.0"
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

# --- Offline fallback ---

@test "succeeds when json2yamlresume npm query fails" {
  mock_npm "fail" "0.14.2"
  run_check_script
  [ "$status" -eq 0 ]
}

@test "succeeds when yamlresume npm query fails" {
  mock_npm "0.14.2" "fail"
  run_check_script
  [ "$status" -eq 0 ]
}

@test "succeeds when both npm queries fail" {
  mock_npm "fail" "fail"
  run_check_script
  [ "$status" -eq 0 ]
}
