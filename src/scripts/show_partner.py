"""Display all partners from database."""
import asyncio
from sqlalchemy import text, inspect
from src.database import get_engine


async def show_all_partners():
    """Fetch and display all partners from database."""
    engine = get_engine()
    
    async with engine.connect() as conn:
        # Get table columns dynamically
        result = await conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'partner' "
            "ORDER BY ordinal_position"
        ))
        columns = [row[0] for row in result]
        
        # Fetch all partners
        result = await conn.execute(text("SELECT * FROM partner"))
        partners = result.fetchall()
        
        print(f"\nFound {len(partners)} partners in database:\n")
        
        for partner in partners:
            print("=" * 60)
            for col, value in zip(columns, partner):
                print(f"{col}: {value}")
            print()


if __name__ == "__main__":
    asyncio.run(show_all_partners())
