import re
from typing import Optional, Tuple

from app.config import CATEGORY_TRANSLATION, GENRE_TRANSLATION
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

#  TODO: викликати піля отримання рекомендацій
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



if __name__ == "__main__":
    update_profile_vector("5DAGbcxFASgjsUNm15nP3AIlMYu1")
