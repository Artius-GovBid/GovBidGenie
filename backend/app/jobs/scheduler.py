from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.services.sam_service import SAMService
from app.db.models import Opportunity

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set for the scheduler.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fetch_and_store_opportunities():
    """
    Fetches opportunities from the SAM.gov API and stores them in the database.
    Prevents duplicates by checking the sam_gov_id.
    """
    print("Scheduler: Starting to fetch opportunities from SAM.gov...")
    sam_service = SAMService()
    db = SessionLocal()
    try:
        # The public API requires a date range. We'll fetch from the last 24 hours.
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        # Format dates as MM/DD/YYYY
        posted_from = yesterday.strftime('%m/%d/%Y')
        posted_to = today.strftime('%m/%d/%Y')

        params = {
            'limit': 100, # Fetch more to increase chance of finding new ones
            'postedFrom': posted_from,
            'postedTo': posted_to
        }

        opportunities_data = sam_service.fetch_opportunities(params=params)
        if not opportunities_data:
            print("Scheduler: No opportunities found in the last 24 hours.")
            return

        new_opportunities = []
        for opp_data in opportunities_data:
            sam_id = opp_data.get('noticeId')
            title = opp_data.get('title')

            # Ensure we have the essential data before proceeding
            if not (sam_id and title):
                continue

            # Check if opportunity already exists
            exists = db.query(Opportunity).filter(Opportunity.sam_gov_id == sam_id).first()
            if not exists:
                
                # Safely parse the posted_date
                posted_date_str = opp_data.get('postedDate')
                posted_date_obj = None
                if posted_date_str:
                    try:
                        # The API returns a simple date 'YYYY-MM-DD'
                        posted_date_obj = datetime.strptime(posted_date_str, '%Y-%m-%d')
                    except ValueError:
                        print(f"Scheduler: Could not parse date '{posted_date_str}' for noticeId {sam_id}. Skipping.")
                        continue
                
                if not posted_date_obj:
                    continue # Skip if date is missing or malformed

                new_opportunities.append(
                    Opportunity(
                        sam_gov_id=sam_id,
                        title=title,
                        url=opp_data.get('uiLink'),
                        agency=opp_data.get('fullParentPathName'), # Use a more reliable agency field
                        posted_date=posted_date_obj
                    )
                )

        if new_opportunities:
            print(f"Scheduler: Found {len(new_opportunities)} new opportunities to store.")
            db.add_all(new_opportunities)
            db.commit()
            print(f"Scheduler: Successfully stored {len(new_opportunities)} new opportunities.")
        else:
            print("Scheduler: No new opportunities to store.")

    except Exception as e:
        print(f"Scheduler: An error occurred: {e}")
        db.rollback()
    finally:
        print("Scheduler: Job finished.")
        db.close()

scheduler = BackgroundScheduler()
# Schedule the job to run every 24 hours
scheduler.add_job(fetch_and_store_opportunities, 'interval', hours=24, id="sam_fetch_job")
# For testing, run every minute. For production, change to hours=24
# scheduler.add_job(fetch_and_store_opportunities, 'interval', minutes=1, id="sam_fetch_job")
