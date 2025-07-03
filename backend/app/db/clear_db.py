import os
import sys
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.core.config import settings
from app.db.models import Base, Opportunity, Lead

async def clear_database():
    """
    Connects to the database and truncates the opportunities and leads tables.
    """
    if not settings.DATABASE_URL:
        print("DATABASE_URL not found in environment variables.")
        return

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        # For PostgreSQL, use TRUNCATE for efficiency and to reset sequences.
        # CASCADE drops dependent objects (like foreign key references).
        await conn.execute(text("TRUNCATE TABLE leads, opportunities RESTART IDENTITY CASCADE;"))
        print("Successfully truncated 'leads' and 'opportunities' tables.")

    await engine.dispose()

if __name__ == "__main__":
    print("--- Starting database clearing process ---")
    asyncio.run(clear_database())
    print("--- Database clearing process finished ---") 