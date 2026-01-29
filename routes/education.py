from model.education import Education
from database.config import education_collection
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from routes.user import get_current_user

router = APIRouter()

@router.post("/education/", response_model=Education, dependencies=[Depends(get_current_user)])
def create_education(education: Education):
    education_dict = education.model_dump()
    result = education_collection.insert_one(education_dict)
    if result.inserted_id:
        return education
    else:
        raise HTTPException(status_code=500, detail="Education entry could not be created.")
    
@router.get("/education/", response_model=List[Education])
def get_educations():
    educations = list(education_collection.find({}, {"_id": 0}))
    return [Education(**edu) for edu in educations]

#updating education entry by level
@router.put("/education/{level}", response_model=Education, dependencies=[Depends(get_current_user)])
def update_education(level: str, education: Education):
    result = education_collection.update_one(
        {"level": level},
        {"$set": education.model_dump()}
    )
    if result.modified_count == 1:
        return education
    else:
        raise HTTPException(status_code=404, detail="Education entry not found or no changes made.")

@router.delete("/education/{level}", dependencies=[Depends(get_current_user)])
def delete_education(level: str):
    result = education_collection.delete_one({"level": level})
    if result.deleted_count == 1:
        return {"detail": "Education entry deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Education entry not found.")