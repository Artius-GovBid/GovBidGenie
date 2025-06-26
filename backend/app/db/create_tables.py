import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.models import Base

def create_tables():
    """
    Connects to the database and creates all tables defined in the models.
    """
    # Construct a robust path to the .env file in the 'backend' directory
    # Path(__file__).parent.parent.parent gives us the path to the 'backend' directory
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    
    db_url = os.environ.get("SUPABASE_DB_URL")
    
    # --- TEMPORARY FIX ---
    # Bypassing the .env file to test the connection string directly.
    # db_url = "postgresql://postgres:XvUjeDbR78sWJqT9@db.xiaxbkipvrgxubrcybna.supabase.co:6543/postgres"

    if not db_url:
        print("Error: SUPABASE_DB_URL environment variable not set.")
        print(f"Attempted to load .env file from: {env_path}")
        print("Please ensure the .env file exists in the 'backend' directory and contains the variable.")
        return

    try:
        # --- DEBUGGING ---
        # print(f"Attempting to connect with URL: '{db_url}'")
        engine = create_engine(db_url)
        print("Connecting to the database...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_tables() 