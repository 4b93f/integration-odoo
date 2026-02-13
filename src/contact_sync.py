from src.odoo_client import OdooClient
from src.models.contact import FIELD_MAP, Contact
from src.database import engine
import asyncio
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert



async def sync_contacts():
    client = OdooClient()

    client.connect()
    client.authenticate()

    partners = client.get_partners()
    records = []
    for partner in partners:
        record = {}
        for odooField, local in FIELD_MAP.items():
            record[local] = partner.get(odooField) or None
        record["synced_at"] = datetime.now()
        records.append(record)

    for record in records:
        for r in record:
            print(f"  - {r}: {record[r]}")
    
    await upsert_contacts(records)


async def upsert_contacts(records):
    async with engine.begin() as conn:
        stmt = insert(Contact).values(records)
        stmt = stmt.on_conflict_do_update(
            index_elements=["odoo_id"],
            set_={c.name: c for c in stmt.excluded if c.name != "odoo_id"}
        )
        await conn.execute(stmt)


if __name__ == "__main__":
    asyncio.run(sync_contacts())