from app.config import EVENTS_API_URL, RAPIDAPI_KEY, RAPIDAPI_HOST
from categorization.event_categorization import assign_categories_to_events
from recommendation.vectorizer import generate_events_vectors
from services.transformers import transform_events
from services.firestore_client import save_events
import requests

HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST,
}

BIG_CITIES = {
    "Kyiv": 3,
    "Lviv": 3,
    "Odesa": 3,
    "Kharkiv": 3,
    "Dnipro": 3
}

OTHER_CITIES = [
    "Zaporizhzhia", "Vinnytsia", "Poltava", "Chernihiv", "Cherkasy",
    "Mykolaiv", "Ivano-Frankivsk", "Ternopil", "Chernivtsi", "Uzhhorod",
    "Sumy", "Rivne", "Zhytomyr", "Kropyvnytskyi", "Lutsk"
]

DATE = "month"

def fetch_events_for_city(city: str, offset: int = 0) -> list:
    params = {
        "query": city,
        "date": DATE,
        "start": str(offset),
    }
    try:
        response = requests.get(EVENTS_API_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json().get("data", [])
        print(f"Fetched {len(data)} events for {city} (offset {offset})")
    except requests.RequestException as e:
        print(f"Error fetching events for {city}: {e}")
        return []

    enriched = assign_categories_to_events(data)
    return enriched


def fetch_and_store_events():
    all_events = []

    for city, max_pages in BIG_CITIES.items():
        for page in range(max_pages):
            offset = page * 10
            events = fetch_events_for_city(city, offset)

            if not events:
                print(f"No events returned for {city} at offset {offset}.")
                break

            all_events.extend(events)

            if len(events) < 10:
                print(f"Less than 10 events found for {city}, stopping further fetches.")
                break

    for city in OTHER_CITIES:
        events = fetch_events_for_city(city)
        all_events.extend(events)

    print(f"Total raw events fetched: {len(all_events)}")

    parsed_events = transform_events(all_events)
    enriched_events = generate_events_vectors(parsed_events)
    save_events(enriched_events)
    print(f"Saved {len(parsed_events)} parsed events to Firestore.")

if __name__ == "__main__":
    fetch_and_store_events()
