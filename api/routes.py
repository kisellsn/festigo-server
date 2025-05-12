from fastapi import APIRouter, Depends
from app.dependencies import verify_token
from recommendation.user_profile import build_profile_vector, update_profile_vector
from services.fetcher import fetch_and_store_events
from services.firestore_client import delete_expired_events
from recommendation.recommendation_engine import get_recommendations

router = APIRouter()

# -------------------------- EVENTS UPDATES
@router.post("/sync", dependencies=[Depends(verify_token)])
def manual_sync():
    fetch_and_store_events()
    return {"status": "Manual sync complete"}

@router.post("/cleanup", dependencies=[Depends(verify_token)])
def manual_cleanup():
    delete_expired_events()
    return {"status": "Expired events deleted"}

# -------------------------- USER UPDATES
@router.post("/user/{user_id}/init_profile", dependencies=[Depends(verify_token)])
def init_user_profile(user_id: str):
    build_profile_vector(user_id)
    return {"status": "User profile initialized"}

@router.post("/user/{user_id}/update_profile", dependencies=[Depends(verify_token)])
def update_user_profile(user_id: str):
    update_profile_vector(user_id)
    return {"status": "Profile updated"}

@router.get("/get_recommendations", dependencies=[Depends(verify_token)])
def get_user_recommendations(user_id: str):
    recommendations = get_recommendations(user_id)
    return {"recommendations": recommendations}



# @router.get("/create_profile", dependencies=[Depends(verify_token)])
# def create_user_profile(user_id: str):
#     build_profile_vector(user_id)
#     return {"status": profile created}
#
# @router.get("/update_profile", dependencies=[Depends(verify_token)])
# def update_user_profile(user_id: str):
#     recommendations = get_recommendations(user_id)
#     return {"recommendations": recommendations}
