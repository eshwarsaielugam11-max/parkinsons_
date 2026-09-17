#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$(cd "${SCRIPT_DIR}/../frontend" && pwd)"

echo "Starting PD Voice Frontend Vite Dev Server..."
cd "${FRONTEND_DIR}"

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

exec npm run dev
