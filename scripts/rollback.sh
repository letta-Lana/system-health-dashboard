#!/usr/bin/env bash
# Redeploy the last known good image tag for one environment.
# Usage: scripts/rollback.sh <staging|production>
#
# The pipeline writes "last_good_<environment>" only AFTER that environment's smoke test passed,
# so the file always holds the most recent tag that is known to work.
set -euo pipefail

ENV_NAME="${1:?usage: rollback.sh staging|production}"
case "${ENV_NAME}" in
    staging) PORT=5001 ;;
    production) PORT=5002 ;;
    *) echo "Unknown environment '${ENV_NAME}' (use staging or production)"; exit 2 ;;
esac

# Always run from the repository root so the Compose file is found
cd "$(dirname "$0")/.."

STATE_DIR="${STATE_DIR:-${HOME}/system-health-state}"
DEPLOY_HOST="${DEPLOY_HOST:-localhost}"

TAG="$(cat "${STATE_DIR}/last_good_${ENV_NAME}" 2>/dev/null || true)"
if [ -z "${TAG}" ]; then
    echo "No previous good tag recorded for ${ENV_NAME}: nothing to roll back to."
    exit 0
fi

echo "Rolling back ${ENV_NAME} to system-health:${TAG}"
IMAGE_TAG="${TAG}" docker compose -p "${ENV_NAME}" -f "docker-compose.${ENV_NAME}.yml" up -d

echo "Running image: $(docker inspect -f '{{.Config.Image}}' "app-${ENV_NAME}")"
./scripts/smoke_test.sh "http://${DEPLOY_HOST}:${PORT}"
echo "Rollback of ${ENV_NAME} to system-health:${TAG} complete"
