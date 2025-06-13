import re
from datetime import datetime, timezone
from typing import Optional, Tuple

import numpy as np
from google.cloud import firestore
from sklearn.preprocessing import minmax_scale

from app.config import CATEGORY_TRANSLATION, GENRE_TRANSLATION
from recommendation.scoring import score_event_by_components
from recommendation.vectorizer import genre_vector, category_vector
from services.firestore_client import db


def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """
    geocodes a text address into coordinates (lat, lon).
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

def update_profile_vector(user_id, event_id, alpha = 0.7):
    """
    updates the user profile vector by integrating the last-liked event using exponential smoothing.

    :param event_id: last liked event
    :param alpha: weight
    """
    from sklearn.preprocessing import minmax_scale

    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        return None
    user_data = user_doc.to_dict()
    profile = user_data.get("component_profile_vectors")
    if not profile:
        profile = build_profile_vector(user_id)
        if not profile:
            return None

    # нова подія
    event_doc = db.collection("events").document(event_id).get()
    if not event_doc.exists:
        return None
    event_data = event_doc.to_dict()

    event_vector = {
        "main_categories": category_vector(event_data.get("main_categories", [])),
        "genres": genre_vector(event_data.get("genres", []))
    }

    # оновлення профілю
    updated_profile = {}
    for key in event_vector:
        old_vec = profile.get(key)
        new_vec = event_vector[key]
        if not old_vec or len(old_vec) != len(new_vec):
            updated_profile[key] = new_vec
        else:
            combined = [alpha * new + (1 - alpha) * old for old, new in zip(old_vec, new_vec)]
            scaled = minmax_scale(combined)
            total = sum(scaled)
            normalized = [v / total for v in scaled] if total > 0 else scaled
            thresholded = [v if v > 0.02 else 0 for v in normalized]
            total_thresh = sum(thresholded)
            updated_profile[key] = [v / total_thresh for v in thresholded] if total_thresh > 0 else thresholded

    # Зберігаємо
    db.collection("users").document(user_id).update({
        "component_profile_vectors": updated_profile
    })

    return updated_profile



def get_similar_to_last_liked(user_id, top_n=10):
    """
    returns similar events to the user's last-liked event
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

    # вектори останньої лайкнутої події
    base_components = base_event["component_vectors"]
    field_names = base_components.keys()
    base_components = {k: np.array(v) for k, v in base_components.items()}

    # майбутні події
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

    # схожість
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
    # print(update_profile_vector(
    #     "5DAGbcxFASgjsUNm15nP3AIlMYu1",
    #     "L2F1dGhvcml0eS9ob3Jpem9uL2NsdXN0ZXJlZF9ldmVudC8yMDI1LTA0LTI2fDEwMDM1NTU5OTk3MDA0MjA2Nzk4"))

