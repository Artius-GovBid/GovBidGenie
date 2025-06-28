import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL set for the database client")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This client is for application-level lifecycle (startup/shutdown)
class DBClient:
    def connect(self):
        print("Database connection pool established.")
        # The engine connects lazily, so no explicit connect call is needed here.
        pass

    def disconnect(self):
        print("Database connection pool closed.")
        # Dispose of the connection pool
        engine.dispose()

db_client = DBClient()

# This function is for dependency injection in API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()