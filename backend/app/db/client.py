import os
from dotenv import load_dotenv
from supabase import create_client, Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Supabase connection
url: Optional[str] = os.environ.get("SUPABASE_URL")
key: Optional[str] = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in the environment.")

supabase: Client = create_client(url, key)

# SQLAlchemy connection for relationship handling
# Note: Replace with your actual Supabase Postgres connection string
DATABASE_URL: Optional[str] = os.environ.get("SUPABASE_DB_URL")
if not DATABASE_URL:
    raise ValueError("SUPABASE_DB_URL must be set in the environment.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
