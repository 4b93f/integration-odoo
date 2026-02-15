#!/usr/bin/env bash
set -euo pipefail

echo "Redeploying all AWS resources (API + Sync)..."

./scripts/clean_aws.sh

./scripts/build_lambda.sh

FUNCTION_NAME=api_handler HANDLER=src.main.handler ./scripts/deploy_lambda.sh

SYNC_FUNCTION=${SYNC_FUNCTION:-sync_handler}
SYNC_HANDLER=${SYNC_HANDLER:-src.sync_lambda.handler}
FUNCTION_NAME="$SYNC_FUNCTION" HANDLER="$SYNC_HANDLER" ./scripts/deploy_lambda.sh

./scripts/build_layer.sh
# Attach layer to both functions
FUNCTION_NAME=api_handler ./scripts/deploy_layer.sh
FUNCTION_NAME="$SYNC_FUNCTION" ./scripts/deploy_layer.sh

./scripts/setup_apigw.sh

SYNC_RULE_NAME=${SYNC_RULE_NAME:-chift-sync-daily}
SYNC_SCHEDULE=${SYNC_SCHEDULE:-rate(1 day)}
RULE_ARN=$(aws events put-rule --name "$SYNC_RULE_NAME" --schedule-expression "$SYNC_SCHEDULE" --query 'RuleArn' --output text)
FUNC_ARN=$(aws lambda get-function-configuration --function-name "$SYNC_FUNCTION" --query 'FunctionArn' --output text)
aws events put-targets --rule "$SYNC_RULE_NAME" --targets Id="1",Arn="$FUNC_ARN"
aws lambda add-permission --function-name "$SYNC_FUNCTION" \
  --statement-id "events-$SYNC_RULE_NAME" \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn "$RULE_ARN" >/dev/null || true

echo "Redeploy complete."
