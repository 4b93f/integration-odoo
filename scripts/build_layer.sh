#!/usr/bin/env bash
set -euo pipefail

RUNTIME_IMAGE="public.ecr.aws/lambda/python:3.12"
LAYER_DIR="build/layer/python"
ZIP_PATH="build/layer.zip"

mkdir -p "$LAYER_DIR"
rm -rf "$LAYER_DIR"/*

docker run --rm \
  --platform linux/amd64 \
  --entrypoint /bin/sh \
  -v "$PWD":/opt -w /opt "$RUNTIME_IMAGE" -lc \
  "python -m pip install --upgrade --no-cache-dir -r requirements.lambda.txt -t \"$LAYER_DIR\""

(echo "Pruning layer size..." \
  && find "$LAYER_DIR" -name "__pycache__" -type d -exec rm -rf {} + \
  && find "$LAYER_DIR" -name "*.pyc" -delete \
  && find "$LAYER_DIR" -name "*.pyo" -delete \
  && find "$LAYER_DIR" -name "*.dist-info" -type d -exec rm -rf {} + \
  && find "$LAYER_DIR" -name "*.egg-info" -type d -exec rm -rf {} + \
  && find "$LAYER_DIR" -name "tests" -type d -exec rm -rf {} + \
  && find "$LAYER_DIR" -name "*.pyi" -delete) >/dev/null

(cd build/layer && zip -r ../layer.zip . >/dev/null)

echo "Layer package created at $ZIP_PATH"
