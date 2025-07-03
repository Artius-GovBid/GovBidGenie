import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv
from typing import Optional

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.models import Base

def create_tables():
    """
    Connects to the database and creates all tables defined in the models.
    """
    # Load environment variables from the .env file in the 'backend' directory
    env_path: Path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)

    db_url: Optional[str] = os.environ.get("SUPABASE_DB_URL")

    if not db_url:
        print(
            "Error: SUPABASE_DB_URL environment variable not found.\n"
            f"Attempted to load .env file from: {env_path}\n"
            "Please ensure the .env file exists in the 'backend' directory and contains the variable."
        )
        return

    try:
        engine = create_engine(db_url)
        print("Connecting to the database...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully based on the definitions in models.py!")
    except Exception as e:
        print(f"An error occurred while creating tables: {e}")

if __name__ == "__main__":
    create_tables() 