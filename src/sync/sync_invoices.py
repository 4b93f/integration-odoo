import asyncio
import logging
from src.sync import odoo_client as Odoo_client
from src.db.models.invoices import FIELD_MAP, Invoice
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert


logger = logging.getLogger(__name__)


async def sync_invoices(session: AsyncSession):
    client = Odoo_client.OdooClient()
    client.authenticate()

    try:
        invoices = client.get_invoices()
    except Exception as e:
        logger.error(f"Error fetching invoices: {e}")
        return

    logger.info("Found %d invoices to sync", len(invoices))

    records = []
    for invoice in invoices:
        record = {}
        for odoo_field, local in FIELD_MAP.items():
            value = invoice.get(odoo_field)

            if value is False:
                record[local] = None
            elif isinstance(value, (list, tuple)) and len(value) > 0:
                record[local] = value[0]
            else:
                record[local] = value

        record["synced_at"] = datetime.now()
        records.append(record)

    await upsert_invoices(records, session)


async def upsert_invoices(records: list[dict], session: AsyncSession) -> int:
    async with session.begin():
        total = 0
        for record in records:
            stmt = insert(Invoice).values(record)
            update_dict = {
                c.name: c
                for c in stmt.excluded
                if c.name not in ("id", "odoo_id", "synced_at")
            }
            update_dict["synced_at"] = stmt.excluded.synced_at
            stmt = stmt.on_conflict_do_update(
                index_elements=["odoo_id"], set_=update_dict
            )
            result = await session.execute(stmt)
            total += result.rowcount or 0
        return total


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    asyncio.run(sync_invoices())
