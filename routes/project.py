from fastapi import APIRouter, HTTPException, Depends, status
from model.project import projectModel as Project, ProjectOut
from database.config import project_collection
from routes.user import get_current_user
from core.object_id import parse_object_id, serialize_doc
from typing import List

router = APIRouter()

@router.post(
    "/projects/",
    response_model=ProjectOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_project(project: Project):
    result = project_collection.insert_one(project.model_dump())
    return ProjectOut(id=str(result.inserted_id), **project.model_dump())

@router.get("/projects/", response_model=List[ProjectOut])
def get_projects():
    return [serialize_doc(proj) for proj in project_collection.find({})]

@router.put("/projects/{project_id}", response_model=ProjectOut, dependencies=[Depends(get_current_user)])
def update_project(project_id: str, project: Project):
    oid = parse_object_id(project_id)
    result = project_collection.update_one({"_id": oid}, {"$set": project.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project entry not found.")
    return ProjectOut(id=project_id, **project.model_dump())

@router.delete("/projects/{project_id}", dependencies=[Depends(get_current_user)])
def delete_project(project_id: str):
    oid = parse_object_id(project_id)
    result = project_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project entry not found.")
    return {"detail": "Project entry deleted successfully."}
