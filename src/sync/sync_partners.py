import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from src.sync.odoo_client import OdooClient
from src.db.models.partner import FIELD_MAP, Partner
from sqlmodel.ext.asyncio.session import AsyncSession


logger = logging.getLogger(__name__)


async def sync_partners(session: AsyncSession):
    logger.info("Starting partner synchronization...")

    client = OdooClient()
    try:
        client.authenticate()
        partners_data = client.get_partners()
    except Exception as e:
        logger.error(f"Failed to fetch data from Odoo: {e}")
        return

    records, odoo_ids = [], []

    for partner in partners_data:
        record = {}
        for odoo_field, local in FIELD_MAP.items():
            value = partner.get(odoo_field)

            if value is False:
                record[local] = None
            elif isinstance(value, (list, tuple)) and len(value) > 0:
                record[local] = value[0]
            else:
                record[local] = value

        record["synced_at"] = datetime.now()
        records.append(record)
        odoo_ids.append(partner["id"])

    if records:
        updated_count = await upsert_partners(records, session)
        logger.info(f"Upserted {updated_count} partners.")

    deleted_count = await delete_removed_partners(odoo_ids, session)
    if deleted_count:
        logger.info(f"Deleted {deleted_count} partners removed from Odoo.")

    logger.info("Partner synchronization complete.")


async def upsert_partners(records: List[Dict[str, Any]], session: AsyncSession) -> int:
    async with session.begin():
        total = 0
        for record in records:
            stmt = insert(Partner).values(record)
            update_dict = {
                c.name: c
                for c in stmt.excluded
                if c.name not in ("id", "odoo_id", "synced_at")
            }
            update_dict["synced_at"] = stmt.excluded.synced_at
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
            result = await session.execute(stmt)
            total += result.rowcount or 0
        return total


async def delete_removed_partners(odoo_ids: List[int], session: AsyncSession) -> int:
    async with session.begin():
        stmt = delete(Partner).where(Partner.odoo_id.notin_(odoo_ids))
        result = await session.execute(stmt)
        return result.rowcount


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(sync_partners())
