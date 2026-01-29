from model.profile import profileBase, ProfileCreate
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from routes.user import get_current_user
from database.config import profile_collection


router = APIRouter()

# 🟢 Create
@router.post("/profile", response_model=profileBase, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
def create_or_update_profile(profile: ProfileCreate):
    profile = profile.model_dump()
    profile_collection.delete_many({})  # Ensure only one profile exists
    result = profile_collection.insert_one(profile)
    new_profile = profile_collection.find_one({"_id": result.inserted_id})
    new_profile["id"] = str(new_profile["_id"])
    new_profile.pop("_id", None)
    return new_profile

# 🔵 Read
@router.get("/profile", response_model=List[profileBase])
def read_profiles():
    profiles = profile_collection.find({}, {"_id": 0})
    return list(profiles)
