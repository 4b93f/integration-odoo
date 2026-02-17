#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

RUNTIME_IMAGE="${RUNTIME_IMAGE:-$RUNTIME_IMAGE_DEFAULT}"
LAYER_DIR="${LAYER_DIR:-$LAYER_DIR_DEFAULT}"
ZIP_PATH="${ZIP_PATH:-$LAYER_ZIP_DEFAULT}"

mkdir -p "$LAYER_DIR"
rm -rf "$LAYER_DIR"/*

docker run --rm \
  --platform linux/amd64 \
  --entrypoint /bin/sh \
  -v "$PWD":/opt -w /opt "$RUNTIME_IMAGE" -lc \
  "python -m pip install --upgrade --no-cache-dir -r requirements.lambda.txt -t \"$LAYER_DIR\" && \
   find \"$LAYER_DIR\" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true && \
   find \"$LAYER_DIR\" -name '*.pyc' -delete 2>/dev/null || true && \
   find \"$LAYER_DIR\" -name '*.pyo' -delete 2>/dev/null || true && \
   find \"$LAYER_DIR\" -name '*.dist-info' -type d -exec rm -rf {} + 2>/dev/null || true && \
   find \"$LAYER_DIR\" -name '*.egg-info' -type d -exec rm -rf {} + 2>/dev/null || true && \
   find \"$LAYER_DIR\" -name 'tests' -type d -exec rm -rf {} + 2>/dev/null || true && \
   find \"$LAYER_DIR\" -name '*.pyi' -delete 2>/dev/null || true"

(cd build/layer && zip -r ../layer.zip . >/dev/null)

echo "Layer package created at $ZIP_PATH"
