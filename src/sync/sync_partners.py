import asyncio
import logging
from sqlmodel.ext.asyncio.session import AsyncSession
from src.services.partner_service import PartnerService
from src.db.database import AsyncSessionLocal


logger = logging.getLogger(__name__)


async def sync_partners(session: AsyncSession):
    service = PartnerService(session)
    try:
        stats = await service.sync_from_odoo()
        logger.info(f"Sync completed: {stats}")
    except Exception as e:
        logger.error(f"Partner synchronization failed: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        async with AsyncSessionLocal() as session:
            await sync_partners(session)
    
    asyncio.run(main())
