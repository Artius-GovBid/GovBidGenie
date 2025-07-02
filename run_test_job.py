# run_test_job.py
import asyncio
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# --- Hardcode all credentials to bypass environment loading issues ---
DATABASE_URL = "postgresql://postgres.ezyrtiaittdxeburpazi:XvUjeDbR78sWJqT9@aws-0-us-east-2.pooler.supabase.com:6543/postgres"
FACEBOOK_PAGE_ID = "1793148737436389"
FACEBOOK_ACCESS_TOKEN = "EAAsf7GtQxqYBO0GNLZBp32MVZCn727XAc3SGIhQBSZCNLn2XBmIX0ExbqKJ5jITbPiJYOrIN268lhlUndinZA60lh5qcftZC9JBRjtnubmZBaZCHrdzI62czvfy6DyCZCJkpLBrj6KMZAbkPXvu7LvnB0EueWnR25QiPkiZAyEAaNrrxOYrTZAxzImfZBv26gBtYIijipZBXIcZCyl25rL5YhFgKzFP69Clv1D2ZBweZAiFSnwZDZD"
# --------------------------------------------------------------------

# Add backend to path
project_dir = os.path.dirname(__file__)
backend_path = os.path.join(project_dir, 'backend')
sys.path.insert(0, backend_path)

# Import services now that path is set
from app.services.lead_service import LeadService
from app.services.facebook_service import FacebookService
from app.services.naics_service import NAICSService
from app.services.conversation_service import ConversationService
from app.db.models import Lead

# Setup database connection using the hardcoded URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestLeadService(LeadService):
    """
    A modified LeadService that bypasses environment loading completely
    by manually instantiating its dependencies with hardcoded credentials.
    """
    def __init__(self, db_session: Session):
        self.db = db_session
        # Manually instantiate FacebookService with credentials
        self.facebook_service = FacebookService(
            page_id=FACEBOOK_PAGE_ID,
            access_token=FACEBOOK_ACCESS_TOKEN
        )
        # NAICSService needs no credentials
        self.naics_service = NAICSService()

class TestConversationService(ConversationService):
    """
    A modified ConversationService that uses hardcoded credentials for its
    FacebookService instance, consistent with the rest of the test script.
    """
    def __init__(self, db_session: Session):
        self.db = db_session
        # Manually instantiate FacebookService with credentials
        self.facebook_service = FacebookService(
            page_id=FACEBOOK_PAGE_ID,
            access_token=FACEBOOK_ACCESS_TOKEN
        )

async def main():
    print("--- Starting E2E test: Lead Creation -> Conversation Initiation ---")
    db = SessionLocal()
    try:
        # STAGE 1: Create new leads
        print("\n--- STAGE 1: Running LeadService to find and create leads ---")
        lead_service = TestLeadService(db_session=db)
        await lead_service.process_new_opportunities()
        print("--- LeadService finished. ---")

        # STAGE 2: Initiate conversation for one of the new leads
        print("\n--- STAGE 2: Running ConversationService to contact a lead ---")
        conversation_service = TestConversationService(db_session=db)
        
        # Find a lead that was just discovered
        discovered_lead = db.query(Lead).filter(Lead.status == "Discovered").first()

        if discovered_lead:
            print(f"Found discovered lead {discovered_lead.id}. Attempting to initiate conversation...")
            conversation_service.initiate_conversation(discovered_lead)
            print(f"--- ConversationService finished for lead {discovered_lead.id}. Check logs for details. ---")
        else:
            print("--- No 'Discovered' leads found to contact. ---")

    except Exception as e:
        print(f"!!! AN UNEXPECTED ERROR OCCURRED: {e} !!!")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("Database session closed.")

if __name__ == "__main__":
    print("Running standalone test job...")
    asyncio.run(main())
    print("--- Standalone test job finished. ---")
