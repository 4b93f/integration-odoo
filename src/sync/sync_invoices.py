import asyncio
import logging
from sqlmodel.ext.asyncio.session import AsyncSession
from src.services.invoice_service import InvoiceService
from src.db.database import AsyncSessionLocal


logger = logging.getLogger(__name__)


async def sync_invoices(session: AsyncSession):
    service = InvoiceService(session)
    try:
        stats = await service.sync_from_odoo()
        logger.info(f"Sync completed: {stats}")
    except Exception as e:
        logger.error(f"Invoice synchronization failed: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        async with AsyncSessionLocal() as session:
            await sync_invoices(session)
    
    asyncio.run(main())
