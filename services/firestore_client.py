import asyncio
import json
from datetime import datetime

import firebase_admin

from services import transformers
from app.config import FIREBASE_CREDENTIALS_PATH
from firebase_admin import credentials, firestore

from app.models import Event
from typing import List


# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = FIREBASE_CREDENTIALS_PATH
#
# cred = credentials.Certificate(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
# initialize_app(cred)
# db = firestore.Client()
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()


def save_events(events: List[Event]):
    collection = db.collection("events")

    for event in events:
        doc_ref = collection.document(event.id)
        doc_ref.set(event.model_dump())

def get_all_events():
    events_ref = db.collection("events")
    return [doc.to_dict() for doc in events_ref.stream()]


def delete_expired_events():
    now = datetime.now()
    events_ref = db.collection("events")
    deleted_count = 0

    for doc in events_ref.stream():
        event = doc.to_dict()
        end_time = event.get("endTime")
        start_time = event.get("startTime")

        expired = False
        if isinstance(end_time, datetime):
            expired = end_time.astimezone().replace(tzinfo=None) < now
        elif isinstance(start_time, datetime):
            expired = start_time.astimezone().replace(tzinfo=None) < now

        if expired:
            event_id = doc.id
            success = delete_event_by_id(event_id)
            if success:
                deleted_count += 1

    print(f"Deleted {deleted_count} expired events (and removed from favourites).")


def delete_event_by_id(event_id: str) -> bool:
    """Видаляє подію з бд та з усіх favourites"""
    doc_ref = db.collection("events").document(event_id)
    if not doc_ref.get().exists:
        print(f"Event {event_id} not found.")
        return False

    doc_ref.delete()
    print(f"Event {event_id} deleted from events.")

    users = db.collection("users").stream()
    for user in users:
        fav_ref = db.collection("users").document(user.id).collection("favourite_events").document(event_id)
        if fav_ref.get().exists:
            fav_ref.delete()
            print(f"Event {event_id} deleted from user {user.id} favourites.")

    return True


if __name__ == "__main__":
    # Для тестування — завантаження з файлу
    with open("../test_data/categorized_events.json", "r", encoding="utf-8") as f:
        api_response = json.load(f)

    parsed_events = asyncio.run(transformers.transform_events(api_response[2:]))
    print(f"Total raw events fetched: {len(parsed_events)}")
    # save_events(parsed_events)
    # print(f"Збережено {len(parsed_events)} івентів у Firestore.")

    # delete_event_by_id("L2F1dGhvcml0eS9ob3Jpem9uL2NsdXN0ZXJlZF9ldmVudC8yMDI1LTA1LTEwfDQ1NDc3NDU1MjkzNzk4ODE2MQ==")

# L2F1dGhvcml0eS9ob3Jpem9uL2NsdXN0ZXJlZF9ldmVudC8yMDI1LTA1LTEwfDQ1NDc3NDU1MjkzNzk4ODE2MQ==