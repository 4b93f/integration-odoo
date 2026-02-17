#!/usr/bin/env bash

# Shared configuration for all AWS resources

API_NAME_DEFAULT="odoo-integration-api"
API_FUNCTION_NAME_DEFAULT="api_handler"
SYNC_FUNCTION_NAME_DEFAULT="sync_handler"
LAYER_NAME_DEFAULT="odoo-integration-deps"
RUNTIME_DEFAULT="python3.12"
TIMEOUT_DEFAULT="30"
MEMORY_SIZE_DEFAULT="512"
LAYER_DESCRIPTION_DEFAULT="Runtime dependencies for Odoo Integration FastAPI Lambda"
STAGE_NAME_DEFAULT="prod"
API_KEY_NAME_DEFAULT="odoo-integration-api-key"
USAGE_PLAN_NAME_DEFAULT="odoo-integration-api-plan"
BUILD_DIR_DEFAULT="build/lambda_pkg"
LAYER_DIR_DEFAULT="build/layer/python"
LAMBDA_ZIP_DEFAULT="build/lambda.zip"
LAYER_ZIP_DEFAULT="build/layer.zip"
RUNTIME_IMAGE_DEFAULT="public.ecr.aws/lambda/python:3.12"
