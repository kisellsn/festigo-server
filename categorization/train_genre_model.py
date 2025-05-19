import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.preprocessing import MultiLabelBinarizer
from app.config import GENRES, IMPLICIT_GENRE_HINTS

# Формуємо навчальний набір
train_texts = []
train_labels = []

# Прямі жанри
for category, genre_list in GENRES.items():
    for genre in genre_list:
        train_texts.append(f"{genre} event with {genre} music")
        train_labels.append([genre])

# Імпліцитні підказки
for hint, genre in IMPLICIT_GENRE_HINTS.items():
    train_texts.append(f"This is about {hint}")
    train_labels.append([genre])

# Бінаризація
mlb_genres = MultiLabelBinarizer()
Y = mlb_genres.fit_transform(train_labels)

# Модель
genre_model = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
    ('clf', OneVsRestClassifier(LinearSVC()))
])

genre_model.fit(train_texts, Y)

# Збереження
joblib.dump(genre_model, 'models/genre_model.joblib')
joblib.dump(mlb_genres, 'models/genre_mlb.joblib')
