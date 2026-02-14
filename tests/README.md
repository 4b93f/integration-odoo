# Tests

This directory contains the test suite for the Odoo integration project.

## Running Tests

Install test dependencies:
```bash
pip install -r requirements.txt
```

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_odoo_client.py
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

Run specific test:
```bash
pytest tests/test_odoo_client.py::TestOdooClient::test_connect_success
```

## Test Structure

- `conftest.py` - Shared fixtures and test configuration
- `test_odoo_client.py` - Tests for Odoo API client
- `test_contact_sync.py` - Tests for contact synchronization
- `test_models.py` - Tests for data models
