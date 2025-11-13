from fastapi import APIRouter, HTTPException
from model.skill import skill
from database.config import skills_collection
from typing import List

router = APIRouter()

@router.post("/skills/", response_model=skill)
def create_skill(skill: skill):
    skill_dict = skill.model_dump()
    result = skills_collection.insert_one(skill_dict)
    if result.inserted_id:
        return skill
    else:
        raise HTTPException(status_code=500, detail="Skill entry could not be created.")
    
@router.get("/skills/", response_model=List[skill])
def get_skills():
    skills = list(skills_collection.find({}, {"_id": 0}))
    return [skill(**sk) for sk in skills]

@router.put("/skills/{name}", response_model=skill)
def update_skill(name: str, skill: skill):
    result = skills_collection.update_one(
        {"name": name},
        {"$set": skill.model_dump()}
    )
    if result.modified_count == 1:
        return skill
    else:
        raise HTTPException(status_code=404, detail="Skill entry not found or no changes made.")
    
@router.delete("/skills/{name}")
def delete_skill(name: str):
    result = skills_collection.delete_one({"name": name})
    if result.deleted_count == 1:
        return {"detail": "Skill entry deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Skill entry not found.")