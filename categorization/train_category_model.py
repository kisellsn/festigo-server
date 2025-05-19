import json
import random
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from app.config import CATEGORY_KEYWORDS


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

# -------- Навчання моделі --------

def train_and_save_model():
    data = generate_training_data()
    texts = [text for text, labels in data]
    labels = [labels for text, labels in data]

    mlb = MultiLabelBinarizer()
    Y = mlb.fit_transform(labels)

    # TF-IDF + One-vs-Rest SVM
    model = make_pipeline(
        TfidfVectorizer(ngram_range=(1,2), max_features=5000),
        OneVsRestClassifier(LinearSVC())
    )

    # Навчання
    X_train, X_test, y_train, y_test = train_test_split(texts, Y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)

    # Оцінка
    accuracy = model.score(X_test, y_test)
    print(f"Model accuracy: {accuracy:.3f}")

    joblib.dump(model, "models/category_model_multi.joblib")
    joblib.dump(mlb, "models/category_mlb.joblib")
    print("✅ Модель і MultiLabelBinarizer збережені.")

if __name__ == "__main__":
    train_and_save_model()
    # save_generated_data()