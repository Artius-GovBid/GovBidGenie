from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self, sam_service, lead_service, conversation_service, devops_service, db_session_factory: sessionmaker):
        self.scheduler = BackgroundScheduler()
        self.sam_service = sam_service
        self.lead_service = lead_service
        self.conversation_service = conversation_service
        self.devops_service = devops_service
        self.db_session_factory = db_session_factory
        self._add_jobs()

    def _job_wrapper(self, job_function, *args, **kwargs):
        """Wrapper to provide a db session to a job."""
        session = self.db_session_factory()
        try:
            job_function(session, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in scheduled job '{job_function.__name__}': {e}", exc_info=True)
            session.rollback()
        finally:
            session.close()

    def _async_job_wrapper(self, async_job_function, *args, **kwargs):
        """Wrapper to run an async job from the sync scheduler."""
        try:
            # The async job function is responsible for its own session management
            asyncio.run(async_job_function(*args, **kwargs))
        except Exception as e:
            logger.error(f"Error in async scheduled job '{async_job_function.__name__}': {e}", exc_info=True)
    
    def _add_jobs(self):
        # --- Job Definitions ---
        def fetch_opportunities_job(db_session):
            logger.info("Scheduler: Running SAM.gov fetch job...")
            self.sam_service.fetch_and_store_opportunities(db_session)
            logger.info("Scheduler: Finished SAM.gov fetch job.")

        async def process_leads_job():
            logger.info("Scheduler: Running lead processing job...")
            await self.lead_service.process_new_opportunities()
            logger.info("Scheduler: Finished lead processing job.")
        
        def initiate_conversations_job():
            logger.info("Scheduler: Running conversation initiation job...")
            self.conversation_service.process_discovered_leads()
            logger.info("Scheduler: Finished conversation initiation job.")

        # --- Scheduling ---
        run_time_fetch = datetime.now() + timedelta(seconds=5)
        run_time_process = datetime.now() + timedelta(seconds=15)
        run_time_contact = datetime.now() + timedelta(seconds=30)

        self.scheduler.add_job(lambda: self._job_wrapper(fetch_opportunities_job), 'date', run_date=run_time_fetch, id="initial_sam_fetch")
        self.scheduler.add_job(lambda: self._async_job_wrapper(process_leads_job), 'date', run_date=run_time_process, id="initial_lead_processing")
        self.scheduler.add_job(lambda: self._async_job_wrapper(initiate_conversations_job), 'date', run_date=run_time_contact, id="initial_conversation_job")

        self.scheduler.add_job(lambda: self._job_wrapper(fetch_opportunities_job), 'interval', hours=12, id="recurring_sam_fetch")
        self.scheduler.add_job(lambda: self._async_job_wrapper(process_leads_job), 'interval', hours=12, id="recurring_lead_processing", misfire_grace_time=900)
        self.scheduler.add_job(lambda: self._async_job_wrapper(initiate_conversations_job), 'interval', hours=12, id="recurring_conversation_job", misfire_grace_time=900)

    def get_scheduler(self):
        return self.scheduler

scheduler = BackgroundScheduler()