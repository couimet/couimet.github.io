#!/usr/bin/env bats

ACTION_DIR="$(cd "$(dirname "${BATS_TEST_FILENAME}")/.." && pwd)"
SUBMIT="$ACTION_DIR/submit.sh"

# No setup() needed — this is pure bash, no uv/Python

@test "missing both arguments fails" {
  run bash "$SUBMIT"
  [ "$status" -eq 1 ]
  [[ "$output" == *"Usage"* ]]
}

@test "missing API key fails" {
  run bash "$SUBMIT" "" "https://ouimet.info/sitemap.xml"
  [ "$status" -eq 1 ]
  [[ "$output" == *"Usage"* ]]
}

@test "missing URL fails" {
  run bash "$SUBMIT" "testkeytest" ""
  [ "$status" -eq 1 ]
  [[ "$output" == *"Usage"* ]]
}

@test "invalid URL (no https://) fails" {
  run bash "$SUBMIT" "testkeytest" "not-a-url"
  [ "$status" -eq 1 ]
  [[ "$output" == *"Error"* ]]
}

@test "dry-run mode succeeds" {
  run env INDEXNOW_DRY_RUN=1 bash "$SUBMIT" "testkey123" "https://ouimet.info/sitemap.xml"
  [ "$status" -eq 0 ]
}

@test "dry-run output contains expected fields" {
  run env INDEXNOW_DRY_RUN=1 bash "$SUBMIT" "testkey123" "https://ouimet.info/sitemap.xml"
  [ "$status" -eq 0 ]
  [[ "$output" == *"\"host\": \"ouimet.info\""* ]]
  [[ "$output" == *"\"key\": \"testkey123\""* ]]
  [[ "$output" == *"\"keyLocation\": \"https://ouimet.info/testkey123.txt\""* ]]
  [[ "$output" == *"\"urlList\""* ]]
  [[ "$output" == *"api.indexnow.org/indexnow"* ]]
}

@test "dry-run with different host" {
  run env INDEXNOW_DRY_RUN=1 bash "$SUBMIT" "testkey123" "https://example.com/sitemap.xml"
  [ "$status" -eq 0 ]
  [[ "$output" == *"\"host\": \"example.com\""* ]]
  [[ "$output" == *"\"keyLocation\": \"https://example.com/testkey123.txt\""* ]]
}

@test "invalid API key with special characters fails" {
  run bash "$SUBMIT" "bad key!" "https://ouimet.info/sitemap.xml"
  [ "$status" -eq 1 ]
  [[ "$output" == *"api_key must contain only alphanumeric"* ]]
}

@test "invalid API key too short fails" {
  run bash "$SUBMIT" "ab" "https://ouimet.info/sitemap.xml"
  [ "$status" -eq 1 ]
  [[ "$output" == *"api_key must contain only alphanumeric"* ]]
}
