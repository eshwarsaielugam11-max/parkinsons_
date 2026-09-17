#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "Starting PD Voice Backend Service..."
cd "${ROOT_DIR}"

if [ -f "backend/pd-voice-backend/bin/activate" ]; then
    source backend/pd-voice-backend/bin/activate
fi

export MODEL_VERSION="${MODEL_VERSION:-model_v1.0.0}"
export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-mock_key_for_testing}"
export DATABASE_URL="${DATABASE_URL:-sqlite:///./test.db}"
export VECTOR_DB_PATH="${VECTOR_DB_PATH:-./chroma_db}"
export BACKEND_CORS_ORIGINS='["http://localhost:3000","http://127.0.0.1:3000","http://localhost:5173"]'

exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
