#!/usr/bin/env bash
set -euo pipefail

RUNTIME_IMAGE="public.ecr.aws/lambda/python:3.12"
BUILD_DIR="build/lambda_pkg"
ZIP_PATH="build/lambda.zip"

mkdir -p "$BUILD_DIR"
rm -rf "$BUILD_DIR"/*
rm -f "$ZIP_PATH"

docker run --rm \
  --platform linux/amd64 \
  --entrypoint /bin/sh \
  -v "$PWD":/opt -w /opt "$RUNTIME_IMAGE" -lc \
  "python -m pip install --upgrade --no-cache-dir -r requirements.lambda.txt -t \"$BUILD_DIR\" && cp -r src \"$BUILD_DIR\""

find "$BUILD_DIR" -name "__pycache__" -type d -exec rm -rf {} + >/dev/null 2>&1 || true
find "$BUILD_DIR" -name "*.pyc" -delete >/dev/null 2>&1 || true
find "$BUILD_DIR" -name "*.pyo" -delete >/dev/null 2>&1 || true
find "$BUILD_DIR" -name "*.dist-info" -type d -exec rm -rf {} + >/dev/null 2>&1 || true
find "$BUILD_DIR" -name "*.egg-info" -type d -exec rm -rf {} + >/dev/null 2>&1 || true
find "$BUILD_DIR" -name "tests" -type d -exec rm -rf {} + >/dev/null 2>&1 || true
find "$BUILD_DIR" -name "*.pyi" -delete >/dev/null 2>&1 || true

(cd "$BUILD_DIR" && zip -r ../lambda.zip . >/dev/null)

echo "Package created at $ZIP_PATH"
