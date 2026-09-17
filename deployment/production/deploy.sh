#!/usr/bin/env bash
set -e

# ==============================================================================
# Production Deployment Script
# Usage: ./deploy.sh [VERSION]
# Example: ./deploy.sh v1.0.1
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

VERSION="${1:-v1.0.0}"
ENV_FILE="${SCRIPT_DIR}/.env.production"

echo "========================================================"
echo "Starting Production Deployment: Target Version ${VERSION}"
echo "========================================================"

if [ ! -f "${ENV_FILE}" ]; then
    echo "ERROR: Production environment file ${ENV_FILE} not found!"
    echo "Please copy ${SCRIPT_DIR}/.env.production.example to ${ENV_FILE} and configure secrets."
    exit 1
fi

export APP_VERSION="${VERSION}"
export MODEL_VERSION="model_${VERSION}"

cd "${SCRIPT_DIR}"

echo "[1/4] Building production container images for ${VERSION}..."
docker compose -f docker-compose.prod.yml --env-file "${ENV_FILE}" build

echo "[2/4] Pulling database & dependency images..."
docker compose -f docker-compose.prod.yml --env-file "${ENV_FILE}" pull db

echo "[3/4] Launching upgraded production stack..."
docker compose -f docker-compose.prod.yml --env-file "${ENV_FILE}" up -d --remove-orphans

echo "[4/4] Performing post-deployment health check..."
ATTEMPTS=0
MAX_ATTEMPTS=12

until curl -s -f http://localhost:8000/api/v1/health | grep -q "healthy"; do
    ATTEMPTS=$((ATTEMPTS + 1))
    if [ ${ATTEMPTS} -ge ${MAX_ATTEMPTS} ]; then
        echo "HEALTH CHECK FAILED! Health endpoint did not return healthy after 60s."
        echo "To roll back to previous release, run: ./rollback.sh <PREVIOUS_VERSION>"
        exit 1
    fi
    echo "Waiting for healthcheck to pass... (${ATTEMPTS}/${MAX_ATTEMPTS})"
    sleep 5
done

echo "========================================================"
echo "Deployment of ${VERSION} COMPLETED SUCCESSFULLY!"
echo "Health status: HEALTHY"
echo "========================================================"
