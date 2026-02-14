import asyncio
from sqlalchemy import inspect, text
from src.database import engine


async def check_db():
    async with engine.connect() as conn:
        # Check if table exists
        result = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        print(f"Tables in database: {result}")
        
        # Count partners
        if 'partner' in result:
            count = await conn.execute(text("SELECT COUNT(*) FROM partner"))
            print(f"Number of partners: {count.scalar()}")


if __name__ == "__main__":
    asyncio.run(check_db())
