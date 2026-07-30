#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# fix.sh -- Sitemap snapshot auto-fix
#
# Reads environment variables: HEAD_BRANCH, HEAD_SHA, PR_JSON, GITHUB_TOKEN
# Optionally: SITEMAP_FIX_DRY_RUN (any non-empty value enables dry-run mode)
#
# Regenerates the sitemap snapshot, detects drift, commits the fix, pushes to
# a `${HEAD_BRANCH}-sitemap-fix` branch, and creates a PR targeting the
# original branch.
# ---------------------------------------------------------------------------

# --- Step 1: Validate required env vars --------------------------------------

_missing=""
for _var in HEAD_BRANCH HEAD_SHA PR_JSON GITHUB_TOKEN; do
  if [ -z "${!_var:-}" ]; then
    _missing="$_missing $_var"
  fi
done
if [ -n "$_missing" ]; then
  echo "Error: Missing required environment variable(s):$_missing" >&2
  echo "Usage: This script reads from environment variables." >&2
  echo "  Required: HEAD_BRANCH, HEAD_SHA, PR_JSON, GITHUB_TOKEN" >&2
  exit 1
fi

# --- Step 2: Guard -- skip recursive fix branches ----------------------------

if [[ "$HEAD_BRANCH" == *-sitemap-fix ]]; then
  echo "Branch '$HEAD_BRANCH' ends with '-sitemap-fix'; skipping to avoid recursive fix PRs."
  exit 0
fi

# --- Step 3: Guard -- extract PR number --------------------------------------

PR_NUMBER=$(echo "$PR_JSON" | jq -r '.[0].number // empty')
if [ -z "$PR_NUMBER" ]; then
  echo "Warning: Could not extract PR number from PR_JSON. Skipping."
  exit 0
fi

echo "pr_number=$PR_NUMBER" >> "${GITHUB_OUTPUT:-/dev/null}"

# --- Step 4: Dry-run mode ----------------------------------------------------

if [ -n "${SITEMAP_FIX_DRY_RUN:-}" ]; then
  echo "Dry run: would process PR #$PR_NUMBER from branch '$HEAD_BRANCH'"
  exit 0
fi

# --- Step 5: Generate sitemap ------------------------------------------------

make snapshot-sitemap

# --- Step 6: Check for changes -----------------------------------------------

if [ -z "$(git status --porcelain)" ]; then
  echo "No sitemap changes detected; nothing to fix."
  echo "fix_pr_url=" >> "${GITHUB_OUTPUT:-/dev/null}"
  exit 0
fi

# --- Step 7: Configure git ---------------------------------------------------

git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

# --- Step 8: Commit ----------------------------------------------------------

git add -A
git commit -m "chore: update sitemap snapshot [skip ci]"

# --- Step 9: Push ------------------------------------------------------------

FIX_BRANCH="${HEAD_BRANCH}-sitemap-fix"
git push --force origin "HEAD:$FIX_BRANCH"

# --- Step 10: Create fix PR --------------------------------------------------

FIX_PR_URL=$(gh pr create \
  --base "$HEAD_BRANCH" \
  --head "$FIX_BRANCH" \
  --title "chore: update sitemap snapshot" \
  --body "This PR was automatically created because the sitemap snapshot drifted from the site build. It targets the originating PR (#${PR_NUMBER}) so the fix lands in the same merge.

🤖 Generated with [Claude Code](https://claude.com/claude-code)")

echo "fix_pr_url=$FIX_PR_URL" >> "${GITHUB_OUTPUT:-/dev/null}"

# --- Step 11: Write comment file ---------------------------------------------

cat > /tmp/sitemap-fix-comment.md <<EOF
The sitemap snapshot drifted from the site build. A fix PR has been created:

[$FIX_PR_URL]($FIX_PR_URL)

Once that PR is merged, re-run the "Verify sitemap snapshot" workflow on this PR to clear the check.
EOF

# --- Step 12: Success --------------------------------------------------------

echo "Successfully created fix PR: $FIX_PR_URL"
exit 0
