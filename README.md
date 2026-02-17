# Odoo Integration Service

> A production-ready FastAPI service that synchronizes Odoo partners and invoices to PostgreSQL with a clean 3-layer architecture.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange.svg)](https://aws.amazon.com/lambda/)
[![Tests](https://img.shields.io/badge/tests-15%20passing-brightgreen.svg)](./tests/)

## 🏗️ Architecture

This project follows **Separation of Concerns (SoC)** with a clean 3-layer architecture:

![Architecture Workflow](./Workflow.png)

```
┌─────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                     │
│  • FastAPI Routers (partners.py, invoices.py)          │
│  • Sync Scripts (sync_partners.py, sync_invoices.py)   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│  SERVICE LAYER (Business Logic)                         │
│  • PartnerService  • InvoiceService                     │
│  • Odoo integration • Data transformation               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│  REPOSITORY LAYER (Data Access)                         │
│  • PartnerRepository  • InvoiceRepository               │
│  • Pure database operations • No business logic         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
              ┌──────────────┐
              │  PostgreSQL  │
              └──────────────┘
```

## ✨ Features

- **🔄 Automated Sync**: EventBridge-triggered Lambda syncs Odoo data every 15 minutes
- **🚀 REST API**: Fast, secure API Gateway with API key authentication
- **🏛️ Clean Architecture**: Service layer, repository pattern, dependency injection
- **📊 Two Data Models**: Partners and Invoices with full relationship support
- **✅ Well Tested**: 15 passing tests with mocked dependencies
- **🐳 Dockerized Build**: Consistent Lambda deployment packages
- **☁️ AWS Native**: Lambda, API Gateway, EventBridge, Neon PostgreSQL

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker
- AWS CLI v2 configured
- Odoo instance with API access
- PostgreSQL database (Neon recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/4b93f/integration-odoo.git
cd integration-odoo

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
ODOO_URL=https://your-company.odoo.com
ODOO_DB=your-odoo-db-name
ODOO_USERNAME=your@email
ODOO_PASSWORD=your-odoo-api-key
```

### Deployment

```bash
# Deploy everything to AWS (API + Sync + Scheduler)
./scripts/redeploy_all.sh
```

Outputs:
```
API URL: https://xxxxx.execute-api.eu-west-1.amazonaws.com/prod
API Key: PUb1TzXqB64NfqoO0sYpAabx1maPbmjQ1oArHwop
```

### Usage

```bash
# List all partners
curl -H "x-api-key: YOUR_API_KEY" \
  https://xxxxx.execute-api.eu-west-1.amazonaws.com/prod/partners/

# Get specific partner by Odoo ID
curl -H "x-api-key: YOUR_API_KEY" \
  https://xxxxx.execute-api.eu-west-1.amazonaws.com/prod/partners/123

# List all invoices
curl -H "x-api-key: YOUR_API_KEY" \
  https://xxxxx.execute-api.eu-west-1.amazonaws.com/prod/invoices/
```

## 📁 Project Structure

```
.
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── app.py             # Main FastAPI app + Lambda handler
│   │   └── routers/           # API endpoints
│   │       ├── partners.py    # Partner endpoints
│   │       └── invoices.py    # Invoice endpoints
│   ├── services/              # Business logic layer
│   │   ├── partner_service.py # Partner operations
│   │   └── invoice_service.py # Invoice operations
│   ├── repositories/          # Data access layer
│   │   ├── partner_repository.py
│   │   └── invoice_repository.py
│   ├── sync/                  # Odoo synchronization
│   │   ├── odoo_client.py     # Odoo API client
│   │   ├── sync_partners.py   # Partner sync logic
│   │   └── sync_invoices.py   # Invoice sync logic
│   ├── db/                    # Database models & config
│   │   ├── database.py        # SQLModel async setup
│   │   └── models/            # SQLModel definitions
│   └── cron_lambda.py         # Lambda handler for scheduled sync
├── scripts/                   # Deployment automation
│   ├── redeploy_all.sh       # Full deployment
│   ├── build_lambda.sh       # Docker build
│   ├── deploy_lambda.sh      # Lambda deployment
│   └── setup_apigw.sh        # API Gateway setup
├── tests/                     # Test suite
│   ├── test_services.py      # Service layer tests
│   ├── test_partner_sync.py  # Sync tests
│   └── test_models.py        # Model validation tests
└── requirements.txt          # Python dependencies
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_services.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

Current coverage: **15 tests passing** ✅

## 🔧 Development

### Running Locally

```bash
# Start FastAPI dev server
uvicorn src.api.app:app --reload --port 8000

# Run manual sync
python -m src.sync.sync_partners
python -m src.sync.sync_invoices
```

### Architecture Patterns

#### Service Layer
Handles business logic and orchestration:
```python
service = PartnerService(session)

# Fetch from Odoo (transforms data)
records, odoo_ids = await service.fetch_from_odoo()

# Save to database (handles upsert + cleanup)
stats = await service.save_partners(records, odoo_ids)

# Or do both in one call
stats = await service.sync_from_odoo()
```

#### Repository Layer
Pure database operations:
```python
repo = PartnerRepository(session)

partners = await repo.get_all()
partner = await repo.get_by_odoo_id(123)
await repo.upsert_batch(records)
```

### Adding New Features

1. **Add a new endpoint**: Create route in `src/api/routers/`
2. **Add business logic**: Extend service in `src/services/`
3. **Add database operation**: Extend repository in `src/repositories/`
4. **Add tests**: Create test file in `tests/`

## 📊 API Documentation

Once deployed, visit:
```
https://YOUR_API_URL/docs        # Swagger UI
https://YOUR_API_URL/redoc       # ReDoc
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/partners/` | List all partners |
| GET | `/partners/{odoo_id}` | Get partner by Odoo ID |
| GET | `/invoices/` | List all invoices |
| GET | `/invoices/{id}` | Get invoice by ID |

## 🔐 Security

- **API Key Authentication**: All endpoints require `x-api-key` header
- **AWS IAM**: Lambda execution roles with least-privilege
- **VPC Support**: Can run Lambda in VPC for database security
- **Environment Variables**: Secrets stored in Lambda environment (can integrate with Secrets Manager)

## 🔄 Sync Process

EventBridge triggers sync every 15 minutes:

1. **Fetch**: Authenticate with Odoo, fetch partners/invoices
2. **Transform**: Map Odoo fields to database schema
3. **Upsert**: Insert new records, update existing (based on `odoo_id`)
4. **Cleanup**: Delete partners removed from Odoo
5. **Log**: Report statistics (upserted, deleted, total)

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `ODOO_URL` | Odoo instance URL | Yes |
| `ODOO_DB` | Odoo database name | Yes |
| `ODOO_USERNAME` | Odoo API username | Yes |
| `ODOO_PASSWORD` | Odoo API key/password | Yes |

## 🐛 Troubleshooting

See [HOWTO.md](./HOWTO.md) for detailed deployment guide and troubleshooting.