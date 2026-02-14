import sys
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / '.env',
        extra='ignore',
    )

    odoo_url: str
    odoo_db: str
    odoo_username: str
    odoo_password: str
    database_url: str


try:
    settings = Settings()
except (ValueError, TypeError) as e:
    env_file = Path(__file__).parent.parent / '.env'
    print("\n❌ Configuration Error: Missing or invalid .env file")
    print("F\nPlease create a .env file at: {env_file}")
    print("\nRequired variables:")
    print("  ODOO_URL=https://your-odoo-instance.com")
    print("  ODOO_DB=your_database_name")
    print("  ODOO_USERNAME=your_username")
    print("  ODOO_PASSWORD=your_password")
    print("  DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname")
    print(f"\nError details: {e}\n")
    sys.exit(1)
