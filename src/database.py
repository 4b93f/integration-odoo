import asyncio

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from .config import settings

engine = create_async_engine(settings.database_url, echo=False)

async def ping_database():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print(result.scalar())


if __name__ == "__main__":
    asyncio.run(ping_database())