from pydantic import BaseModel, Field
from typing import Optional

class timeline(BaseModel):
    title: str = Field(..., description="Title of the timeline event")
    description: Optional[str] = Field(None, description="Detailed description of the event")
    start_date: str = Field(..., description="Start date of the event in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, description="End date of the event in YYYY-MM-DD format, if applicable")
    location: Optional[str] = Field(None, description="Location where the event took place")