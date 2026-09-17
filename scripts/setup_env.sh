#!/usr/bin/env bash
# Sets up the Python environment for the backend.
# NOTE: Using built-in venv due to local Conda/pyenv instability, but strictly targeting ARM64 Python 3.13.

set -e

ENV_NAME="pd-voice-backend"
ENV_DIR="backend/$ENV_NAME"
PYTHON_BIN="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"

echo "Creating isolated Python environment in $ENV_DIR..."
$PYTHON_BIN -m venv "$ENV_DIR"

echo "Activating environment..."
source "$ENV_DIR/bin/activate"

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing requirements..."
pip install -r backend/requirements.txt

echo "Environment setup complete!"
echo "To activate in the future, run: source $ENV_DIR/bin/activate"
