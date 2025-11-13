from pydantic import BaseModel, Field
from typing import Optional

class Education(BaseModel):
    level: str = Field(..., description="Level of education, e.g., Bachelor's, Master's")
    institution: str = Field(..., description="Name of the educational institution")
    field_of_study: str = Field(..., description="Field of study or major")
    location: str = Field(..., description="Location of the institution")
    start_year: int = Field(..., description="Year when the education started")
    end_year: Optional[int] = Field(None, description="Year when the education ended, if applicable")
