from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import asyncio

from app.services.sam_service import SAMService
from app.services.lead_service import LeadService
from app.db.models import Opportunity, Lead

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set for the scheduler.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clear_data_for_test():
    """TEMPORARY: Clears Lead and Opportunity tables for testing."""
    db = SessionLocal()
    try:
        print("Scheduler (TEST): Clearing existing Lead and Opportunity data...")
        db.query(Lead).delete()
        db.query(Opportunity).delete()
        db.commit()
        print("Scheduler (TEST): Data cleared.")
    except Exception as e:
        print(f"Scheduler (TEST): Error clearing data: {e}")
        db.rollback()
    finally:
        db.close()

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
        print("Scheduler: Finished SAM.gov fetch job.")
    except Exception as e:
        print(f"Scheduler: An error occurred during SAM.gov fetch: {e}")
        db.rollback()
    finally:
        db.close()

def run_async_job(job_function):
    """Helper to run an async job from a synchronous scheduler."""
    asyncio.run(job_function())

async def process_opportunities_into_leads_async():
    """
    Initializes the LeadService and processes new opportunities asynchronously.
    """
    print("Scheduler: Starting async lead processing job...")
    db = SessionLocal()
    try:
        lead_service = LeadService(db)
        await lead_service.process_new_opportunities()
        print("Scheduler: Finished async lead processing job.")
    except Exception as e:
        print(f"Scheduler: An error occurred during lead processing: {e}")
        db.rollback()
    finally:
        db.close()


scheduler = BackgroundScheduler()
# Schedule the opportunity fetching job to run every 24 hours
scheduler.add_job(fetch_and_store_opportunities, 'interval', hours=24, id="sam_fetch_job")

# Schedule the lead processing job to run every 24 hours, starting after a delay
scheduler.add_job(
    lambda: run_async_job(process_opportunities_into_leads_async), 
    'interval', 
    hours=24, 
    id="lead_processing_job",
    start_date=datetime.now() + timedelta(minutes=5) 
)


# For immediate testing, run all jobs on startup
scheduler.add_job(clear_data_for_test, 'date', run_date=datetime.now() + timedelta(seconds=2), id="initial_cleanup")
scheduler.add_job(fetch_and_store_opportunities, 'date', run_date=datetime.now() + timedelta(seconds=5), id="initial_sam_fetch")
scheduler.add_job(
    lambda: run_async_job(process_opportunities_into_leads_async), 
    'date', 
    run_date=datetime.now() + timedelta(seconds=30), # Run after the initial fetch
    id="initial_lead_processing"
)