#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<EOF
Usage: $(basename "$0") <api_key> <sitemap_url>

Submits a sitemap URL to the IndexNow API.

Arguments:
  api_key      IndexNow API key
  sitemap_url  Full URL of the sitemap to submit (must start with https://)
EOF
}

if [[ $# -ne 2 ]]; then
  usage
  exit 1
fi

API_KEY="$1"
SITEMAP_URL="$2"

if [[ -z "$API_KEY" ]]; then
  echo "Error: api_key is required" >&2
  usage
  exit 1
fi

if [[ -z "$SITEMAP_URL" ]]; then
  echo "Error: sitemap_url is required" >&2
  usage
  exit 1
fi

# Validate sitemap_url starts with https://
if [[ "$SITEMAP_URL" != https://* ]]; then
  echo "Error: sitemap_url must start with https://" >&2
  exit 1
fi

HOST="ouimet.info"
KEY_LOCATION="https://${HOST}/${API_KEY}.txt"
ENDPOINT="https://api.indexnow.org/indexnow"

PAYLOAD=$(cat <<JSON
{
  "host": "${HOST}",
  "key": "${API_KEY}",
  "keyLocation": "${KEY_LOCATION}",
  "urlList": ["${SITEMAP_URL}"]
}
JSON
)

# Dry-run mode: print the payload and endpoint, then exit cleanly
if [[ -n "${INDEXNOW_DRY_RUN:-}" ]]; then
  echo "IndexNow dry run"
  echo "Endpoint: ${ENDPOINT}"
  echo "Payload:"
  echo "${PAYLOAD}"
  exit 0
fi

# Submit to IndexNow; capture both body and HTTP status code
HTTP_OUTPUT=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Content-Type: application/json" \
  -d "${PAYLOAD}" \
  "${ENDPOINT}")

# Split body (all but last line) and status code (last line)
BODY=$(echo "${HTTP_OUTPUT}" | sed '$d')
STATUS=$(echo "${HTTP_OUTPUT}" | tail -n1)

# Check if status is 2xx
if [[ ! "${STATUS}" =~ ^2[0-9][0-9]$ ]]; then
  echo "Error: IndexNow returned status ${STATUS}" >&2
  echo "Response body:" >&2
  echo "${BODY}" >&2
  exit 1
fi

echo "Successfully submitted sitemap to IndexNow (status ${STATUS})."
exit 0
