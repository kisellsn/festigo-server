import re
from typing import Dict, List, Tuple
import json
import joblib

from app.config import CATEGORY_KEYWORDS

# Завантаження моделі
genre_model = joblib.load('categorization/models/genre_model.joblib')
genre_mlb = joblib.load('categorization/models/genre_mlb.joblib')
category_model = joblib.load('categorization/models/category_model_multi.joblib')
category_mlb = joblib.load('categorization/models/category_mlb.joblib')


def preprocess_text(*texts: List[str]) -> str:
    """Об'єднує та очищує текстові поля."""
    combined = ' '.join([t for t in texts if t])
    text = combined.lower()
    text = re.sub(r'http\S+|www.\S+', '', text)  # Видалення URL
    text = re.sub(r'[^a-zA-Zа-яА-Я0-9\s]', ' ', text)  # Спецсимволи
    text = re.sub(r'\s+', ' ', text).strip()  # Зайві пробіли
    return text


def detect_genres(event: Dict, main_categories: List[str]) -> List[str]:
    # Працюємо тільки для відповідних категорій
    applicable = {"music", "cinema", "show"}
    if not any(cat in applicable for cat in main_categories):
        return []

    text = preprocess_text(
        event.get("name", ""),
        event.get("description", ""),
        event.get("venue", {}).get("name", ""),
        event.get("publisher", ""),
        ' '.join(event.get("venue", {}).get("subtypes") or [])
    )

    scores = genre_model.decision_function([text])[0]
    genres = genre_mlb.classes_

    detected = [genre for genre, score in zip(genres, scores) if score > 0]

    return sorted(set(detected))


def categorize_event(event: Dict) -> List[Tuple[str, float]]:
    text = preprocess_text(
        event.get("name", ""),
        event.get("description", ""),
        event.get("venue", {}).get("name", ""),
        event.get("publisher", ""),
        ' '.join(event.get("venue", {}).get("subtypes") or [])
    )

    # --- Model scores ---
    model_scores_raw = category_model.decision_function([text])[0]
    model_categories = category_mlb.classes_
    model_scores = {cat: float(score) for cat, score in zip(model_categories, model_scores_raw) if score > 0}

    # --- Keyword scores ---
    keyword_scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0.0
        for keyword, weight in keywords.items():
            if re.search(rf"\b{re.escape(keyword)}\b", text):
                score += weight
        if score > 0:
            keyword_scores[category] = round(score, 3)

    # --- Combined ---
    combined_scores = {}
    for category in set(model_scores) | set(keyword_scores):
        score_model = model_scores.get(category, 0)
        score_keyword = keyword_scores.get(category, 0)
        combined_scores[category] = round(0.7 * score_model + 0.3 * score_keyword, 3)

    return sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)


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
    with open("../test_data/new_categorized_events.json", "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print("Категорії призначено кожному івенту.")