from fastapi import APIRouter, HTTPException, Depends, status
from model.timeline import timeline, TimelineOut
from database.config import timeline_collection
from typing import List
from routes.user import get_current_user
from core.object_id import parse_object_id, serialize_doc

router = APIRouter()

@router.post(
    "/timeline/",
    response_model=TimelineOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_timeline_event(event: timeline):
    result = timeline_collection.insert_one(event.model_dump())
    return TimelineOut(id=str(result.inserted_id), **event.model_dump())

@router.get("/timeline/", response_model=List[TimelineOut])
def get_timeline_events():
    return [serialize_doc(evt) for evt in timeline_collection.find({})]

@router.put("/timeline/{event_id}", response_model=TimelineOut, dependencies=[Depends(get_current_user)])
def update_timeline_event(event_id: str, event: timeline):
    oid = parse_object_id(event_id)
    result = timeline_collection.update_one({"_id": oid}, {"$set": event.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timeline event not found.")
    return TimelineOut(id=event_id, **event.model_dump())

@router.delete("/timeline/{event_id}", dependencies=[Depends(get_current_user)])
def delete_timeline_event(event_id: str):
    oid = parse_object_id(event_id)
    result = timeline_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timeline event not found.")
    return {"detail": "Timeline event deleted successfully."}
