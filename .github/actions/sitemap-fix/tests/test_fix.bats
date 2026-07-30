#!/usr/bin/env bats

ACTION_DIR="$(cd "$(dirname "${BATS_TEST_FILENAME}")/.." && pwd)"
FIX="$ACTION_DIR/fix.sh"

# No setup() needed — pure bash, no uv/Python

@test "missing HEAD_BRANCH fails" {
  run env HEAD_SHA=abc PR_JSON='[{"number":1}]' GITHUB_TOKEN=token bash "$FIX"
  [ "$status" -eq 1 ]
  [[ "$output" == *"Error"* || "$output" == *"Usage"* ]]
}

@test "missing HEAD_SHA fails" {
  run env HEAD_BRANCH=main PR_JSON='[{"number":1}]' GITHUB_TOKEN=token bash "$FIX"
  [ "$status" -eq 1 ]
  [[ "$output" == *"Error"* || "$output" == *"Usage"* ]]
}

@test "missing PR_JSON fails" {
  run env HEAD_BRANCH=main HEAD_SHA=abc GITHUB_TOKEN=token bash "$FIX"
  [ "$status" -eq 1 ]
  [[ "$output" == *"Error"* || "$output" == *"Usage"* ]]
}

@test "missing GITHUB_TOKEN fails" {
  run env HEAD_BRANCH=main HEAD_SHA=abc PR_JSON='[{"number":1}]' bash "$FIX"
  [ "$status" -eq 1 ]
  [[ "$output" == *"Error"* || "$output" == *"Usage"* ]]
}

@test "branch ending with -sitemap-fix skips" {
  run env SITEMAP_FIX_DRY_RUN=1 HEAD_BRANCH=feature-sitemap-fix HEAD_SHA=abc PR_JSON='[{"number":1}]' GITHUB_TOKEN=token bash "$FIX"
  [ "$status" -eq 0 ]
  [[ "$output" == *"skipping"* ]]
}

@test "empty PR_JSON array exits with warning" {
  run env SITEMAP_FIX_DRY_RUN=1 HEAD_BRANCH=main HEAD_SHA=abc PR_JSON='[]' GITHUB_TOKEN=token bash "$FIX"
  [ "$status" -eq 0 ]
  [[ "$output" == *"Warning"* ]]
}

@test "PR_JSON without number field exits with warning" {
  run env SITEMAP_FIX_DRY_RUN=1 HEAD_BRANCH=main HEAD_SHA=abc PR_JSON='[{}]' GITHUB_TOKEN=token bash "$FIX"
  [ "$status" -eq 0 ]
  [[ "$output" == *"Warning"* ]]
}

@test "valid inputs in dry-run mode succeeds" {
  run env SITEMAP_FIX_DRY_RUN=1 HEAD_BRANCH=feature-branch HEAD_SHA=abc123 PR_JSON='[{"number":42}]' GITHUB_TOKEN=token bash "$FIX"
  [ "$status" -eq 0 ]
}

@test "dry-run output contains expected info" {
  run env SITEMAP_FIX_DRY_RUN=1 HEAD_BRANCH=feature-branch HEAD_SHA=abc123 PR_JSON='[{"number":42}]' GITHUB_TOKEN=token bash "$FIX"
  [ "$status" -eq 0 ]
  [[ "$output" == *"Dry run"* ]]
  [[ "$output" == *"PR #42"* ]]
  [[ "$output" == *"feature-branch"* ]]
}

@test "branch NOT ending with -sitemap-fix proceeds past guard" {
  run env SITEMAP_FIX_DRY_RUN=1 HEAD_BRANCH=normal-branch HEAD_SHA=abc PR_JSON='[{"number":5}]' GITHUB_TOKEN=token bash "$FIX"
  [ "$status" -eq 0 ]
  [[ "$output" != *"skipping"* ]]
  [[ "$output" == *"Dry run"* ]]
}
