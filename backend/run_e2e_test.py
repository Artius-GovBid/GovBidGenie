import os
import random
import string
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Opportunity, Lead
from app.db.client import DATABASE_URL as DB_URL_FROM_CONFIG

# --- Test Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", DB_URL_FROM_CONFIG)
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment or config.")

def run_test():
    """Main function to run the E2E test."""
    engine = create_engine(str(DATABASE_URL))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    mock_sam_id = f"E2E-TEST-{unique_id}"
    mock_opp = None
    mock_lead = None

    try:
        print("--- Starting E2E Test ---")

        # 1. Create mock opportunity and lead
        print("1. Creating mock opportunity...")
        mock_opp = Opportunity(
            sam_gov_id=mock_sam_id,
            title=f"E2E Test: {unique_id}",
            agency="Department of Testing",
            url=f"http://sam.gov/{mock_sam_id}",
            posted_date=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db.add(mock_opp)
        db.commit()
        db.refresh(mock_opp)

        print("2. Creating mock lead...")
        mock_lead = Lead(
            opportunity_id=mock_opp.id,
            business_name=f"TestCorp LLC ({unique_id})",
            status="IDENTIFIED", # Initial state
            created_at=datetime.utcnow(),
            last_updated_at=datetime.utcnow()
        )
        db.add(mock_lead)
        db.commit()
        db.refresh(mock_lead)
        print(f"   - Created Lead ID: {mock_lead.id} for Opportunity ID: {mock_opp.id}")
        
        # 3. Update status to trigger DevOps integration
        print("\n3. Updating lead status to APPOINTMENT_SET...")
        db.query(Lead).filter(Lead.id == mock_lead.id).update({
            "status": "APPOINTMENT_SET",
            "last_updated_at": datetime.utcnow()
        })
        db.commit()
        print("   - Lead status updated. Trigger should have fired.")

        print("\n4. Test complete.")
        print("   - Please check your Azure DevOps board for a new work item.")
        print(f"   - Title should be: 'TestCorp LLC ({unique_id})'")

    except Exception as e:
        print(f"\nAn error occurred during the test: {e}")
        db.rollback()
    finally:
        # --- Cleanup ---
        print("\n--- Cleaning up test data ---")
        if db:
            if mock_lead:
                db.query(Lead).filter(Lead.id == mock_lead.id).delete()
            if mock_opp:
                db.query(Opportunity).filter(Opportunity.id == mock_opp.id).delete()
            db.commit()
            db.close()
            print("Cleanup complete.")

if __name__ == "__main__":
    run_test()
