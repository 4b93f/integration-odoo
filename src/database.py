from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from .config import settings
import asyncio

engine = create_async_engine(settings.database_url, echo=True)

async def pingDatabase():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print(result.scalar())


if __name__ == "__main__":
    asyncio.run(pingDatabase())