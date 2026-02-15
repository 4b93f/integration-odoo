#!/usr/bin/env bash
set -euo pipefail

API_NAME="${API_NAME:-chift-api}"
FUNCTION_NAME="${FUNCTION_NAME:-api_handler}"
LAYER_NAME="${LAYER_NAME:-chift-deps}"

echo "Cleaning AWS resources..."

# Delete HTTP APIs named chift-api
API_IDS=$(aws apigatewayv2 get-apis --query "Items[?Name=='$API_NAME'].ApiId" --output text || true)
if [ -n "${API_IDS:-}" ]; then
  for ID in $API_IDS; do
    echo "Deleting API: $ID"
    aws apigatewayv2 delete-api --api-id "$ID" || true
  done
else
  echo "No APIs named $API_NAME found"
fi

# Delete Lambda function
if aws lambda get-function --function-name "$FUNCTION_NAME" >/dev/null 2>&1; then
  echo "Deleting Lambda function: $FUNCTION_NAME"
  aws lambda delete-function --function-name "$FUNCTION_NAME" || true
else
  echo "Lambda function $FUNCTION_NAME not found"
fi

# Delete all versions of layer
LAYER_VERS=$(aws lambda list-layer-versions --layer-name "$LAYER_NAME" --query 'LayerVersions[].Version' --output text || true)
if [ -n "${LAYER_VERS:-}" ]; then
  for V in $LAYER_VERS; do
    echo "Deleting layer $LAYER_NAME version: $V"
    aws lambda delete-layer-version --layer-name "$LAYER_NAME" --version-number "$V" || true
  done
else
  echo "No layer versions found for $LAYER_NAME"
fi

echo "Clean complete."
