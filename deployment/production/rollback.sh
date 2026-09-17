#!/usr/bin/env bash
set -e

# ==============================================================================
# Production Rollback Script
# Usage: ./rollback.sh [TARGET_PREVIOUS_VERSION]
# Example: ./rollback.sh v1.0.0
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_VERSION="${1:?ERROR: Target rollback version must be specified (e.g. ./rollback.sh v1.0.0)}"
ENV_FILE="${SCRIPT_DIR}/.env.production"

echo "========================================================"
echo "INITIATING EMERGENCY ROLLBACK TO: ${TARGET_VERSION}"
echo "========================================================"

if [ ! -f "${ENV_FILE}" ]; then
    echo "ERROR: Production environment file ${ENV_FILE} not found!"
    exit 1
fi

export APP_VERSION="${TARGET_VERSION}"
export MODEL_VERSION="model_${TARGET_VERSION}"

cd "${SCRIPT_DIR}"

echo "[1/3] Switching container images to version ${TARGET_VERSION}..."
docker compose -f docker-compose.prod.yml --env-file "${ENV_FILE}" up -d --no-build

echo "[2/3] Verifying rollback container health..."
ATTEMPTS=0
MAX_ATTEMPTS=12

until curl -s -f http://localhost:8000/api/v1/health | grep -q "healthy"; do
    ATTEMPTS=$((ATTEMPTS + 1))
    if [ ${ATTEMPTS} -ge ${MAX_ATTEMPTS} ]; then
        echo "ROLLBACK HEALTH CHECK FAILED!"
        exit 1
    fi
    echo "Checking health... (${ATTEMPTS}/${MAX_ATTEMPTS})"
    sleep 5
done

echo "========================================================"
echo "ROLLBACK TO ${TARGET_VERSION} COMPLETED SUCCESSFULLY!"
echo "System restored to stable state."
echo "========================================================"
