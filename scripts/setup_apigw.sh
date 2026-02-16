#!/usr/bin/env bash
set -euo pipefail
export AWS_PAGER=""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

FUNCTION_NAME="${FUNCTION_NAME:-$API_FUNCTION_NAME_DEFAULT}"
API_NAME="${API_NAME:-$API_NAME_DEFAULT}"
STAGE_NAME="${STAGE_NAME:-$STAGE_NAME_DEFAULT}"
API_KEY_NAME="${API_KEY_NAME:-$API_KEY_NAME_DEFAULT}"
USAGE_PLAN_NAME="${USAGE_PLAN_NAME:-$USAGE_PLAN_NAME_DEFAULT}"

AWS_REGION="${AWS_REGION:-$(aws configure get region || true)}"
if [ -z "${AWS_REGION:-}" ]; then
  echo "AWS_REGION is not set and no default region found. Configure AWS CLI or set AWS_REGION." >&2
  exit 1
fi

ACCOUNT_ID="${ACCOUNT_ID:-$(aws sts get-caller-identity --query 'Account' --output text)}"
if [ -z "${ACCOUNT_ID:-}" ]; then
  echo "ACCOUNT_ID could not be determined. Ensure AWS credentials are configured." >&2
  exit 1
fi

FUNC_ARN="$(aws lambda get-function-configuration --function-name "$FUNCTION_NAME" --query 'FunctionArn' --output text)"

# Clean up any old HTTP APIs created by previous versions of this script
OLD_HTTP_IDS="$(aws apigatewayv2 get-apis --query "Items[?Name=='$API_NAME'].ApiId" --output text || true)"
if [ -n "${OLD_HTTP_IDS:-}" ]; then
  for ID in $OLD_HTTP_IDS; do
    aws apigatewayv2 delete-api --api-id "$ID" >/dev/null || true
  done
fi

# Delete existing REST APIs with the same name to keep things idempotent
OLD_REST_IDS="$(aws apigateway get-rest-apis --query "items[?name=='$API_NAME'].id" --output text || true)"
if [ -n "${OLD_REST_IDS:-}" ]; then
  for ID in $OLD_REST_IDS; do
    aws apigateway delete-rest-api --rest-api-id "$ID" >/dev/null || true
  done
fi

# Create REST API
REST_API_ID="$(aws apigateway create-rest-api \
  --name "$API_NAME" \
  --endpoint-configuration types=REGIONAL \
  --query 'id' --output text)"

# Get root resource and create a catch-all proxy resource
ROOT_ID="$(aws apigateway get-resources \
  --rest-api-id "$REST_API_ID" \
  --query 'items[?path==`/`].id' --output text)"

PROXY_ID="$(aws apigateway create-resource \
  --rest-api-id "$REST_API_ID" \
  --parent-id "$ROOT_ID" \
  --path-part "{proxy+}" \
  --query 'id' --output text)"

# Method for proxying all routes (with API key requirement)
aws apigateway put-method \
  --rest-api-id "$REST_API_ID" \
  --resource-id "$PROXY_ID" \
  --http-method ANY \
  --authorization-type "NONE" \
  --api-key-required

# Lambda proxy integration for /{proxy+}
aws apigateway put-integration \
  --rest-api-id "$REST_API_ID" \
  --resource-id "$PROXY_ID" \
  --http-method ANY \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:${AWS_REGION}:lambda:path/2015-03-31/functions/${FUNC_ARN}/invocations"

# Also handle the root path "/" so /prod/ and /prod/health work
aws apigateway put-method \
  --rest-api-id "$REST_API_ID" \
  --resource-id "$ROOT_ID" \
  --http-method ANY \
  --authorization-type "NONE" \
  --api-key-required

aws apigateway put-integration \
  --rest-api-id "$REST_API_ID" \
  --resource-id "$ROOT_ID" \
  --http-method ANY \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:${AWS_REGION}:lambda:path/2015-03-31/functions/${FUNC_ARN}/invocations"

# Allow API Gateway to invoke the Lambda
aws lambda add-permission \
  --function-name "$FUNCTION_NAME" \
  --statement-id "apigw-$REST_API_ID-$STAGE_NAME" \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:${AWS_REGION}:${ACCOUNT_ID}:${REST_API_ID}/*/*/*" >/dev/null || true

# Deploy the API to a stage
aws apigateway create-deployment \
  --rest-api-id "$REST_API_ID" \
  --stage-name "$STAGE_NAME" >/dev/null

# Check if API key already exists
EXISTING_API_KEY_ID="$(aws apigateway get-api-keys \
  --name-query "$API_KEY_NAME" \
  --query 'items[0].id' --output text 2>/dev/null || echo 'None')"

if [ "$EXISTING_API_KEY_ID" = "None" ] || [ -z "$EXISTING_API_KEY_ID" ]; then
  # Create new API key
  API_KEY_ID="$(aws apigateway create-api-key \
    --name "$API_KEY_NAME" \
    --enabled \
    --query 'id' --output text)"
  echo "Created new API key: $API_KEY_NAME"
else
  API_KEY_ID="$EXISTING_API_KEY_ID"
  echo "Using existing API key: $API_KEY_NAME"
fi

API_KEY_VALUE="$(aws apigateway get-api-key \
  --api-key "$API_KEY_ID" \
  --include-value \
  --query 'value' --output text)"

# Check if usage plan already exists
EXISTING_USAGE_PLAN_IDS="$(aws apigateway get-usage-plans \
  --query "items[?name=='$USAGE_PLAN_NAME'].id" --output text 2>/dev/null || echo '')"

# Delete all existing usage plans with the same name
if [ -n "$EXISTING_USAGE_PLAN_IDS" ]; then
  for PLAN_ID in $EXISTING_USAGE_PLAN_IDS; do
    echo "Deleting old usage plan: $PLAN_ID"
    aws apigateway delete-usage-plan --usage-plan-id "$PLAN_ID" >/dev/null 2>&1 || true
  done
fi

# Create new usage plan
USAGE_PLAN_ID="$(aws apigateway create-usage-plan \
  --name "$USAGE_PLAN_NAME" \
  --api-stages "apiId=$REST_API_ID,stage=$STAGE_NAME" \
  --throttle burstLimit=100,rateLimit=50 \
  --quota limit=100000,period=MONTH \
  --query 'id' --output text)"
echo "Created new usage plan: $USAGE_PLAN_NAME"

# Attach API key to usage plan (idempotent - won't fail if already attached)
aws apigateway create-usage-plan-key \
  --usage-plan-id "$USAGE_PLAN_ID" \
  --key-type "API_KEY" \
  --key-id "$API_KEY_ID" >/dev/null 2>&1 || true

# Create a new deployment to apply all changes (with retry for rate limits)
echo "Deploying API to stage: $STAGE_NAME"
MAX_RETRIES=5
RETRY_COUNT=0
RETRY_DELAY=2

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if aws apigateway create-deployment \
    --rest-api-id "$REST_API_ID" \
    --stage-name "$STAGE_NAME" >/dev/null 2>&1; then
    break
  else
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
      echo "Deployment rate limited, retrying in ${RETRY_DELAY}s... (attempt $((RETRY_COUNT + 1))/$MAX_RETRIES)"
      sleep $RETRY_DELAY
      RETRY_DELAY=$((RETRY_DELAY * 2))  # Exponential backoff
    else
      echo "Failed to deploy after $MAX_RETRIES attempts"
      exit 1
    fi
  fi
done

INVOKE_URL="https://${REST_API_ID}.execute-api.${AWS_REGION}.amazonaws.com/${STAGE_NAME}"

echo "REST API ID: $REST_API_ID"
echo "Stage: $STAGE_NAME"
echo "Invoke URL: $INVOKE_URL"
echo "API key (use in x-api-key header): $API_KEY_VALUE"
