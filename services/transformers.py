from app.models import Event, Venue
from datetime import datetime
from typing import List

from services.translation_ai import translate_event_fields
from services.translation import translate_text, translate_city

def parse_event(raw: dict) -> Event:
    name_en = raw.get("name", "")
    description_en = raw.get("description", "")
    venue_data = raw.get("venue", {})
    city = venue_data.get("city", "") if venue_data else ""

    # Основні поля для перекладу
    translation_input = {
        "name": name_en,
        "description": description_en,
        "venue_name": venue_data.get("name", ""),
        "city": city,
    }

    translated = translate_event_fields(translation_input)

    name_uk = translated.get("name") or translate_text(name_en)
    description_uk = translated.get("description") or translate_text(description_en) if description_en else None
    venue_name_uk = translated.get("venue_name") or translate_text(venue_data.get("name", "")) if venue_data else ""
    city_uk = translated.get("city") or translate_city(city) if city else ""

    venue = None
    if venue_data:
        subtypes = venue_data.get("subtypes")
        if subtypes is None:
            subtype = venue_data.get("subtype")
            subtypes = [subtype] if subtype else []

        venue = Venue(
            name=venue_data.get("name", ""),
            name_uk=venue_name_uk,
            address=venue_data.get("full_address", ""),
            latitude=venue_data.get("latitude"),
            longitude=venue_data.get("longitude"),
            subtypes=subtypes
        )

    # Посилання
    link = raw.get("link")
    if not link:
        info_links = raw.get("info_links", [])
        ticket_links = raw.get("ticket_links", [])
        if info_links and isinstance(info_links[0], dict):
            link = info_links[0].get("link")
        elif ticket_links and isinstance(ticket_links[0], dict):
            link = ticket_links[0].get("link")

    categories = raw.get("tags", [])
    return Event(
        id=raw["event_id"],
        name=name_en,
        name_uk=name_uk,
        description=description_en,
        description_uk=description_uk,
        link=link,
        imageUrl=raw.get("thumbnail"),
        startTime=datetime.strptime(raw["start_time"], "%Y-%m-%d %H:%M:%S"),
        endTime=datetime.strptime(raw["end_time"], "%Y-%m-%d %H:%M:%S") if raw.get("end_time") else None,
        isVirtual=raw.get("is_virtual", False),
        venue=venue,
        categories_scored=raw.get("categories_scored", []),
        main_categories=categories if categories else raw.get("main_categories", []),
        genres=raw.get("genres", []),
        city=city,
        city_uk=city_uk,
        country=venue_data.get("country", "") if venue_data else "",
        price="-"
    )

def transform_events(raw_data: List[dict]) -> List[Event]:
    return [parse_event(event) for event in raw_data]

if __name__ == "__main__":
    parsed_events = transform_events([{
        "event_id": "L2F1dGhvcml0eS9ob3Jpem9uL2NsdXN0ZXJlZF9ldmVudC8yMDI1LTA1LTEzfDg4NjgwNDA1MDEzMjI0OTU2NzQ=",
        "name": "TNMK (Tanok na Maidani Kongo)",
        "link": None,
        "description": "I have a page in my application(in angular) where the user can post a comment. The comment is stored in Firestore collection with the name o",
        "language": "en",
        "date_human_readable": "Tue, May 13, 7 PM GMT+3",
        "start_time": "2025-05-13 19:00:00",
        "start_time_utc": "2025-05-13 16:00:00",
        "start_time_precision_sec": 1,
        "is_virtual": False,
        "thumbnail": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcROqH_QP2vQmvo8C8veAIfDcIfi3f3L905Iq6Z0E9Sv9Q3eJNAY9gVsxKKwPg&s",
        "ticket_links": [
            {
                "source": "Karabas.com",
                "link": "https://ternopil.karabas.com/en/index.php/clubs/",
                "fav_icon": "https://encrypted-tbn3.gstatic.com/faviconV2?url=https://karabas.com&client=HORIZON&size=96&type=FAVICON&fallback_opts=TYPE,SIZE,URL&nfrp=2"
            }
        ],
        "info_links": [

        ],
        "venue": {
            "google_id": "0x473036c7d0221f29:0x3fa81302bef0d6",
            "name": "PK Berezil",
            "phone_number": None,
            "website": None,
            "review_count": 7,
            "rating": 4.3,
            "subtype": "Transit stop",
            "subtypes": [
                "Transit stop",
                "Bus stop",
                "Trolleybus stop"
            ],
            "full_address": "PK Berezil, Ternopil, Ternopil's'ka oblast, Ukraine, 46003",
            "latitude": 49.54649,
            "longitude": 25.5765,
            "district": None,
            "street": None,
            "city": "Ternopil",
            "zipcode": None,
            "state": "Ternopil Oblast",
            "country": "UA",
            "timezone": "Europe/Kiev",
            "google_mid": "/g/1ptzbh8pg"
        }
    }])

    print(parsed_events)
