#!/usr/bin/env bash
set -euo pipefail
export AWS_PAGER=""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

FUNCTION_NAME="${FUNCTION_NAME:-$API_FUNCTION_NAME_DEFAULT}"
ZIP_FILE="${ZIP_FILE:-$LAMBDA_ZIP_DEFAULT}"
RUNTIME="${RUNTIME:-$RUNTIME_DEFAULT}"
HANDLER="${HANDLER:-src.api.app.handler}"
TIMEOUT="${TIMEOUT:-$TIMEOUT_DEFAULT}"
MEMORY_SIZE="${MEMORY_SIZE:-$MEMORY_SIZE_DEFAULT}"

ROLE_ARN="${ROLE_ARN:-}"
ROLE_NAME="${ROLE_NAME:-lambda-execution-role}"
if [ -z "$ROLE_ARN" ]; then
  if ! aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
    TRUST_POLICY='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
    aws iam create-role --role-name "$ROLE_NAME" --assume-role-policy-document "$TRUST_POLICY" >/dev/null
    aws iam attach-role-policy --role-name "$ROLE_NAME" --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole >/dev/null
    aws iam wait role-exists --role-name "$ROLE_NAME"
  fi
  ROLE_ARN="$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)"
fi

ENV_FILE="${ENV_FILE:-.env}"
ENV_ARGS=""
if [ -f "$ENV_FILE" ]; then
  VARS=""
  while IFS='=' read -r key value; do
    [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
    value="${value%\"}"; value="${value#\"}"
    value="${value%\'}"; value="${value#\'}"
    VARS+="$key=$value,"
  done < "$ENV_FILE"
  VARS="${VARS%,}"
  if [ -n "$VARS" ]; then
    ENV_ARGS="--environment Variables={$VARS}"
  fi
fi

if ! aws lambda get-function --function-name "$FUNCTION_NAME" >/dev/null 2>&1; then
  aws lambda create-function \
    --function-name "$FUNCTION_NAME" \
    --runtime "$RUNTIME" \
    --role "$ROLE_ARN" \
    --handler "$HANDLER" \
    --timeout "$TIMEOUT" \
    --memory-size "$MEMORY_SIZE" \
    --zip-file "fileb://$ZIP_FILE" \
    ${ENV_ARGS}
else
  aws lambda update-function-code \
    --function-name "$FUNCTION_NAME" \
    --zip-file "fileb://$ZIP_FILE" >/dev/null
  if [ -n "$ENV_ARGS" ]; then
    ATTEMPTS=0
    MAX_ATTEMPTS=5
    while true; do
      if aws lambda update-function-configuration \
        --function-name "$FUNCTION_NAME" \
        ${ENV_ARGS} >/dev/null; then
        break
      fi
      ATTEMPTS=$((ATTEMPTS + 1))
      if [ "$ATTEMPTS" -ge "$MAX_ATTEMPTS" ]; then
        echo "Failed to update configuration for function: $FUNCTION_NAME after $MAX_ATTEMPTS attempts" >&2
        exit 1
      fi
      sleep 5
    done
  fi
fi

echo "Deployed function: $FUNCTION_NAME"
