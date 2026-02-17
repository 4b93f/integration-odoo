import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from decimal import Decimal
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models.invoices import Invoice, FIELD_MAP
from src.repositories.invoice_repository import InvoiceRepository
from src.sync.odoo_client import OdooClient


logger = logging.getLogger(__name__)


class InvoiceService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = InvoiceRepository(session)
        self.odoo_client = OdooClient()

    async def get_all_invoices(self) -> List[Invoice]:
        return await self.repository.get_all()

    async def get_invoice_by_id(self, invoice_id: int) -> Optional[Invoice]:
        return await self.repository.get_by_id(invoice_id)

    async def get_invoice_by_odoo_id(self, odoo_id: int) -> Optional[Invoice]:
        return await self.repository.get_by_odoo_id(odoo_id)

    async def get_invoices_by_partner(self, partner_id: int) -> List[Invoice]:
        return await self.repository.get_by_partner_id(partner_id)

    async def get_invoice_count(self) -> int:
        return await self.repository.count()

    async def get_total_amount(self) -> Decimal:
        return await self.repository.get_total_amount()

    async def fetch_from_odoo(self):
        logger.info("Fetching invoices from Odoo...")

        try:
            self.odoo_client.authenticate()
            invoices_data = self.odoo_client.get_invoices()
        except Exception as e:
            logger.error(f"Failed to fetch invoices from Odoo: {e}")
            raise

        logger.info(f"Fetched {len(invoices_data)} invoices from Odoo")
        
        return invoices_data

    async def save_invoices(self, records):
        logger.info(f"Saving {len(records)} invoices to database...")

        upserted_count = 0
        if records:
            upserted_count = await self.repository.upsert_batch(records)
            logger.info(f"Upserted {upserted_count} invoices.")

        return {
            "upserted": upserted_count
        }

    async def sync_from_odoo(self) -> Dict[str, int]:
        logger.info("Starting invoice synchronization from Odoo...")
        
        # Fetch and transform
        invoices_data = await self.fetch_from_odoo()
        records = self._transform_odoo_data(invoices_data)
        
        # Save to database
        save_stats = await self.save_invoices(records)
        
        logger.info("Invoice synchronization complete.")
        
        return {
            **save_stats,
            "total_fetched": len(records)
        }

    def _transform_odoo_data(self, invoices_data):
        records = []

        for invoice in invoices_data:
            record = {}
            for odoo_field, local_field in FIELD_MAP.items():
                value = invoice.get(odoo_field)

                if value is False:
                    record[local_field] = None
                # Odoo many2one fields return [id, name], extract just the id
                elif isinstance(value, (list, tuple)) and len(value) > 0:
                    record[local_field] = value[0]
                else:
                    record[local_field] = value

            record["synced_at"] = datetime.now()
            records.append(record)

        return records
