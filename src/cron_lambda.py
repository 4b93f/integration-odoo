import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from src.sync.sync_invoices import sync_invoices
from src.sync.sync_partners import sync_partners
from src.config import settings


async def main():
    engine = create_async_engine(settings.database_url, echo=False)
    SessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with SessionLocal() as session:
        await sync_invoices(session)
        await sync_partners(session)


def handler(event, context):
    asyncio.run(main())
    return {"status": "ok"}
