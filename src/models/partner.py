from datetime import datetime
from sqlmodel import SQLModel, Field


FIELD_MAP = {
    "id": "odoo_id",
    "name": "name",
    "email": "email",
    "phone": "phone",
    "function": "function",
    "active": "active",
}


class Partner(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    odoo_id: int = Field(unique=True, index=True)
    name: str
    email: str | None = None
    phone: str | None = None
    function: str | None = None
    active: bool = Field(default=True)
    synced_at: datetime = Field(default_factory=datetime.utcnow)
