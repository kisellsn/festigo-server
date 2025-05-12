import json
from typing import List

from app.config import ALL_GENRES, ALL_CATEGORIES
from app.models import Event
from services.firestore_client import db
from sklearn.feature_extraction.text import TfidfVectorizer

def category_vector(selected_categories):
    """
    Створює вектор для вибраних категорій на основі фіксованого списку.
    """
    return [1 if category in selected_categories else 0 for category in ALL_CATEGORIES]

def genre_vector(selected_genres):
    """
    Створює вектор для вибраних жанрів на основі фіксованого списку.
    """
    return [1 if genre in selected_genres else 0 for genre in ALL_GENRES]


def vectorize_field(texts, stop_words="english"):

    vectorizer = TfidfVectorizer(stop_words=stop_words)
    matrix = vectorizer.fit_transform(texts)
    return matrix.toarray(), vectorizer


def build_event_components(event):
    fields = {
        "name": event.get("name", ""),
        # "description": event.get("description", ""),
        "main_categories": " ".join(event.get("main_categories", [])),
        "genres": " ".join(event.get("genres", [])),
        # "venue_name": event.get("venue", {}).get("name", ""),
        "venue_subtypes": " ".join(event.get("venue", {}).get("subtypes", [])),
        "isVirtual": "virtual" if event.get("isVirtual") else ""
    }
    return {k: v.lower() for k, v in fields.items()}


def extract_event_fields_for_vectorization(event):
    def get_text(val):
        if isinstance(val, list):
            return " ".join(val)
        elif isinstance(val, bool):
            return "online" if val else "offline"
        elif isinstance(val, dict):
            return " ".join(str(v) for v in val.values() if isinstance(v, str))
        return str(val) if val else ""

    return {
        "name": get_text(event.get("name", "")),
        # "description": get_text(event.get("description", "")),
        "main_categories": get_text(event.get("main_categories", [])),
        "genres": get_text(event.get("genres", [])),
        "isVirtual": get_text(event.get("isVirtual", False)),
        # "venue_name": get_text(event.get("venue", {}).get("name", "")),
        "venue_subtypes": get_text(event.get("venue", {}).get("subtypes", []))
    }




def generate_events_vectors(events: List[Event]):
    raw_events = [extract_event_fields_for_vectorization(e.model_dump()) for e in events]
    field_names = raw_events[0].keys()


    field_vectors = {}
    vectorizers = {}

    for field in field_names:
        if field == "main_categories":
            field_vectors[field] = [category_vector(e[field]) for e in raw_events]
        elif field == "genres":
            field_vectors[field] = [genre_vector(e[field]) for e in raw_events]
        else:
            # TfidfVectorizer
            texts = [e[field].lower() for e in raw_events]
            vectors, vec = vectorize_field(texts)
            field_vectors[field] = vectors
            vectorizers[field] = vec

    for i, event in enumerate(events):
        component_vectors = {
            field: field_vectors[field][i].tolist()
            for field in field_names
        }
        event.component_vectors = component_vectors

    return events

# update already existing events
def generate_component_vectors_from_firestore():
    events = list(db.collection("events").stream())
    if not events:
        return

    raw_events = [extract_event_fields_for_vectorization(e.to_dict()) for e in events]
    field_names = raw_events[0].keys()

    field_vectors = {}
    vectorizers = {}

    for field in field_names:
        if field == "main_categories":
            field_vectors[field] = [category_vector(e[field]) for e in raw_events]
        elif field == "genres":
            field_vectors[field] = [genre_vector(e[field]) for e in raw_events]
        else:
            # TfidfVectorizer
            texts = [e[field].lower() for e in raw_events]
            vectors, vec = vectorize_field(texts)
            field_vectors[field] = vectors
            vectorizers[field] = vec

    for doc, original, i in zip(events, raw_events, range(len(events))):
        component_vectors = {
            field: field_vectors[field][i] if isinstance(field_vectors[field][i], list) else field_vectors[field][i].tolist()
            for field in field_names
        }
        db.collection("events").document(doc.id).update({
            "component_vectors": component_vectors
        })

    print("✅ Component vectors added to Firestore events.")

# update already existing events if file to test
def generate_component_vectors_from_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        events = json.load(f)

    raw_events = [extract_event_fields_for_vectorization(e) for e in events]
    field_names = raw_events[0].keys()

    field_vectors = {}
    vectorizers = {}

    for field in field_names:
        if field == "main_categories":
            field_vectors[field] = [category_vector(e[field]) for e in raw_events]
        elif field == "genres":
            field_vectors[field] = [genre_vector(e[field]) for e in raw_events]
        else:
            # TfidfVectorizer
            texts = [e[field].lower() for e in raw_events]
            vectors, vec = vectorize_field(texts)
            field_vectors[field] = vectors
            vectorizers[field] = vec

    for i, event in enumerate(events):
        component_vectors = {
            field: field_vectors[field][i] if isinstance(field_vectors[field][i], list) else field_vectors[field][i].tolist()
            for field in field_names
        }
        event["component_vectors"] = component_vectors

    return events


if __name__ == "__main__":
    filepath = "../test_data/categorized_events.json"
    # with open(filepath, "r", encoding="utf-8") as f:
    #     events = json.load(f)
    updated_events = generate_component_vectors_from_file(filepath)

    with open("../test_data/categorized_events_with_vectors.json", "w", encoding="utf-8") as f:
        json.dump(updated_events, f)
    # generate_component_vectors_from_firestore()