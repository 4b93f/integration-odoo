from datetime import datetime
from typing import Optional, Dict
from sqlmodel import SQLModel, Field


FIELD_MAP: Dict[str, str] = {
    "id": "odoo_id",
    "name": "name",
    "email": "email",
    "phone": "phone",
    "function": "function",
    "active": "active",
}


class Partner(SQLModel, table=True):
    __tablename__ = "partner"
    id: Optional[int] = Field(default=None, primary_key=True)
    odoo_id: int = Field(unique=True, index=True)
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    function: Optional[str] = None
    active: bool = Field(default=True)
    synced_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self):
        return (
            f"Partner(id={self.id}, odoo_id={self.odoo_id}, name={self.name}, "
            f"email={self.email}, phone={self.phone}, function={self.function}, "
            f"active={self.active}, synced_at={self.synced_at})"
        )
