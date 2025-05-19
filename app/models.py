from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class CategoryScore(BaseModel):
    category: str
    score: float

class Venue(BaseModel):
    name: str
    name_uk: Optional[str] = None
    address: str
    address_uk: Optional[str] = None
    latitude: float
    longitude: float
    subtypes: List[str] = []

class Event(BaseModel):
    id: str
    name: str
    name_uk: Optional[str] = None

    description: Optional[str]
    description_uk: Optional[str] = None

    link: Optional[str]
    imageUrl: Optional[str]
    startTime: datetime
    endTime: Optional[datetime]
    isVirtual: bool
    venue: Optional[Venue]
    categories_scored: List[CategoryScore]
    genres: List[str]
    main_categories: List[str]

    city: str
    city_uk: Optional[str] = None

    country: str
    country_uk: Optional[str] = None

    price: Optional[str] = "-"
    component_vectors: Optional[Dict[str, List[float]]] = None

class FirebaseLoginRequest(BaseModel):
    user_id: str



