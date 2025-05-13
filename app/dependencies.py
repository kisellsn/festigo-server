from app.config import SECRET_KEY, ALGORITHM
from services.firestore_client import db
import jwt
from fastapi import HTTPException, Security, Depends, Request, Header
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/firebase-login")

async def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        request.state.user_id = user_id
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_token_easy(authorization: str = Header(...)):
    if authorization != f"Bearer {SECRET_KEY}":
        raise HTTPException(status_code=403, detail="Unauthorized")

def get_firestore_db():
    return db
