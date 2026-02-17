# Deployment Guide: Odoo Integration Service

This guide walks you through deploying the Odoo Integration Service to AWS.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Customization](#customization)

---

## Prerequisites

### Required Tools

- **Python 3.12+** and `pip`
- **Docker** (for building Lambda packages)
- **AWS CLI v2** configured with credentials
- **Git** (to clone the repository)

### AWS Account Requirements

You need permissions for:
- Lambda (create/update functions and layers)
- API Gateway (REST APIs)
- EventBridge (Scheduler)
- IAM (create Lambda execution roles)
- CloudWatch Logs (for viewing logs)

### Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and default region

# Or export environment variables:
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_REGION=eu-west-1
```

Verify configuration:
```bash
aws sts get-caller-identity
```

---

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/4b93f/integration-odoo.git
cd integration-odoo
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

### 1. Database Setup (Neon PostgreSQL)

Recommended: Use [Neon](https://neon.tech) for serverless PostgreSQL:

1. Create account at https://neon.tech
2. Create new project
3. Copy connection string (format: `postgresql://user:password@host/dbname`)
4. Modify for async support: `postgresql+asyncpg://user:password@host/dbname`

### 2. Odoo API Access

1. Log into your Odoo instance
2. Go to Settings → Users → Your User
3. Generate API Key (or use password)
4. Note your Odoo URL and database name

### 3. Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit .env file
nano .env  # or vim, code, etc.
```

Required variables in `.env`:

```env
# PostgreSQL Database (use async driver)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Odoo Connection
ODOO_URL=https://your-company.odoo.com
ODOO_DB=your-odoo-db-name
ODOO_USERNAME=your@email.com
ODOO_PASSWORD=your-odoo-api-key
```

**Important**: 
- Use `postgresql+asyncpg://` prefix (not `postgresql://`)
- Ensure database is accessible from AWS Lambda (whitelist AWS IP ranges or use VPC)
- Test Odoo credentials before deploying

---

## Deployment

### One-Command Deployment

```bash
./scripts/redeploy_all.sh
```

This script performs the following steps:

1. **Builds Lambda Package** (Docker container)
   - Creates deployment ZIP with application code
   - Includes all necessary files from `src/`
   
2. **Builds Lambda Layer** (Python dependencies)
   - Packages all requirements from `requirements.lambda.txt`
   - Creates optimized layer for Lambda runtime

3. **Deploys Lambda Functions**
   - **API Lambda**: Handles HTTP requests via API Gateway
   - **Sync Lambda**: Runs scheduled Odoo synchronization

4. **Creates API Gateway**
   - REST API with API key authentication
   - CORS enabled for web access
   - Usage plan with rate limiting

5. **Sets Up EventBridge Schedule**
   - Triggers sync Lambda every 15 minutes
   - Runs both partner and invoice sync

### Deployment Output

Upon successful deployment, you'll see:

```
============================================
Deployment Complete!
============================================
API URL: https://r3uopo4xal.execute-api.eu-west-1.amazonaws.com/prod
API Key: PUb1TzXqB64NfqoO0sYpAabx1maPbmjQ1oArHwop

Test your API:
curl -H "x-api-key: PUb1TzXqB64NfqoO0sYpAabx1maPbmjQ1oArHwop" \\
  https://r3uopo4xal.execute-api.eu-west-1.amazonaws.com/prod/partners/
============================================
```

**Save these values!** You'll need them to access your API.

---

## Verification

### 1. Test API Endpoints

```bash
# Set variables for convenience
export API_KEY="your-api-key-from-deployment"
export API_URL="your-api-url-from-deployment"

# Test partners endpoint
curl -H "x-api-key: $API_KEY" "$API_URL/partners/"

# Test specific partner
curl -H "x-api-key: $API_KEY" "$API_URL/partners/123"

# Test invoices endpoint
curl -H "x-api-key: $API_KEY" "$API_URL/invoices/"

# Test API documentation
open "$API_URL/docs"  # Opens Swagger UI in browser
```

Expected response:
```json
[
  {
    "id": 1,
    "odoo_id": 123,
    "name": "Partner Name",
    "email": "partner@example.com",
    "active": true,
    "synced_at": "2026-02-16T10:30:00Z"
  }
]
```

### 2. Check Lambda Logs

```bash
# View API Lambda logs
aws logs tail /aws/lambda/odoo-integration-api --follow

# View Sync Lambda logs
aws logs tail /aws/lambda/odoo-integration-sync --follow
```

### 3. Verify Sync Schedule

```bash
# List EventBridge schedules
aws scheduler list-schedules

# Get specific schedule details
aws scheduler get-schedule --name odoo-integration-sync-schedule
```

### 4. Manual Sync Trigger

```bash
# Invoke sync Lambda manually
aws lambda invoke \\
  --function-name odoo-integration-sync \\
  --log-type Tail \\
  response.json

# Check response
cat response.json
```

---

## Troubleshooting

### Issue: API Returns 500 Error

**Symptoms**: `{"detail": "Internal Server Error"}`

**Solutions**:
1. Check Lambda logs for exceptions:
   ```bash
   aws logs tail /aws/lambda/odoo-integration-api --follow
   ```

2. Verify database connection:
   - Ensure `DATABASE_URL` in Lambda environment is correct
   - Check database is accessible from Lambda (security groups/firewall)
   - Test connection: `psql $DATABASE_URL`

3. Check Lambda environment variables:
   ```bash
   aws lambda get-function-configuration --function-name odoo-integration-api
   ```

### Issue: Sync Not Running

**Symptoms**: No new data in database after 15 minutes

**Solutions**:
1. Check EventBridge schedule is enabled:
   ```bash
   aws scheduler get-schedule --name odoo-integration-sync-schedule
   ```

2. Manually trigger sync to see error:
   ```bash
   aws lambda invoke --function-name odoo-integration-sync response.json
   cat response.json
   ```

3. Verify Odoo credentials in Lambda environment

### Issue: Database Connection Timeout

**Symptoms**: `asyncpg.exceptions.ConnectionDoesNotExistError`

**Solutions**:
1. **Whitelist AWS Lambda IPs** in your database firewall
2. **Use VPC**: Deploy Lambda in VPC with access to database
3. **Increase connection timeout** in DATABASE_URL:
   ```
   postgresql+asyncpg://user:pass@host/db?connect_timeout=10
   ```

### Issue: Docker Build Fails

**Symptoms**: `docker: command not found` or permission errors

**Solutions**:
1. Ensure Docker is running:
   ```bash
   docker ps
   ```

2. Fix Docker permissions (Linux):
   ```bash
   sudo usermod -aG docker $USER
   # Log out and back in
   ```

3. Use Docker Desktop (macOS/Windows)

### Issue: API Key Not Working

**Symptoms**: `{"message":"Forbidden"}`

**Solutions**:
1. Verify you're using the correct header:
   ```bash
   curl -H "x-api-key: YOUR_KEY" "$API_URL/partners/"
   ```

2. Check API key is associated with usage plan:
   ```bash
   aws apigateway get-usage-plan-keys --usage-plan-id YOUR_PLAN_ID
   ```

3. Regenerate API key if needed:
   ```bash
   ./scripts/setup_apigw.sh  # Re-run API Gateway setup
   ```

---

## Customization

### Change Sync Schedule

Edit EventBridge schedule (default: every 15 minutes):

```bash
# Update schedule expression
aws scheduler update-schedule \\
  --name odoo-integration-sync-schedule \\
  --schedule-expression "rate(30 minutes)"  # Change to 30 minutes

# Or use cron expression
aws scheduler update-schedule \\
  --name odoo-integration-sync-schedule \\
  --schedule-expression "cron(0 */2 * * ? *)"  # Every 2 hours
```

### Override Default Names

Set environment variables before deployment:

```bash
API_NAME="my-odoo-api" \\
SYNC_NAME="my-odoo-sync" \\
LAYER_NAME="my-python-deps" \\
SCHEDULE_NAME="my-sync-schedule" \\
./scripts/redeploy_all.sh
```

### Deploy to Different Region

```bash
export AWS_REGION=us-east-1
./scripts/redeploy_all.sh
```

### Add Custom Endpoints

1. Create new router in `src/api/routers/`:
   ```python
   # src/api/routers/custom.py
   from fastapi import APIRouter
   
   router = APIRouter(prefix="/custom", tags=["custom"])
   
   @router.get("/")
   async def custom_endpoint():
       return {"message": "Custom endpoint"}
   ```

2. Register in `src/api/app.py`:
   ```python
   from src.api.routers import custom
   app.include_router(custom.router)
   ```

3. Redeploy:
   ```bash
   ./scripts/redeploy_all.sh
   ```

### Enable VPC for Lambda

For database security, run Lambda in VPC:

```bash
# In scripts/deploy_lambda.sh, add VPC configuration:
aws lambda update-function-configuration \\
  --function-name odoo-integration-api \\
  --vpc-config SubnetIds=subnet-xxx,SecurityGroupIds=sg-xxx
```

---

## Cleanup

To remove all AWS resources:

```bash
# Delete Lambda functions
aws lambda delete-function --function-name odoo-integration-api
aws lambda delete-function --function-name odoo-integration-sync

# Delete Lambda layer
aws lambda delete-layer-version --layer-name odoo-integration-deps --version-number 1

# Delete API Gateway
aws apigateway delete-rest-api --rest-api-id YOUR_API_ID

# Delete EventBridge schedule
aws scheduler delete-schedule --name odoo-integration-sync-schedule

# Delete IAM role (if created separately)
aws iam delete-role --role-name odoo-integration-lambda-role
```

---

## Next Steps

- **Monitor**: Set up CloudWatch alarms for Lambda errors
- **Optimize**: Tune Lambda memory/timeout for performance
- **Secure**: Integrate AWS Secrets Manager for credentials
- **Scale**: Add caching layer (Redis/ElastiCache)
- **Extend**: Add more Odoo models (products, sales orders)

For architecture details and development guide, see [README.md](./README.md).
   DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

   # Odoo connection
   ODOO_URL=https://your-company.odoo.com
   ODOO_DB=your-odoo-db-name
   ODOO_USERNAME=your@email
   ODOO_PASSWORD=your-odoo-api-key

   ```

Use a managed Postgres (RDS/Neon/etc.) or a reachable Postgres instance.

### 4. Deploy everything (API + Sync + Layer + Gateway + Schedule)

From the project root:

```bash
./scripts/redeploy_all.sh
```

This script will:

- Build the Lambda deployment package in Docker (`scripts/build_lambda.sh`).
- Deploy two Lambda functions (`scripts/deploy_lambda.sh`):
  - API Lambda: `api_handler` with handler `src.api.app.handler`
  - Sync Lambda: `sync_handler` with handler `src.cron_lambda.handler`
- Build and publish a Lambda layer with Python dependencies and attach it to both functions.
- Create an HTTP API Gateway pointing to `api_handler` and print the API URL.
- Create an EventBridge schedule that periodically triggers `sync_handler`.
- Set up API Gateway CORS and security (API)

When it finishes, it will output something like:

```text
API URL: https://xxxxx.execute-api.<region>.amazonaws.com
Redeploy complete.
```

You can then call your API, for example:

```bash
curl -H "x-api-key: ${API_KEY}" \
     "https://${REST_API_ID}.execute-api.${AWS_REGION}.amazonaws.com/${STAGE_NAME}/partners/"
```

### 5. Customizing names and schedule (optional)

You can override default names without editing the scripts, using environment variables:

```bash
API_NAME="my-odoo-integration-api" \
SYNC_FUNCTION="my-sync-handler" \
SYNC_RULE_NAME="my-sync-daily" \
SYNC_SCHEDULE="rate(12 hours)" \
  ./scripts/redeploy_all.sh
```

Defaults (function names, API name, schedule, etc.) are defined in `scripts/config.sh`.

