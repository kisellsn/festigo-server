from models import Event, Venue
from datetime import datetime
from typing import List

def parse_event(raw: dict) -> Event:
    venue_data = raw.get("venue")
    venue = None
    if venue_data:
        venue = Venue(
            name=venue_data["name"],
            address=venue_data["full_address"],
            latitude=venue_data["latitude"],
            longitude=venue_data["longitude"],
            subtypes = [] if venue_data.get("subtypes") is None else venue_data.get("subtypes")
        )

    categories = raw.get("tags", [])

    return Event(
        id=raw["event_id"],
        name=raw["name"],
        description=raw.get("description"),
        link=raw.get("link"),
        imageUrl=raw.get("thumbnail"),
        startTime=datetime.strptime(raw["start_time"], "%Y-%m-%d %H:%M:%S"),
        endTime=datetime.strptime(raw["end_time"], "%Y-%m-%d %H:%M:%S") if raw.get("end_time") else None,
        isVirtual=raw.get("is_virtual", False),
        venue=venue,
        categories_scored=raw.get("categories_scored", []),
        main_categories=categories if categories else raw.get("main_categories", []),
        genres=raw.get("genres", []),
        city=venue_data.get("city", "") if venue_data else "",
        country=venue_data.get("country", "") if venue_data else "",
        price="-"
    )

def transform_events(raw_data: List[dict]) -> List[Event]:
    return [parse_event(event) for event in raw_data]
