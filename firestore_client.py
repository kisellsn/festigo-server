import json
import os
from datetime import datetime

from google.cloud import firestore
from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app

import transformers
from config import FIREBASE_CREDENTIALS_PATH
from models import Event
from typing import List



load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = FIREBASE_CREDENTIALS_PATH

cred = credentials.Certificate(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
initialize_app(cred)
db = firestore.Client()


def save_events(events: List[Event]):
    collection = db.collection("events")

    for event in events:
        doc_ref = collection.document(event.id)
        doc_ref.set(event.model_dump())

def get_all_events():
    events_ref = db.collection("events")
    return [doc.to_dict() for doc in events_ref.stream()]

from google.cloud.firestore_v1 import DocumentSnapshot

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
    with open("categorized_events.json", "r", encoding="utf-8") as f:
        api_response = json.load(f)

    parsed_events = transformers.transform_events(api_response[2:])
    save_events(parsed_events)
    print(f"Збережено {len(parsed_events)} івентів у Firestore.")

