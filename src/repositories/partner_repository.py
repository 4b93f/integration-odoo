"""Partner repository for data access operations."""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models.partner import Partner


logger = logging.getLogger(__name__)


class PartnerRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[Partner]:
        result = await self.session.exec(select(Partner))
        return result.all()

    async def get_by_id(self, partner_id: int) -> Optional[Partner]:
        statement = select(Partner).where(Partner.id == partner_id)
        result = await self.session.exec(statement)
        return result.first()

    async def get_by_odoo_id(self, odoo_id: int) -> Optional[Partner]:
        statement = select(Partner).where(Partner.odoo_id == odoo_id)
        result = await self.session.exec(statement)
        return result.first()

    async def upsert_batch(self, records: List[Dict[str, Any]]) -> int:
        async with self.session.begin():
            total = 0
            for record in records:
                stmt = insert(Partner).values(record)
                
                # Build update dict excluding primary key and odoo_id
                update_dict = {
                    c.name: c
                    for c in stmt.excluded
                    if c.name not in ("id", "odoo_id", "synced_at")
                }
                update_dict["synced_at"] = stmt.excluded.synced_at
                
                # Only update if there are actual changes
                stmt = stmt.on_conflict_do_update(
                    index_elements=["odoo_id"],
                    set_=update_dict,
                    where=(
                        (Partner.name != stmt.excluded.name)
                        | (Partner.email != stmt.excluded.email)
                        | (Partner.phone != stmt.excluded.phone)
                        | (Partner.function != stmt.excluded.function)
                        | (Partner.active != stmt.excluded.active)
                    ),
                )
                
                result = await self.session.execute(stmt)
                total += result.rowcount or 0
                
            return total

    async def delete_by_odoo_ids_not_in(self, odoo_ids: List[int]) -> int:
        async with self.session.begin():
            stmt = delete(Partner).where(Partner.odoo_id.notin_(odoo_ids))
            result = await self.session.execute(stmt)
            return result.rowcount