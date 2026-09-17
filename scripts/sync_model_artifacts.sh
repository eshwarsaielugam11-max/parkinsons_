#!/usr/bin/env bash
# sync_model_artifacts.sh
# Safely pulls the canonical model_v1.0.0 artifacts from Google Drive to local.

set -e

DRIVE_EXPORT_DIR="/content/drive/MyDrive/pd_voice_project/artifacts/exported/model_v1.0.0"
LOCAL_EXPORT_DIR="$(dirname "$0")/../model/exported/model_v1.0.0"

echo "=========================================================="
echo "    Model Sync Script: Pulling v1.0.0 from Google Drive   "
echo "=========================================================="

echo "NOTE: This script assumes you have mounted or synced your Google Drive."
echo "If running on macOS with Google Drive Desktop, we can copy directly."

# Common path for Google Drive Desktop on macOS:
MAC_GDRIVE_PATH="$HOME/My Drive/pd_voice_project/artifacts/exported/model_v1.0.0"
if [ -d "$MAC_GDRIVE_PATH" ]; then
    echo "Found Google Drive Desktop path!"
    mkdir -p "$LOCAL_EXPORT_DIR"
    cp -r "$MAC_GDRIVE_PATH/"* "$LOCAL_EXPORT_DIR/"
    echo "Sync Complete! Artifacts are now in $LOCAL_EXPORT_DIR"
    exit 0
fi

echo "Google Drive path not automatically found."
echo "Manual Instructions:"
echo "1. Go to your Colab environment or Google Drive."
echo "2. Download the folder: pd_voice_project/artifacts/exported/model_v1.0.0"
echo "3. Extract/Place the contents directly into: $LOCAL_EXPORT_DIR"
echo "   Required files: weights.pt, model_config.json, preprocessing_config.json, calibration.json, feature_scalers.pkl, label_map.json, MODEL_CONTRACT.json"
