import re
from typing import Dict, List, Tuple
import json

from app.config import GENRES, IMPLICIT_GENRE_HINTS, CATEGORY_KEYWORDS


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
    with open("../test_data/mockEvents.json", "r", encoding="utf-8") as f:
        api_response = json.load(f)

    enriched = assign_categories_to_events(api_response.get("data", []))

    # Зберігаємо результат у файл
    with open("../test_data/categorized_events.json", "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print("Категорії призначено кожному івенту.")