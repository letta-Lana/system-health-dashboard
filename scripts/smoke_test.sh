#!/usr/bin/env bash
# Post-deployment smoke test. Exits non-zero on the first failed check.
# Usage: scripts/smoke_test.sh <base-url>     e.g. scripts/smoke_test.sh http://localhost:5001
set -euo pipefail

BASE_URL="${1:?usage: smoke_test.sh BASE_URL}"

# -f makes curl fail on HTTP 4xx/5xx; the retries give a freshly started container time to come up
CURL=(curl -fsS --retry 5 --retry-delay 2 --retry-connrefused)

for path in /health /version; do
    echo "Checking ${BASE_URL}${path}"
    "${CURL[@]}" "${BASE_URL}${path}" > /dev/null
done

# /metrics must answer and must already contain the request counter (the calls above created it)
echo "Checking ${BASE_URL}/metrics"
metrics="$("${CURL[@]}" "${BASE_URL}/metrics")"
if ! grep -q '^http_requests_total' <<< "${metrics}"; then
    echo "FAIL: /metrics did not contain http_requests_total"
    exit 1
fi

echo "Smoke test passed for ${BASE_URL}"
