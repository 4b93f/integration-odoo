import asyncio
from datetime import datetime
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from src.odoo_client import OdooClient
from src.models.partner import FIELD_MAP, Partner
from src.database import engine



async def sync_partners():
    client = OdooClient()

    client.connect()
    client.authenticate()

    partners = client.get_partners()
    records = []
    odoo_ids = []
    for partner in partners:
        record = {}
        for odoo_field, local in FIELD_MAP.items():
            record[local] = partner.get(odoo_field) or None
        record["synced_at"] = datetime.now()
        records.append(record)
        odoo_ids.append(partner["id"])

    for record in records:
        for r in record:
            print(f"  - {r}: {record[r]}")
        print(" --- ")
    
    await upsert_partners(records)
    await delete_removed_partners(odoo_ids)


async def upsert_partners(records):
    async with engine.begin() as conn:
        stmt = insert(Partner).values(records)

        update_dict = {
            c.name: c for c in stmt.excluded
            if c.name not in ("odoo_id", "id", "synced_at")
        }
        update_dict["synced_at"] = stmt.excluded.synced_at

        stmt = stmt.on_conflict_do_update(
            index_elements=["odoo_id"],
            set_=update_dict,
            where=(
                (Partner.name != stmt.excluded.name) |
                (Partner.email != stmt.excluded.email) |
                (Partner.phone != stmt.excluded.phone) |
                (Partner.function != stmt.excluded.function)
            )
        )
        result = await conn.execute(stmt)

        print(f"\n✅ Sync complete: {result.rowcount} records inserted/updated")
        return result.rowcount

async def delete_removed_partners(odoo_ids):
    async with engine.begin() as conn:
        stmt = delete(Partner).where(~Partner.odoo_id.in_(odoo_ids))
        result = await conn.execute(stmt)
        print(f"\n🗑️  Deleted {result.rowcount} partners removed from Odoo")
        return result.rowcount

if __name__ == "__main__":
    asyncio.run(sync_partners())
