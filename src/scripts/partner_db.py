import asyncio
import sys
from sqlmodel import SQLModel
from src.database import engine
from src.models.partner import Partner


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all, checkfirst=True)

async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Partner.__table__.drop, checkfirst=True)

if __name__ == "__main__":
    choice = input("Do you want to create (c) or drop (d) tables? ")
    if choice.lower() == 'c':
        asyncio.run(create_tables())
    elif choice.lower() == 'd':
        asyncio.run(drop_tables())
    else:
        print("Invalid choice. Please enter 'c' to create or 'd' to drop tables.")
        sys.exit(1)