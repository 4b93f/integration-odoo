#!/usr/bin/env bash
set -euo pipefail

LAYER_NAME="${LAYER_NAME:-chift-deps}"
ZIP_FILE="${ZIP_FILE:-build/layer.zip}"
RUNTIME="python3.12"
DESCRIPTION="${DESCRIPTION:-Runtime dependencies for Chift FastAPI Lambda}"

LAYER_VERSION_ARN=$(aws lambda publish-layer-version \
  --layer-name "$LAYER_NAME" \
  --description "$DESCRIPTION" \
  --compatible-runtimes "$RUNTIME" \
  --zip-file "fileb://$ZIP_FILE" \
  --query 'LayerVersionArn' \
  --output text)

echo "Published layer: $LAYER_VERSION_ARN"

FUNCTION_NAME="${FUNCTION_NAME:-api_handler}"
aws lambda update-function-configuration \
  --function-name "$FUNCTION_NAME" \
  --layers "$LAYER_VERSION_ARN" >/dev/null

echo "Attached layer to function: $FUNCTION_NAME"
