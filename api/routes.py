from datetime import datetime

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request

from app.config import SECRET_KEY, ALGORITHM
from app.dependencies import verify_token, verify_token_easy
from app.models import FirebaseLoginRequest, EventUpdateRequest
from recommendation.user_profile import build_profile_vector, update_profile_vector, get_similar_to_last_liked
from services.fetcher import fetch_and_store_events
from services.firestore_client import delete_expired_events, set_last_manual_sync_time
from recommendation.recommendation_engine import get_recommendations

router = APIRouter()

# -------------------------- EVENTS UPDATES
@router.post("/sync", dependencies=[Depends(verify_token_easy)])
def manual_sync():
    fetch_and_store_events()
    set_last_manual_sync_time(datetime.now())
    return {"status": "Manual sync complete"}

@router.post("/cleanup", dependencies=[Depends(verify_token_easy)])
def manual_cleanup():
    delete_expired_events()
    return {"status": "Expired events deleted"}

# -------------------------- USER UPDATES
@router.post("/auth/firebase-login")
def firebase_login(data: FirebaseLoginRequest):
    if not data.user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")
    app_token = jwt.encode({"sub": data.user_id}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": app_token}


@router.post("/user/init_profile", dependencies=[Depends(verify_token)])
def init_user_profile(request: Request):
    user_id = request.state.user_id
    build_profile_vector(user_id)
    return {"status": "User profile initialized"}

@router.post("/user/update_profile", dependencies=[Depends(verify_token)])
def update_user_profile(request: Request, body: EventUpdateRequest):
    user_id = request.state.user_id
    update_profile_vector(user_id, body.event_id)
    return {"status": "Profile updated"}

@router.get("/user/get_recommendations", dependencies=[Depends(verify_token)])
def get_user_recommendations(request: Request):
    user_id = request.state.user_id
    recommendations = get_recommendations(user_id)
    return {"recommendations": recommendations}

@router.get("/user/get_similar_events", dependencies=[Depends(verify_token)])
def get_similar_events(request: Request):
    user_id = request.state.user_id
    similar, last_fav_id = get_similar_to_last_liked(user_id)
    return {"similar": similar,
            "lastLikedEventId": last_fav_id}


