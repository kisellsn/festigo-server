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

REGIONS = {
    "Kyiv Oblast": 2,
    "Lviv Oblast": 2,
    "Odesa Oblast": 2,
    "Kharkiv Oblast": 2,
    "Dnipro Oblast": 2,
}

OTHER_CITIES = [
    "Zaporizhzhia", "Vinnytsia", "Poltava", "Chernihiv", "Cherkasy",
    "Mykolaiv", "Ivano-Frankivsk", "Ternopil", "Chernivtsi", "Uzhhorod",
    "Sumy", "Rivne", "Zhytomyr", "Kropyvnytskyi", "Lutsk"
]


DATE = "next_month"

def fetch_events_for_query(query: str, offset: int = 0, date: str = DATE, is_virtual: bool = False) -> list:
    params = {
        "query": query,
        "date": date,
        "start": str(offset)
    }

    if is_virtual:
        params["is_virtual"] = "true"

    try:
        response = requests.get(EVENTS_API_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json().get("data", [])
        print(f"Fetched {len(data)} events for {query} (offset {offset})")
    except requests.RequestException as e:
        print(f"Error fetching events for {query}: {e}")
        return []

    enriched = assign_categories_to_events(data)
    return enriched

def fetch_and_store_events():
    all_events = []

    # обробка з кількома сторінками
    for location_group in [BIG_CITIES, REGIONS]:
        events = fetch_events_from_locations(location_group)
        all_events.extend(events)

    # 1 сторінка
    other_events = fetch_events_from_single_page(OTHER_CITIES)
    all_events.extend(other_events)

    # онлайн події
    online_events = fetch_events_for_query("ukraine", is_virtual = True)
    all_events.extend(online_events)

    print(f"Total raw events fetched: {len(all_events)}")

    # обробка та збереження
    parsed_events = transform_events(all_events)
    enriched_events = generate_events_vectors(parsed_events)
    save_events(enriched_events)
    print(f"Saved {len(parsed_events)} parsed events to Firestore.")


def fetch_events_from_locations(locations: dict) -> list:
    all_events = []
    for location, max_pages in locations.items():
        location_events = fetch_paginated_events(location, max_pages)
        all_events.extend(location_events)
    return all_events


def fetch_paginated_events(query: str, max_pages: int) -> list:
    all_events = []
    for page in range(max_pages):
        offset = page * 10
        events = fetch_events_for_query(query, offset)

        if not events:
            print(f"No events returned for {query} at offset {offset}.")
            break

        all_events.extend(events)

        if len(events) < 10:
            print(f"Less than 10 events found for {query}, stopping further fetches.")
            break
    return all_events


def fetch_events_from_single_page(cities: list) -> list:
    all_events = []
    for city in cities:
        events = fetch_events_for_query(city)
        all_events.extend(events)
    return all_events

if __name__ == "__main__":
    fetch_and_store_events()
