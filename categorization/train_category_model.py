import json
import random
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import make_pipeline
from app.config import CATEGORY_KEYWORDS
from services.firestore_client import db


# Зберігаємо у файл
def save_generated_data(filepath="generated_category_data.json"):
    data = generate_training_data(2000)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump([{"text": text, "labels": labels} for text, labels in data], f, ensure_ascii=False, indent=2)

# -------- Генерація синтетичних даних --------

def generate_training_data(num_samples: int = 2000):
    data = []
    for _ in range(num_samples):
        categories = random.sample(list(CATEGORY_KEYWORDS.keys()), k=random.randint(1, 2))
        text_parts = []

        for cat in categories:
            keywords = list(CATEGORY_KEYWORDS[cat].keys())
            selected_words = random.sample(keywords, k=random.randint(2, 4))
            sentence = f"{' '.join(selected_words)} event with {' and '.join(selected_words)} in the city center"
            text_parts.append(sentence)

        full_text = '. '.join(text_parts)
        data.append((full_text, categories))

    return data

def export_training_data_to_file(filepath="../test_data/real_training_data.json"):
    events_ref = db.collection("events")
    events = list(events_ref.stream())
    data = []

    def get_text(val):
        if isinstance(val, list):
            return " ".join(val)
        elif isinstance(val, bool):
            return "online" if val else "offline"
        elif isinstance(val, dict):
            return " ".join(str(v) for v in val.values() if isinstance(v, str))
        return str(val) if val else ""

    for doc in events:
        event = doc.to_dict()
        text_parts = []

        name = get_text(event.get("name", ""))
        if name:
            text_parts.append(f"Event name: {name}")

        description = get_text(event.get("description", ""))
        if description:
            text_parts.append(f"Description: {description}")

        genres = get_text(event.get("genres", []))
        if genres:
            text_parts.append(f"Genres: {genres}")

        subtypes = get_text(event.get("venue", {}).get("subtypes", []))
        if subtypes:
            text_parts.append(f"Location type: {subtypes}")

        is_virtual = get_text(event.get("isVirtual", False))
        text_parts.append(f"Format: {is_virtual}")

        full_text = ". ".join(text_parts).strip()

        labels = []
        for item in event.get("categories_scored", []):
            if isinstance(item, dict) and item.get("score", 0) >= 0.4:
                labels.append(item["category"])

        if full_text and labels:
            data.append({"text": full_text, "labels": labels})

    with open(filepath, "a", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Exported {len(data)} enriched samples to {filepath}")

# -------- Дані з бд --------

def load_training_data_from_file(filepath="../test_data/real_training_data.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✅ Loaded {len(data)} real samples from {filepath}")
    return [(item["text"], item["labels"]) for item in data]


# -------- Навчання моделі --------

def train_model_with_pretrain_and_finetune():
    # --- синтетичні дані ---
    synthetic_data = generate_training_data(1000)
    print(f"🧪 Generated {len(synthetic_data)} synthetic samples")

    # ---  реальні ---
    real_data = load_training_data_from_file()

    # --- разом ---
    all_data = synthetic_data + real_data
    texts = [text for text, labels in all_data]
    labels = [labels for text, labels in all_data]

    mlb = MultiLabelBinarizer()
    Y = mlb.fit_transform(labels)

    model = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 3), max_features=8000),
        OneVsRestClassifier(LogisticRegression(max_iter=1000))
    )

    # --- навчання ---
    X_synth, y_synth = zip(*synthetic_data)
    X_real, y_real = zip(*real_data)

    y_synth_bin = mlb.transform(y_synth)
    y_real_bin = mlb.transform(y_real)

    model.fit(X_synth, y_synth_bin)
    model.fit(X_real, y_real_bin)

    # --- оцінка  ---
    print("📊 Оцінка моделі...")
    y_pred_bin = model.predict(X_real)
    report = classification_report(y_real_bin, y_pred_bin, target_names=mlb.classes_, zero_division=0)
    print(report)


    # --- збереження ---
    joblib.dump(model, "models/category_model_multi.joblib")
    joblib.dump(mlb, "models/category_mlb.joblib")
    print("✅ Модель збережено.")


if __name__ == "__main__":
    # export_training_data_to_file()
    train_model_with_pretrain_and_finetune()