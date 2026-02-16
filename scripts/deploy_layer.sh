#!/usr/bin/env bash
set -euo pipefail
export AWS_PAGER=""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

LAYER_NAME="${LAYER_NAME:-$LAYER_NAME_DEFAULT}"
ZIP_FILE="${ZIP_FILE:-$LAYER_ZIP_DEFAULT}"
RUNTIME="${RUNTIME:-$RUNTIME_DEFAULT}"
DESCRIPTION="${DESCRIPTION:-$LAYER_DESCRIPTION_DEFAULT}"

LAYER_VERSION_ARN=$(aws lambda publish-layer-version \
  --layer-name "$LAYER_NAME" \
  --description "$DESCRIPTION" \
  --compatible-runtimes "$RUNTIME" \
  --zip-file "fileb://$ZIP_FILE" \
  --query 'LayerVersionArn' \
  --output text)

echo "Published layer: $LAYER_VERSION_ARN"

FUNCTION_NAME="${FUNCTION_NAME:-$API_FUNCTION_NAME_DEFAULT}"

ATTEMPTS=0
MAX_ATTEMPTS=5
while true; do
  if aws lambda update-function-configuration \
    --function-name "$FUNCTION_NAME" \
    --layers "$LAYER_VERSION_ARN" >/dev/null; then
    break
  fi
  ATTEMPTS=$((ATTEMPTS + 1))
  if [ "$ATTEMPTS" -ge "$MAX_ATTEMPTS" ]; then
    echo "Failed to attach layer to function: $FUNCTION_NAME after $MAX_ATTEMPTS attempts" >&2
    exit 1
  fi
  sleep 5
done

echo "Attached layer to function: $FUNCTION_NAME"
