import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models.partner import Partner, FIELD_MAP
from src.repositories.partner_repository import PartnerRepository
from src.sync.odoo_client import OdooClient


logger = logging.getLogger(__name__)


class PartnerService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PartnerRepository(session)
        self.odoo_client = OdooClient()

    async def get_all_partners(self) -> List[Partner]:
        return await self.repository.get_all()

    async def get_partner_by_id(self, partner_id: int) -> Optional[Partner]:
        return await self.repository.get_by_id(partner_id)

    async def get_partner_by_odoo_id(self, odoo_id: int) -> Optional[Partner]:
        return await self.repository.get_by_odoo_id(odoo_id)

    async def get_active_partners(self) -> List[Partner]:
        return await self.repository.get_active_partners()

    async def get_partner_count(self) -> int:
        return await self.repository.count()

    async def fetch_from_odoo(self):
        logger.info("Fetching partners from Odoo...")

        try:
            self.odoo_client.authenticate()
            partners_data = self.odoo_client.get_partners()
        except Exception as e:
            logger.error(f"Failed to fetch partners from Odoo: {e}")
            raise

        logger.info(f"Fetched {len(partners_data)} partners from Odoo")
        

        return partners_data
    
    async def sync_from_odoo(self) -> Dict[str, int]:
        logger.info("Starting partner synchronization from Odoo...")
        
        # Fetch and transform
        partners_data = await self.fetch_from_odoo()
        records, odoo_ids = self._transform_odoo_data(partners_data)

        # Save to database
        save_stats = await self.save_partners(records, odoo_ids)
        
        logger.info("Partner synchronization complete.")
        
        return {
            **save_stats,
            "total_fetched": len(records)
        }
    
    async def save_partners(self, records: List[Dict[str, Any]], odoo_ids: List[int]) -> Dict[str, int]:
        logger.info(f"Saving {len(records)} partners to database...")

        upserted_count = 0
        if records:
            upserted_count = await self.repository.upsert_batch(records)
            logger.info(f"Upserted {upserted_count} partners.")

        deleted_count = await self.repository.delete_by_odoo_ids_not_in(odoo_ids)
        if deleted_count:
            logger.info(f"Deleted {deleted_count} partners removed from Odoo.")

        return {
            "upserted": upserted_count,
            "deleted": deleted_count
        }

    def _transform_odoo_data(self, partners_data):
        records = []
        odoo_ids = []

        for partner in partners_data:
            record = {}
            for odoo_field, local_field in FIELD_MAP.items():
                value = partner.get(odoo_field)
                if value is False:
                    record[local_field] = None
                # Odoo many2one fields return [id, name], extract just the id
                elif isinstance(value, (list, tuple)) and len(value) > 0:
                    record[local_field] = value[0]
                else:
                    record[local_field] = value

            record["synced_at"] = datetime.now()
            records.append(record)

            if "odoo_id" in record:
                odoo_ids.append(record["odoo_id"])

        return records, odoo_ids
