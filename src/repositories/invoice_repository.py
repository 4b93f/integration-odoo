"""Invoice repository for data access operations."""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models.invoices import Invoice


logger = logging.getLogger(__name__)


class InvoiceRepository:
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[Invoice]:
        result = await self.session.exec(select(Invoice))
        return result.all()

    async def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        statement = select(Invoice).where(Invoice.id == invoice_id)
        result = await self.session.exec(statement)
        return result.first()

    async def get_by_odoo_id(self, odoo_id: int) -> Optional[Invoice]:
        statement = select(Invoice).where(Invoice.odoo_id == odoo_id)
        result = await self.session.exec(statement)
        return result.first()

    async def get_by_partner_id(self, partner_id: int) -> List[Invoice]:
        statement = select(Invoice).where(Invoice.partner_id == partner_id)
        result = await self.session.exec(statement)
        return result.all()

    async def upsert_batch(self, records: List[Dict[str, Any]]) -> int:
        async with self.session.begin():
            total = 0
            for record in records:
                stmt = insert(Invoice).values(record)
                
                # Build update dict excluding primary key and odoo_id
                update_dict = {
                    c.name: c
                    for c in stmt.excluded
                    if c.name not in ("id", "odoo_id", "synced_at")
                }
                update_dict["synced_at"] = stmt.excluded.synced_at
                
                # Update on conflict with odoo_id
                stmt = stmt.on_conflict_do_update(
                    index_elements=["odoo_id"],
                    set_=update_dict,
                )
                
                result = await self.session.execute(stmt)
                total += result.rowcount or 0
                
            return total
