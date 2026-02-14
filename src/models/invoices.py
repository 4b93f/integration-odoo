from datetime import datetime
from typing import Optional, Dict
from sqlmodel import SQLModel, Field


FIELD_MAP: Dict[str, str] = {
    "id": "odoo_id",
	"partner_id" : "partner_id",
    "name": "name",
    "invoice_date": "date",
    "amount_untaxed": "amount_untaxed",
    "amount_total": "amount_total",
}

class Invoice(SQLModel, table=True):
    __tablename__ = "invoice"  # Explicitly set table name
    id: Optional[int] = Field(default=None, primary_key=True)
    odoo_id: Optional[int] = Field(default=None, unique=True, index=True)
    partner_id: Optional[int] = Field(default=None, foreign_key="partner.odoo_id") # linked to Partner
    name: Optional[str] = None
    date: Optional[str] = None
    amount_untaxed: Optional[float] = None
    amount_total: Optional[float] = None
    synced_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self):
        return f"Invoice(id={self.id}, odoo_id={self.odoo_id}, partner_id={self.partner_id}, name={self.name}, date={self.date}, amount_untaxed={self.amount_untaxed}, amount_total={self.amount_total})"