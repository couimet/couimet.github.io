#!/usr/bin/env bats

# Tests for scripts/sync-resume.sh

setup() {
  REPO_ROOT="$(cd "$(dirname "$BATS_TEST_DIRNAME")" && pwd)"
  SYNC_SCRIPT="$REPO_ROOT/scripts/sync-resume.sh"
  MOCK_DIR="$BATS_TEST_TMPDIR/mocks"
  mkdir -p "$MOCK_DIR"
}

# --- Helpers ---

# Create a mock npm that echoes the given versions for json2yamlresume and yamlresume.
# Pass "fail" as a version to make npm exit 1 (simulating offline / registry down).
mock_npm() {
  local j2y="$1" yr="$2"
  cat > "$MOCK_DIR/npm" << EOF
#!/usr/bin/env bash
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

# Create a no-op mock docker that touches resume.yml (enough to satisfy the script).
mock_docker() {
  cat > "$MOCK_DIR/docker" << 'EOF'
#!/usr/bin/env bash
touch resume.yml
EOF
  chmod +x "$MOCK_DIR/docker"
}

# Full mocks: both npm and docker stubbed.
mock_all() {
  mock_npm "${1:-0.13.1}" "${2:-0.13.1}"
  mock_docker
}

run_script() {
  run env PATH="$MOCK_DIR:$PATH" bash "$SYNC_SCRIPT"
}

# --- Version check: happy path ---

@test "version check passes when both packages match pinned versions" {
  mock_all "0.13.1" "0.13.1"
  run_script
  [ "$status" -eq 0 ]
}

# --- Version check: abort paths ---

@test "version check aborts when json2yamlresume is behind latest" {
  mock_npm "0.14.0" "0.13.1"
  run_script
  [ "$status" -eq 1 ]
  [[ "$output" == *"json2yamlresume is pinned at 0.13.1 but 0.14.0 is available"* ]]
  [[ "$output" == *"Update PINNED_J2Y_VERSION"* ]]
}

@test "version check aborts when yamlresume is behind latest" {
  mock_npm "0.13.1" "0.14.0"
  run_script
  [ "$status" -eq 1 ]
  [[ "$output" == *"yamlresume is pinned at 0.13.1 but 0.14.0 is available"* ]]
  [[ "$output" == *"Update PINNED_YR_VERSION"* ]]
}

@test "version check aborts when both packages are behind latest" {
  mock_npm "0.14.0" "0.14.0"
  run_script
  [ "$status" -eq 1 ]
  # Should fail on the first check (json2yamlresume) and never reach yamlresume
  [[ "$output" == *"json2yamlresume is pinned at 0.13.1 but 0.14.0 is available"* ]]
}

# --- Version check: offline fallback ---

@test "version check continues when json2yamlresume npm query fails" {
  mock_npm "fail" "0.13.1"
  mock_docker
  run_script
  [ "$status" -eq 0 ]
}

@test "version check continues when yamlresume npm query fails" {
  mock_npm "0.13.1" "fail"
  mock_docker
  run_script
  [ "$status" -eq 0 ]
}

@test "version check continues when both npm queries fail (fully offline)" {
  mock_npm "fail" "fail"
  mock_docker
  run_script
  [ "$status" -eq 0 ]
}

# --- Country code sed transformation (unit) ---

@test "sed transforms country: CA to country: Canada" {
  printf '    country: CA\n' > "$BATS_TEST_TMPDIR/test.yml"
  sed -i '' 's/^    country: CA$/    country: Canada/' "$BATS_TEST_TMPDIR/test.yml"
  run grep 'country: Canada' "$BATS_TEST_TMPDIR/test.yml"
  [ "$status" -eq 0 ]
}

@test "sed does not touch other country values" {
  cat > "$BATS_TEST_TMPDIR/test.yml" << 'EOF'
    country: US
    country: CA
    city: Montréal
    country: GB
EOF
  sed -i '' 's/^    country: CA$/    country: Canada/' "$BATS_TEST_TMPDIR/test.yml"
  run grep -c 'country: Canada' "$BATS_TEST_TMPDIR/test.yml"
  [ "$output" -eq 1 ]
  run grep -c 'country: US' "$BATS_TEST_TMPDIR/test.yml"
  [ "$output" -eq 1 ]
  run grep -c 'country: GB' "$BATS_TEST_TMPDIR/test.yml"
  [ "$output" -eq 1 ]
  run grep 'country: CA' "$BATS_TEST_TMPDIR/test.yml" || true
  [ "$status" -eq 1 ]
}

@test "sed does not match country: CA when something follows" {
  printf '    country: CA  # inline comment\n' > "$BATS_TEST_TMPDIR/test.yml"
  sed -i '' 's/^    country: CA$/    country: Canada/' "$BATS_TEST_TMPDIR/test.yml"
  run grep 'country: Canada' "$BATS_TEST_TMPDIR/test.yml" || true
  [ "$status" -eq 1 ]
  run grep 'country: CA' "$BATS_TEST_TMPDIR/test.yml"
  [ "$status" -eq 0 ]
}

# --- Integration: resume.yml output validation ---

@test "resume.yml exists after sync" {
  [ -f "$REPO_ROOT/resume.yml" ]
}

@test "resume.yml uses full country name (Canada, not CA)" {
  [ -f "$REPO_ROOT/resume.yml" ]
  run grep -c '^    country: Canada$' "$REPO_ROOT/resume.yml"
  [ "$status" -eq 0 ]
  [ "$output" -eq 1 ]
}

@test "resume.yml does not contain ISO country code CA as a value" {
  [ -f "$REPO_ROOT/resume.yml" ]
  run grep -c '^    country: CA$' "$REPO_ROOT/resume.yml" || true
  [ "$status" -eq 1 ] || [ "$output" -eq 0 ]
}
