from fastapi import APIRouter, HTTPException,Depends
from database.config import (project_collection)
from model.projects import Project

router = APIRouter()


@router.post('/postproject', response_model=Project)
async def post_project(project: Project):
    if project_collection.find_one({"projet_name": project.project_name}):
        raise HTTPException(
            status_code=400,
            detail="project name already exist"
        )
    projecttostore=project.model_dump()
    project_collection.insert_one(projecttostore)
    return Project(**projecttostore)

@router.get('/projects')
async def get_projects():
    projects = project_collection.find({},{'_id': 0})
    project_list = [Project(**project) for project in projects]
    if not project_list:
        raise HTTPException(
            status = 404,
            details= "no project found"
        )
    return project_list

