from pydantic import BaseModel, Field
from typing import Optional

class projectModel(BaseModel):
    title: str = Field(..., description="Title of the project")
    description: Optional[str] = Field(None, description="Detailed description of the project")
    picture_url: Optional[str] = Field(None, description="URL to an image representing the project")
    github_url: Optional[str] = Field(None, description="URL to the project's GitHub repository")
    live_url: Optional[str] = Field(None, description="URL to the live version of the project")
    start_date: Optional[str] = Field(None, description="Start date of the project in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, description="End date of the project in YYYY-MM-DD format, if applicable")
    technologies: Optional[list[str]] = Field(None, description="List of technologies used in the project")
    featured: bool = Field(False, description="Whether this project is highlighted on the homepage")
    order: int = Field(0, description="Lower numbers are shown first among featured projects")

class ProjectOut(projectModel):
    id: str = Field(..., description="Database id of this record")
    slug: str = Field(..., description="Stable URL slug, set at creation and unaffected by later title edits")
