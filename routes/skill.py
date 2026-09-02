from fastapi import APIRouter, HTTPException, Depends, status
from model.skill import skill, SkillOut
from routes.user import get_current_user
from database.config import skills_collection
from core.object_id import parse_object_id, serialize_doc
from typing import List

router = APIRouter()

@router.post(
    "/skills/",
    response_model=SkillOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_skill(skill_in: skill):
    result = skills_collection.insert_one(skill_in.model_dump())
    return SkillOut(id=str(result.inserted_id), **skill_in.model_dump())

@router.get("/skills/", response_model=List[SkillOut])
def get_skills():
    return [serialize_doc(sk) for sk in skills_collection.find({})]

@router.put("/skills/{skill_id}", response_model=SkillOut, dependencies=[Depends(get_current_user)])
def update_skill(skill_id: str, skill_in: skill):
    oid = parse_object_id(skill_id)
    result = skills_collection.update_one({"_id": oid}, {"$set": skill_in.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill entry not found.")
    return SkillOut(id=skill_id, **skill_in.model_dump())

@router.delete("/skills/{skill_id}", dependencies=[Depends(get_current_user)])
def delete_skill(skill_id: str):
    oid = parse_object_id(skill_id)
    result = skills_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill entry not found.")
    return {"detail": "Skill entry deleted successfully."}
