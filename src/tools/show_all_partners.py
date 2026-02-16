import asyncio
from sqlalchemy import text
from src.db.database import engine


async def show_all_partners():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT * FROM partner"))
        rows = result.fetchall()

        if rows:
            print(f"\n📋 All Partners ({len(rows)} total):\n")
            for idx, row in enumerate(rows, 1):
                print(f"Partner #{idx}:")
                for col_idx, column_name in enumerate(result.keys()):
                    print(f"  {column_name}: {row[col_idx]}")
        else:
            print("\n⚠️  No partners found in database")


if __name__ == "__main__":
    asyncio.run(show_all_partners())
