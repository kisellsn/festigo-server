from apscheduler.schedulers.background import BackgroundScheduler
from services.fetcher import fetch_and_store_events
from services.firestore_client import delete_expired_events, get_last_manual_sync_time
from app.config import SCHEDULE_INTERVAL_HOURS, SCHEDULE_DELETE_INTERVAL_HOURS
from datetime import datetime, timedelta

SKIP_SYNC_FOR_HOURS = 24 * 30

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_sync, 'interval', hours=SCHEDULE_INTERVAL_HOURS)
    scheduler.add_job(delete_expired_events, 'interval', hours=SCHEDULE_DELETE_INTERVAL_HOURS)
    scheduler.start()

def scheduled_sync():
    last_sync = get_last_manual_sync_time()
    now = datetime.now()

    if last_sync and now - last_sync < timedelta(hours=SKIP_SYNC_FOR_HOURS):
        print(f"[Scheduler] ⏭ Skipping sync — last manual was {last_sync.isoformat()}")
        return

    print("[Scheduler] 🔁 Running scheduled sync.")
    fetch_and_store_events()
