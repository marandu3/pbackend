from pydantic import BaseModel


class Project(BaseModel):
    project_name: str
    project_description: str
    project_progression: int
    project_image: str