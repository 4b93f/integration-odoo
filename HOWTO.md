## How-To: Deploy This Project to Your AWS Account

This project is designed so you can clone it and deploy everything (API + cron sync) into your own AWS account using the provided scripts.

### 1. Prerequisites

- Tools installed
  - Python 3.11+ and `pip`
  - Docker (used to build the Lambda package and layer)
  - AWS CLI v2 (`aws` in your PATH)
- AWS account setup
  - An AWS account with permissions for:
    - Lambda
    - API Gateway v2 (HTTP APIs)
    - EventBridge (Scheduler)
    - IAM (for creating the Lambda execution role)
  - Configure credentials:

    ```bash
    aws configure
    # or set AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_REGION
    ```

### 2. Clone and install dependencies

```bash
git clone <REPO_URL>
cd Chift

python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure environment variables

Environment variables are stored in a `.env` file at the project root and are injected into the Lambda functions by the deploy script.

1. Copy the example file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set at least:

   ```env
   # PostgreSQL database used by the API and sync
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
API_NAME="my-chift-api" \
SYNC_FUNCTION="my-sync-handler" \
SYNC_RULE_NAME="my-sync-daily" \
SYNC_SCHEDULE="rate(12 hours)" \
  ./scripts/redeploy_all.sh
```

Defaults (function names, API name, schedule, etc.) are defined in `scripts/config.sh`.

