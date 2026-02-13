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


settings = Settings()
