import asyncio
from sqlalchemy import select, text
from src.database import engine
from src.models.contact import Contact


async def show_first_contact():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT * FROM contact"))
        rows = result.fetchall()
        
        if rows:
            print(f"\n📋 All Contacts ({len(rows)} total):\n")
            for idx, row in enumerate(rows, 1):
                print(f"Contact #{idx}:")
                for col_idx, column_name in enumerate(result.keys()):
                    print(f"  {column_name}: {row[col_idx]}")
        else:
            print("\n⚠️  No contacts found in database")


if __name__ == "__main__":
    asyncio.run(show_first_contact())
