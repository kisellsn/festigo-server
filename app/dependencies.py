from fastapi import Header, HTTPException, Depends
from app.config import API_KEY
from services.firestore_client import db


def verify_token(authorization: str = Header(...)):
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=403, detail="Unauthorized")

def get_firestore_db():
    return db
