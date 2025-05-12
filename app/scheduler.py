from apscheduler.schedulers.background import BackgroundScheduler
from services.fetcher import fetch_and_store_events
from app.config import SCHEDULE_INTERVAL_HOURS, SCHEDULE_DELETE_INTERVAL_HOURS
from services.firestore_client import delete_expired_events


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_store_events, 'interval', hours=SCHEDULE_INTERVAL_HOURS)
    scheduler.add_job(delete_expired_events, 'interval', hours=SCHEDULE_DELETE_INTERVAL_HOURS)
    scheduler.start()