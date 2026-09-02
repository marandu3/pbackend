from model.profile import profileBase, ProfileCreate
from fastapi import APIRouter, status, Depends
from typing import List
from routes.user import get_current_user
from database.config import profile_collection

router = APIRouter()

# The portfolio has exactly one profile document, always addressed by this
# fixed id. Saving is an upsert, never a delete-then-insert, so a failed or
# concurrent write can never leave the collection empty.
PROFILE_ID = "main"


def migrate_legacy_profile() -> None:
    """One-time migration for profiles saved before the fixed-id scheme.

    The old create_or_update_profile handler inserted a document with a
    random Mongo-generated _id. If one of those still exists and no "main"
    document has been created yet, carry its data forward under the new
    fixed id instead of silently losing it. Safe to call on every startup:
    it is a no-op once the migration has happened once.
    """
    if profile_collection.find_one({"_id": PROFILE_ID}):
        return

    legacy = profile_collection.find_one({"_id": {"$ne": PROFILE_ID}})
    if not legacy:
        return

    legacy.pop("_id")
    profile_collection.insert_one({"_id": PROFILE_ID, **legacy})
    profile_collection.delete_many({"_id": {"$ne": PROFILE_ID}})


@router.post(
    "/profile",
    response_model=profileBase,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
    summary="Create or update the site profile",
)
def create_or_update_profile(profile: ProfileCreate):
    profile_dict = profile.model_dump()
    profile_collection.update_one(
        {"_id": PROFILE_ID},
        {"$set": profile_dict},
        upsert=True,
    )
    return profile_dict


@router.get("/profile", response_model=List[profileBase], summary="Get the site profile")
def read_profiles():
    profiles = profile_collection.find({}, {"_id": 0})
    return list(profiles)
