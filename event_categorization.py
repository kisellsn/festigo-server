import re
from typing import Dict, List, Tuple
import json
from typing import List, Dict

# Категорії
CATEGORY_KEYWORDS = {
    "music": {
        "concert": 1.0, "music": 0.9, "live": 0.8, "band": 0.8, "dj": 0.9, "orchestra": 0.7, "gig": 0.7,
        "rock": 0.7, "pop": 0.7, "electronic": 0.7, "jazz": 0.7, "rap": 0.7, "hip hop": 0.7, "folk": 0.7
    },
    "show": {
        "theatre": 1.0, "drama": 0.9, "performance": 0.8, "actor": 0.8, "play": 0.8, "comedy": 0.7,
        "tragicomedy": 0.7, "improv": 0.7, "stand-up": 0.7, "ballet": 0.7, "humor": 0.7
    },
    "festival": {
        "festival": 1.0, "fair": 0.8, "parade": 0.8, "street": 0.6, "celebration": 0.7
    },
    "exhibition": {
        "exhibition": 1.0, "gallery": 0.9, "museum": 0.9, "art": 0.8, "vernissage": 0.8
    },
    "cinema": {
        "cinema": 1.0, "movie": 0.9, "film": 0.9, "screening": 0.8, "premiere": 0.7
    },
    "education": {
        "lecture": 0.9, "workshop": 0.9, "course": 0.8, "training": 0.8, "seminar": 0.8, "conference": 0.7,
        "webinar": 0.8, "masterclass": 0.9
    },
    "sport": {
        "match": 1.0, "game": 0.9, "tournament": 0.8, "sports": 0.8, "football": 0.8, "basketball": 0.8,
        "marathon": 0.8, "yoga": 0.7, "run": 0.7, "fitness": 0.7, "activity": 0.9
    }
}
GENRES = {
    "music": ["rock", "pop", "jazz", "electronic", "classical", "folk", "rap", "hip hop", "metal", "indie", "punk", "techno"],
    "show": ["comedy", "drama", "tragicomedy", "ballet", "musical", "stand-up", "opera", "monodrama"],
    "cinema": ["thriller", "horror", "drama", "action", "sci-fi", "documentary", "romance", "animation"]
}

IMPLICIT_GENRE_HINTS = {
    "improvisation": "comedy",
    "improv": "comedy",
    "standup": "stand-up",
    "stand up": "stand-up",
    "symphony": "classical",
    "piano": "classical",
    "techno party": "techno",
    "film noir": "drama",
    "romcom": "romance",
    "romantic comedy": "romance",
}

def preprocess_text(*texts: List[str]) -> str:
    """Об'єднує та очищує текстові поля."""
    combined = ' '.join([t for t in texts if t])
    text = combined.lower()
    text = re.sub(r'http\S+|www.\S+', '', text)  # Видалення URL
    text = re.sub(r'[^a-zA-Zа-яА-Я0-9\s]', ' ', text)  # Спецсимволи
    text = re.sub(r'\s+', ' ', text).strip()  # Зайві пробіли
    return text

def detect_genres(event: Dict, main_categories: List[str]) -> List[Tuple[str, float]]:
    """Визначає жанри на основі тексту та категорій."""
    text = preprocess_text(
        event.get("name", ""),
        event.get("description", ""),
        event.get("venue", {}).get("name", ""),
        event.get("publisher", ""),
        ' '.join(event.get("venue", {}).get("subtypes") or [])
    )

    genres = []
    for category in main_categories:
        for genre in GENRES.get(category, []):
            if genre in text and genre not in genres:
                genres.append(genre)

    # Додаємо жанри з імпліцитних підказок
    for hint, genre in IMPLICIT_GENRE_HINTS.items():
        if hint in text and genre not in genres:
            genres.append(genre)

    return genres

def categorize_event(event: Dict) -> List[Tuple[str, float]]:
    """Категоризує подію на основі ключових слів та повертає список (категорія, score)."""
    text = preprocess_text(
        event.get("name", ""),
        event.get("description", ""),
        event.get("venue", {}).get("name", ""),
        event.get("publisher", ""),
        ' '.join(event.get("venue", {}).get("subtypes") or [])
    )

    category_scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0.0
        for keyword, weight in keywords.items():
            if re.search(rf"\b{re.escape(keyword)}\b", text):
                score += weight
        if score > 0:
            category_scores[category] = round(score, 3)

    sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_categories

def assign_categories_to_events(events: List[Dict]) -> List[Dict]:
    enriched_events = []

    for event in events:
        categories = categorize_event(event)
        categories_dicts = [{"category": cat, "score": score} for cat, score in categories]
        event["categories_scored"] = categories_dicts

        main_categories = [c["category"] for c in categories_dicts if c["score"] >= 0.7]
        event["main_categories"] = main_categories

        event["genres"] = detect_genres(event, main_categories)
        enriched_events.append(event)

    return enriched_events


def summarize_event(event: Dict) -> str:
    return f"{event.get('name', 'No Name')} — Categories: {', '.join(event.get('main_categories', []))}, Genres: {', '.join(event.get('genres', []))}"

if __name__ == "__main__":
    # Для тестування — завантаження з файлу
    with open("mockEvents.json", "r", encoding="utf-8") as f:
        api_response = json.load(f)

    enriched = assign_categories_to_events(api_response.get("data", []))

    # Зберігаємо результат у файл
    with open("categorized_events.json", "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print("Категорії призначено кожному івенту.")