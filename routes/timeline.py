from fastapi import APIRouter, HTTPException
from model.timeline import timeline
from database.config import timeline_collection
from typing import List

router = APIRouter()


@router.post("/timeline/", response_model=timeline)
def create_timeline_event(event: timeline):
    event_dict = event.model_dump()
    result = timeline_collection.insert_one(event_dict)
    if result.inserted_id:
        return event
    else:
        raise HTTPException(status_code=500, detail="Timeline event could not be created.")
    
@router.get("/timeline/", response_model=List[timeline])
def get_timeline_events():
    events = list(timeline_collection.find({}, {"_id": 0}))
    return [timeline(**evt) for evt in events]

@router.put("/timeline/{title}", response_model=timeline)
def update_timeline_event(title: str, event: timeline):
    result = timeline_collection.update_one(
        {"title": title},
        {"$set": event.model_dump()}
    )
    if result.modified_count == 1:
        return event
    else:
        raise HTTPException(status_code=404, detail="Timeline event not found or no changes made.")
    
@router.delete("/timeline/{title}")
def delete_timeline_event(title: str):
    result = timeline_collection.delete_one({"title": title})
    if result.deleted_count == 1:
        return {"detail": "Timeline event deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Timeline event not found.")