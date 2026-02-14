from datetime import datetime
from typing import Optional, Dict
from sqlmodel import SQLModel, Field

# Mapping between Odoo field names and local database field names
FIELD_MAP: Dict[str, str] = {
    "id": "odoo_id",
    "name": "name",
    "email": "email",
    "phone": "phone",
    "function": "function",
    "active": "active",
}


class Partner(SQLModel, table=True):
    """
    Partner model representing an Odoo contact (res.partner).
    Used for both database storage and API response schema.
    """
    __tablename__ = "partner"  # Explicitly set table name for foreign key references
    id: Optional[int] = Field(default=None, primary_key=True)
    odoo_id: int = Field(unique=True, index=True)
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    function: Optional[str] = None
    active: bool = Field(default=True)
    synced_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self):
        return f"Partner(id={self.id}, odoo_id={self.odoo_id}, name={self.name}, email={self.email}, phone={self.phone}, function={self.function}, active={self.active}, synced_at={self.synced_at})"