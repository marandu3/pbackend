from fastapi import APIRouter, HTTPException
from model.project import projectModel as Project
from database.config import project_collection
from typing import List

router = APIRouter()

@router.post("/projects/", response_model=Project)
def create_project(project: Project):
    project_dict = project.model_dump()
    result = project_collection.insert_one(project_dict)
    if result.inserted_id:
        return project
    else:
        raise HTTPException(status_code=500, detail="Project entry could not be created.")
    
@router.get("/projects/", response_model=List[Project])
def get_projects():
    projects = list(project_collection.find({}, {"_id": 0}))
    return [Project(**proj) for proj in projects]

@router.put("/projects/{name}", response_model=Project)
def update_project(name: str, project: Project):
    result = project_collection.update_one(
        {"name": name},
        {"$set": project.model_dump()}
    )
    if result.modified_count == 1:
        return project
    else:
        raise HTTPException(status_code=404, detail="Project entry not found or no changes made.")
    
@router.delete("/projects/{name}")
def delete_project(name: str):
    result = project_collection.delete_one({"name": name})
    if result.deleted_count == 1:
        return {"detail": "Project entry deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Project entry not found.")