import json
import re
from datetime import datetime, timezone
from types import NoneType

import numpy as np
from geopy.distance import geodesic

from recommendation.user_profile import build_profile_vector, geocode_address, get_city_from_address
from recommendation.scoring import score_event_by_components
from recommendation.vectorizer import extract_event_fields_for_vectorization, category_vector, genre_vector, \
    vectorize_field
from services.firestore_client import db

TIME_BUCKETS = {
    "morning": (6, 12),
    "day": (12, 17),
    "evening": (17, 22),
    "weekend": [5, 6]
}

TIME_LABELS_UA = {
    "Ранок": "morning",
    "День": "day",
    "Вечір": "evening",
    "Вихідні": "weekend"
}

DEFAULT_DISTANCE_KM = 50


def is_event_time_suitable(event, preferences):
    start_time = event.get("startTime")
    if not isinstance(start_time, datetime):
        return False

    preferred_times = preferences.get("time", [])
    for bucket in preferred_times:
        mapped = TIME_LABELS_UA.get(bucket)
        if not mapped:
            continue

        if mapped == "weekend":
            if start_time.weekday() in TIME_BUCKETS[mapped]:
                return True
        else:
            low, high = TIME_BUCKETS[mapped]
            if low <= start_time.hour < high:
                return True

    return False


def is_within_distance(user_loc, event_loc, max_km):
    if not user_loc or not event_loc or None in user_loc or None in event_loc:
        return False, None
    try:
        dist = geodesic(user_loc, event_loc).km
        return dist <= max_km, dist
    except Exception:
        return False, None



def recommend_events_for_user(user_id, top_n=20):
    """
    create recommendations for user

    :param user_id
    :param top_n: count of recommendations
    :return: list of recommended events
    """

    # ---------------- user info
    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        return []

    onboarding_doc = db.collection("onboardingResponses").document(user_id).get()
    if not onboarding_doc.exists:
        return []

    responses = onboarding_doc.to_dict()
    answers = responses.get("answers", {})

    # --- координати
    try:
        location_data = answers.get("3")[0]
        user_location_coords = (location_data["lat"], location_data["lon"])
    except (IndexError, KeyError, TypeError):
        user_location_coords = None

    # --- максимальна відстань
    try:
        distance_answer = answers.get("4", [""])[0]
        digits = re.findall(r"\d+", distance_answer)
        max_distance_km = int(digits[0]) if digits else DEFAULT_DISTANCE_KM
    except Exception:
        max_distance_km = DEFAULT_DISTANCE_KM

    preferred_times = answers.get("5", [])


    profile_components = user_doc.to_dict().get("component_profile_vectors")
    if not profile_components:
        profile_components = build_profile_vector(user_id)
        if not profile_components:
            return []

    # ----------------- fav events info
    liked_events_docs = db.collection("users").document(user_id).collection("favourite_events").stream()
    liked_event_refs = [doc.to_dict().get("id") for doc in liked_events_docs]
    liked_events = []
    for event_id in liked_event_refs:
        event_doc = db.collection("events").document(event_id).get()
        if event_doc.exists:
            liked_events.append(event_doc.to_dict())

    aggregated_profile = {}
    weight_liked = 0.7
    weight_profile = 0.3

    if liked_events:
        liked_fields = [extract_event_fields_for_vectorization(event) for event in liked_events]
        field_names = liked_fields[0].keys()

        liked_field_vectors = {}

        for field in field_names:
            if field == "main_categories":
                liked_field_vectors[field] = [category_vector(e[field]) for e in liked_fields]
            elif field == "genres":
                liked_field_vectors[field] = [genre_vector(e[field]) for e in liked_fields]
            else:
                texts = [e[field].lower() for e in liked_fields]
                vectors, _ = vectorize_field(texts)
                liked_field_vectors[field] = vectors

        for field in field_names:
            liked_vecs = np.array(liked_field_vectors[field])
            liked_mean = np.mean(liked_vecs, axis=0)

            #     combined = (liked_mean + profile_vec) / 2
            if profile_components and field in profile_components:
                profile_vec = np.array(profile_components[field])
                combined = liked_mean * weight_liked + profile_vec * weight_profile
                aggregated_profile[field] = combined
            else:
                aggregated_profile[field] = liked_mean

    else:
        # Якщо немає улюблених подій, беремо профіль з анкети
        aggregated_profile = {k: np.array(v) for k, v in profile_components.items()}
        field_names = aggregated_profile.keys()

    # ----------------- events info
    events_docs = db.collection("events").stream()

    events = []
    for doc in events_docs:
        event = doc.to_dict()
        if "component_vectors" not in event:
            continue
        # if not isinstance(event.get("endTime"), datetime) or event["endTime"] < datetime.now(timezone.utc):
        #     continue
        events.append(event)

    scored = []
    for event in events:
        event_components = event.get("component_vectors", {})
        avg_score = score_event_by_components(aggregated_profile, event_components, field_names)

        # --- вплив відстані
        venue = event.get("venue", {})
        lat = venue.get("latitude")
        lon = venue.get("longitude")

        if lat is not None and lon is not None:
            event_coords = (lat, lon)
        else:
            event_coords = None

        within_dist, dist = is_within_distance(user_location_coords, event_coords, max_distance_km)

        if dist is not None:
            if within_dist:
                distance_score_multiplier = 1.0
            else:
                distance_score_multiplier = max(0.1, 1.0 - (dist - max_distance_km) / 100)
            avg_score *= distance_score_multiplier
        elif location_data:
            event_city = get_city_from_address(venue.get("address", ""))
            try:
                user_city = get_city_from_address(location_data.get("title", ""))
            except Exception:
                user_city = location_data
            if user_city and event_city and user_city.lower() != event_city.lower():
                avg_score *= 0.5

        # --- вплив часу
        if not is_event_time_suitable(event, {"time": preferred_times}):
            avg_score *= 0.7

        scored.append((avg_score, event))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [e.get("id") for _, e in scored[:top_n]]

def get_recommendations(user_id, top_n=20):
    return recommend_events_for_user(user_id, top_n)

if __name__ == "__main__":
    # print(len(get_recommendations("5DAGbcxFASgjsUNm15nP3AIlMYu1")))
    print(len(get_recommendations("Ybd9Xb0IsDPdDGySzeXv56D7znJ3")))