from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.services.sam_service import SAMService
from app.services.lead_service import LeadService
from app.db.models import Opportunity

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set for the scheduler.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fetch_and_store_opportunities():
    """
    Fetches opportunities from the SAM.gov API and stores them in the database
    by calling the SAMService.
    """
    print("Scheduler: Starting SAM.gov fetch job...")
    db = SessionLocal()
    try:
        sam_service = SAMService()
        sam_service.fetch_and_store_opportunities(db)
    except Exception as e:
        print(f"Scheduler: An error occurred during SAM.gov fetch: {e}")
        db.rollback()
    finally:
        db.close()

def process_opportunities_into_leads():
    """
    Initializes the LeadService and processes new opportunities.
    """
    print("Scheduler: Starting lead processing job...")
    db = SessionLocal()
    try:
        lead_service = LeadService(db)
        lead_service.process_new_opportunities()
    except Exception as e:
        print(f"Scheduler: An error occurred during lead processing: {e}")
        db.rollback()
    finally:
        db.close()

scheduler = BackgroundScheduler()
# Schedule the opportunity fetching job to run every 24 hours
scheduler.add_job(fetch_and_store_opportunities, 'interval', hours=24, id="sam_fetch_job")

# Run the job immediately on startup
scheduler.add_job(fetch_and_store_opportunities, 'date', run_date=datetime.now() + timedelta(seconds=5))
