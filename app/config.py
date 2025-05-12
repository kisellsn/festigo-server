import os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent
FIREBASE_CREDENTIALS= os.getenv("FIREBASE_CREDENTIALS_PATH")

if FIREBASE_CREDENTIALS and not FIREBASE_CREDENTIALS.startswith("/"):
    FIREBASE_CREDENTIALS_PATH = str(BASE_DIR / FIREBASE_CREDENTIALS)
else:
    FIREBASE_CREDENTIALS_PATH = FIREBASE_CREDENTIALS

EVENTS_API_URL = os.getenv("RAPID_API_URL")
SCHEDULE_INTERVAL_HOURS = int(os.getenv("SCHEDULE_INTERVAL_HOURS", 6))
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
SCHEDULE_DELETE_INTERVAL_HOURS = int(os.getenv("SCHEDULE_DELETE_INTERVAL_HOURS", 24))
API_KEY=os.getenv("API_KEY")
API_KEY_NAME=os.getenv("API_KEY_NAME")



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
ALL_CATEGORIES = [cat for cat in CATEGORY_KEYWORDS.keys()] + ['other']

GENRES = {
    "music": ["rock", "pop", "jazz", "electronic", "classical", "folk", "rap", "hip hop", "metal", "indie", "punk", "techno"],
    "show": ["comedy", "drama", "tragicomedy", "ballet", "musical", "stand-up", "opera", "monodrama"],
    "cinema": ["thriller", "horror", "drama", "action", "sci-fi", "documentary", "romance", "animation"]
}
ALL_GENRES = list({genre for genres in GENRES.values() for genre in genres}) + ['other']


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


CATEGORY_TRANSLATION = {
    "Концерти": "music",
    "Вистави": "show",
    "Виставки": "exhibition",
    "Фестивалі": "festival",
    "Лекції та воркшопи": "education",
    "Спортивні події": "sport",
    "Інше": "other"
}

GENRE_TRANSLATION = {
    # Music genres
    "Рок": "rock",
    "Джаз": "jazz",
    "Класика": "classical",
    "Поп": "pop",
    "Електроніка": "electronic",
    "Інше": "other",

    # Theater / cinema genres
    "Драма": "drama",
    "Комедія": "comedy",
    "Мюзикл": "musical",
    "Фантастика": "sci-fi",
    "Документальне кіно": "documentary"
}

