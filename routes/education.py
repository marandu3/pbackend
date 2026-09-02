from model.education import Education, EducationOut
from database.config import education_collection
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from routes.user import get_current_user
from core.object_id import parse_object_id, serialize_doc

router = APIRouter()

@router.post(
    "/education/",
    response_model=EducationOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_education(education: Education):
    result = education_collection.insert_one(education.model_dump())
    return EducationOut(id=str(result.inserted_id), **education.model_dump())

@router.get("/education/", response_model=List[EducationOut])
def get_educations():
    return [serialize_doc(edu) for edu in education_collection.find({})]

@router.put(
    "/education/{education_id}",
    response_model=EducationOut,
    dependencies=[Depends(get_current_user)],
)
def update_education(education_id: str, education: Education):
    oid = parse_object_id(education_id)
    result = education_collection.update_one({"_id": oid}, {"$set": education.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education entry not found.")
    return EducationOut(id=education_id, **education.model_dump())

@router.delete("/education/{education_id}", dependencies=[Depends(get_current_user)])
def delete_education(education_id: str):
    oid = parse_object_id(education_id)
    result = education_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education entry not found.")
    return {"detail": "Education entry deleted successfully."}
