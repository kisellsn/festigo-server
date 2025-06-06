import re
from datetime import datetime, timezone
from typing import Optional, Tuple

import numpy as np
from google.cloud import firestore

from app.config import CATEGORY_TRANSLATION, GENRE_TRANSLATION
from recommendation.scoring import score_event_by_components
from recommendation.vectorizer import genre_vector, category_vector
from services.firestore_client import db


def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Геокодує текстову адресу в координати (lat, lon).
    """
    pass
def get_city_from_address(address):
    if address:
        address_parts = [part.strip() for part in re.split(r'[,\s]+', address.lower())]
        return address_parts[0] if address_parts else ""
    return ""



def build_profile_vector(user_id):
    """
        creates profile vector for new user based on interests from onboarding responses
    """
    onboarding_doc = db.collection("onboardingResponses").document(user_id).get()
    if not onboarding_doc.exists:
        return None

    onboarding = onboarding_doc.to_dict()
    answers = onboarding.get("answers", {})

    # translate and normalize
    selected_categories = [CATEGORY_TRANSLATION.get(x, "other") for x in answers.get("0", [])]
    selected_genres_music = [GENRE_TRANSLATION.get(x, "other") for x in answers.get("1", [])]
    selected_genres_theater = [GENRE_TRANSLATION.get(x, "other") for x in answers.get("2", [])]

    profile_texts = {
        "main_categories": selected_categories,
        "genres": selected_genres_music + selected_genres_theater,
    }

    profile_components = {}
    for field, selected_items in profile_texts.items():
        vector = genre_vector(selected_items) if field == "genres" else category_vector(selected_items)
        profile_components[field] = vector

    # print(profile_components)
    db.collection("users").document(user_id).update({
        "component_profile_vectors": profile_components
    })
    return profile_components

def update_profile_vector(user_id: str):
    """
    Updates the user's profile vector by averaging the onboarding profile with
    the one derived from liked (favourite) events.
    """
    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        return None

    user_data = user_doc.to_dict()
    existing_profile = user_data.get("component_profile_vectors")
    if not existing_profile:
        build_profile_vector(user_id)

    # Завантаження улюблених подій
    favourite_events_ref = db.collection("users").document(user_id).collection("favourite_events")
    favourite_events = list(favourite_events_ref.stream())

    if not favourite_events:
        return None

    liked_categories = set()
    liked_genres = set()

    for fav_event in favourite_events:
        fav_data = fav_event.to_dict()
        event_id = fav_data.get("id")
        if not event_id:
            continue

        event_doc = db.collection("events").document(event_id).get()
        if not event_doc.exists:
            continue

        event_data = event_doc.to_dict()
        liked_categories.update(event_data.get("main_categories", []))
        liked_genres.update(event_data.get("genres", []))

    # new vector
    new_profile_components = {
        "main_categories": category_vector(list(liked_categories)),
        "genres": genre_vector(list(liked_genres))
    }
    # print(new_profile_components)
    # avg з існуючим профілем
    averaged_profile = {}
    for key in new_profile_components:
        old_vector = existing_profile.get(key)
        new_vector = new_profile_components[key]
        if not old_vector or len(old_vector) != len(new_vector):
            averaged_profile[key] = new_vector  # fallback
        else:
            averaged = [0.3 * old + 0.7 * new for old, new in zip(old_vector, new_vector)]
            averaged_profile[key] = averaged

    # print(averaged_profile)
    db.collection("users").document(user_id).update({
        "component_profile_vectors": averaged_profile
    })

    return averaged_profile


def get_similar_to_last_liked(user_id, top_n=10):
    """
    Повертає подібні події до останньої лайкнутої події користувача
    """
    fav_ref = db.collection("users").document(user_id).collection("favourite_events")
    fav_docs = list(fav_ref.order_by("date_created", direction=firestore.Query.DESCENDING).limit(1).stream())

    if not fav_docs:
        return []

    last_fav_id = fav_docs[0].to_dict().get("id")
    if not last_fav_id:
        return []

    event_doc = db.collection("events").document(last_fav_id).get()
    if not event_doc.exists:
        return []

    base_event = event_doc.to_dict()

    if "component_vectors" not in base_event:
        return []

    # 2. Витягуємо вектори останньої лайкнутої події
    base_components = base_event["component_vectors"]
    field_names = base_components.keys()
    base_components = {k: np.array(v) for k, v in base_components.items()}

    # 3. Витягуємо всі майбутні події з векторами
    events_docs = db.collection("events").stream()

    events = []
    for doc in events_docs:
        e = doc.to_dict()
        if "component_vectors" not in e:
            continue
        # if not isinstance(e.get("endTime"), datetime) or e["endTime"] < datetime.now(timezone.utc):
        #     continue
        if e.get("id") == last_fav_id:
            continue
        events.append(e)

    # 4. Рахуємо схожість (косинусна відстань або dot product)
    scored = []
    for event in events:
        ev_vecs = {k: np.array(v) for k, v in event["component_vectors"].items() if k in field_names}

        score = score_event_by_components(base_components, ev_vecs, field_names)
        scored.append((score, event))

    scored.sort(reverse=True, key=lambda x: x[0])
    similar_ids = [e["id"] for score, e in scored[:top_n]]
    return similar_ids, last_fav_id

if __name__ == "__main__":
    print(get_similar_to_last_liked("5DAGbcxFASgjsUNm15nP3AIlMYu1"))
