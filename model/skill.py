from pydantic import BaseModel, Field
from typing import Optional

class skill(BaseModel):
    name: str = Field(..., description="Name of the skill, e.g., Python, Project Management")
    icon_url: Optional[str] = Field(None, description="URL to an icon representing the skill")
    description: Optional[str] = Field(None, description="Brief description of the skill")
    category: Optional[str] = Field(None, description="Category of the skill, e.g., Programming, Management")