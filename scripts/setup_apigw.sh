#!/usr/bin/env bash
set -euo pipefail

FUNCTION_NAME="${FUNCTION_NAME:-api_handler}"

API_NAME="${API_NAME:-chift-api}"

FUNC_ARN="$(aws lambda get-function-configuration --function-name $FUNCTION_NAME --query 'FunctionArn' --output text)"

OLD_IDS="$(aws apigatewayv2 get-apis --query \"Items[?Name=='$API_NAME'].ApiId\" --output text || true)"
if [ -n \"$OLD_IDS\" ]; then
  for ID in $OLD_IDS; do
    aws apigatewayv2 delete-api --api-id \"$ID\" >/dev/null || true
  done
fi

API_ID="$(aws apigatewayv2 create-api --name $API_NAME --protocol-type HTTP --target $FUNC_ARN --query 'ApiId' --output text)"

URL="$(aws apigatewayv2 get-api --api-id $API_ID --query 'ApiEndpoint' --output text)"

aws lambda add-permission \
  --function-name "$FUNCTION_NAME" \
  --statement-id "apigw-$API_ID" \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com >/dev/null || true

echo "API URL: $URL"
