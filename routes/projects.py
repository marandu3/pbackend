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

@router.delete('/projects/{projectname}', response_model=list[Project])
async def delete_project(projectname: str):
    project = project_collection.find_one({"project_name": projectname})
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    
    project_collection.delete_one({"project_name": projectname})
    
    projects = project_collection.find({}, {"_id": 0})
    return [Project(**p) for p in projects]   # all remaining


@router.put('/projects/{project_name}', response_model=list[Project])
async def update_project(project_name: str, project: Project):
    # Check if project exists
    if not project_collection.find_one({'project_name': project_name}):
        raise HTTPException(
            status_code=404,
            detail="project not found"
        )
    
    # Update project
    updated_project = project_collection.find_one_and_update(
        {'project_name': project_name},   # filter
        {'$set': project.model_dump()},        # new data
        return_document=True
    )
    
    # Get all remaining projects
    projects = project_collection.find({}, {'_id': 0})
    project_list = [Project(**p) for p in projects]

    return project_list