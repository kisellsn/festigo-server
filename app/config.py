import os

import joblib
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
SECRET_KEY = os.getenv("SECRET_KEY")
API_KEY_NAME = os.getenv("API_KEY_NAME")
ALGORITHM = os.getenv("ALGORITHM")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Повні шляхи до моделей
genre_model_path = os.path.join(BASE_DIR, "../categorization/models/genre_model.joblib")
genre_mlb_path = os.path.join(BASE_DIR, "../categorization/models/genre_mlb.joblib")
category_model_path = os.path.join(BASE_DIR, "../categorization/models/category_model_multi.joblib")
category_mlb_path = os.path.join(BASE_DIR, "../categorization/models/category_mlb.joblib")

# Завантаження моделей
genre_model = joblib.load(os.path.abspath(genre_model_path))
genre_mlb = joblib.load(os.path.abspath(genre_mlb_path))
category_model = joblib.load(os.path.abspath(category_model_path))
category_mlb = joblib.load(os.path.abspath(category_mlb_path))


# Категорії
CATEGORY_KEYWORDS = {
    "music": {
        "concert": 2.0, "music": 0.9, "live": 0.8, "band": 0.8, "dj": 0.9, "orchestra": 0.9, "gig": 0.7,
        "rock": 0.7, "pop": 0.7, "electronic": 0.7, "jazz": 0.7, "rap": 0.7, "hip hop": 0.7, "folk": 0.7,
        "spotify":0.9, "pub": 0.5, "ticketsbox": 0.6, "lvivconcert": 0.6, "onlinetickets": 0.6,
        "kontramarka": 0.6, "bar": 0.5, "ra": 0.5
    },
    "show": {
        "theatre": 2.0, "drama": 0.9, "performance": 1.0, "actor": 0.8, "play": 0.8, "comedy": 0.7,
        "tragicomedy": 0.7, "improv": 0.7, "stand-up": 0.7, "ballet": 0.7, "humor": 0.7, "circus": 0.7,
        "pub": 0.5, "fashion": 0.6
    },
    "festival": {
        "festival": 2.0, "fair": 0.8, "parade": 0.8, "street": 0.6, "celebration": 0.7, "fest": 2.0
    },
    "exhibition": {
        "exhibition": 2.0, "gallery": 0.9, "museum": 0.9, "art": 0.8, "vernissage": 0.8, "fashion": 0.3
    },
    "cinema": {
        "cinema": 1.0, "movie": 0.9, "film": 0.9, "screening": 0.8, "premiere": 0.7
    },
    "education": {
        "lecture": 2.0, "workshop": 1.0, "course": 1.0, "training": 0.9, "seminar": 1.0, "conference": 1.0,
        "webinar": 1.0, "master class": 2.0, "school": 0.9, "excursions": 0.5, "test": 0.6
    },
    "sport": {
        "match": 2.0, "game": 0.9, "tournament": 0.8, "sports": 2.0, "football": 2.0, "basketball": 2.0,
        "marathon": 0.9, "yoga": 0.9, "run": 0.8, "fitness": 0.9, "activity": 0.9, "vs": 0.8, "stadium": 0.9
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

city_translation_map = {
    "Kyiv": "Київ",
    "Kharkiv": "Харків",
    "Odesa": "Одеса",
    "Dnipro": "Дніпро",
    "Donetsk": "Донецьк",
    "Zaporizhzhia": "Запоріжжя",
    "Lviv": "Львів",
    "Kryvyi Rih": "Кривий Ріг",
    "Mykolaiv": "Миколаїв",
    "Mariupol": "Маріуполь",
    "Luhansk": "Луганськ",
    "Vinnytsia": "Вінниця",
    "Makiivka": "Макіївка",
    "Simferopol": "Сімферополь",
    "Kherson": "Херсон",
    "Poltava": "Полтава",
    "Chernihiv": "Чернігів",
    "Cherkasy": "Черкаси",
    "Khmelnytskyi": "Хмельницький",
    "Chernivtsi": "Чернівці",
    "Zhytomyr": "Житомир",
    "Sumy": "Суми",
    "Rivne": "Рівне",
    "Horlivka": "Горлівка",
    "Ivano-Frankivsk": "Івано-Франківськ",
    "Ternopil": "Тернопіль",
    "Lutsk": "Луцьк",
    "Bila Tserkva": "Біла Церква",
    "Kramatorsk": "Краматорськ",
    "Kremenchuk": "Кременчук",
    "Melitopol": "Мелітополь",
    "Kerch": "Керч",
    "Severodonetsk": "Сєвєродонецьк",
    "Sloviansk": "Слов’янськ",
    "Uzhhorod": "Ужгород",
    "Berdiansk": "Бердянськ",
    "Nikopol": "Нікополь",
    "Pavlohrad": "Павлоград",
    "Kamianets-Podilskyi": "Кам’янець-Подільський",
    "Oleksandriia": "Олександрія",
    "Konotop": "Конотоп",
    "Brovary": "Бровари",
    "Fastiv": "Фастів",
    "Stryi": "Стрий",
    "Drohobych": "Дрогобич",
    "Mukachevo": "Мукачево",
    "Chervonohrad": "Червоноград",
    "Nizhyn": "Ніжин",
    "Yevpatoria": "Євпаторія",
    "Boyarka": "Боярка",
    "Izmail": "Ізмаїл",
    "Kamianets": "Кам’янець",
    "Boryspil": "Бориспіль",
    "Irpin": "Ірпінь",
    "Pereiaslav": "Переяслав",
    "Obukhiv": "Обухів",
    "Lubny": "Лубни",
    "Shostka": "Шостка",
    "Kolomyia": "Коломия",
    "Nova Kakhovka": "Нова Каховка",
    "Lozova": "Лозова",
    "Smila": "Сміла",
    "Kostiantynivka": "Костянтинівка",
    "Antratsyt": "Антрацит",
    "Sievierodonetsk": "Сєвєродонецьк",
    "Enerhodar": "Енергодар",
    "Yuzhnoukrainsk": "Южноукраїнськ",
    "Slavutych": "Славутич",
    "Pokrovsk": "Покровськ",
    "Chuhuiv": "Чугуїв",
    "Yalta": "Ялта",
    "Alchevsk": "Алчевськ",
    "Toretsk": "Торецьк",
    "Novovolynsk": "Нововолинськ",
    "Netishyn": "Нетішин",
    "Dzhankoi": "Джанкой",
    "Volodymyr": "Володимир",
    "Reni": "Рені",
    "Saky": "Саки",
    "Illichivsk": "Іллічівськ",
    "Artemivsk": "Артемівськ",
    "Kovel": "Ковель",
    "Zhmerynka": "Жмеринка",
    "Zolochiv": "Золочів",
    "Pervomaisk": "Первомайськ",
    "Lubny": "Лубни",
    "Truskavets": "Трускавець"
}
