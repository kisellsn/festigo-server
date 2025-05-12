from pydantic import BaseModel
from typing import Optional, List, Tuple, Dict
from datetime import datetime

class CategoryScore(BaseModel):
    category: str
    score: float

class Venue(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    subtypes: List[str] = []

class Event(BaseModel):
    id: str
    name: str
    description: Optional[str]
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
    country: str
    price: Optional[str] = "-"
    component_vectors: Optional[Dict[str, List[float]]] = None



