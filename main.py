from fastapi import FastAPI

from firestore_client import delete_expired_events
from scheduler import start_scheduler
from fetch_and_store import fetch_and_store_events
# pip freeze > requirements.txt
# pip install -r requirements.txt
# uvicorn main:app --reload

app = FastAPI()

@app.on_event("startup")
def on_startup():
    start_scheduler()

@app.get("/")
def root():
    return {"status": "Event sync API is running"}

@app.post("/sync")
def manual_sync():
    fetch_and_store_events()
    return {"status": "Manual sync complete"}

@app.post("/cleanup")
def manual_cleanup():
    delete_expired_events()
    return {"status": "Expired events deleted"}