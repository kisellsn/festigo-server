import json
import os
from datetime import datetime

import firebase_admin
from dotenv import load_dotenv

from google.cloud import firestore
from firebase_admin import credentials, initialize_app

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

        if isinstance(end_time, datetime):
            if end_time.astimezone().replace(tzinfo=None) < now:
                doc.reference.delete()
                deleted_count += 1
        elif isinstance(start_time, datetime):
            if start_time.astimezone().replace(tzinfo=None) < now:
                doc.reference.delete()
                deleted_count += 1

    print(f"Deleted {deleted_count} expired events.")


if __name__ == "__main__":
    # Для тестування — завантаження з файлу
    with open("../test_data/categorized_events.json", "r", encoding="utf-8") as f:
        api_response = json.load(f)

    parsed_events = transformers.transform_events(api_response[2:])
    save_events(parsed_events)
    print(f"Збережено {len(parsed_events)} івентів у Firestore.")

