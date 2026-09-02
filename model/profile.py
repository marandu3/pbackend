from pydantic import BaseModel, Field
from typing import Optional


class profileBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "John Doe"})
    title: str = Field(..., json_schema_extra={"example": "Software Engineer"})
    description: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Experienced software engineer with a passion for developing innovative programs."},
    )
    social_links: Optional[dict] = Field(
        None,
        json_schema_extra={"example": {"linkedin": "https://linkedin.com/in/johndoe", "github": "https://github.com/johndoe"}},
    )
    profile_image_url: Optional[str] = Field(
        None, json_schema_extra={"example": "https://example.com/images/johndoe.jpg"}
    )

class ProfileCreate(profileBase):
    pass
