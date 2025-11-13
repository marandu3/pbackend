from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class profileBase(BaseModel):
    name:str = Field(..., example="John Doe")
    title:str = Field(..., example="Software Engineer")
    description:Optional[str] = Field(None, example="Experienced software engineer with a passion for developing innovative programs.")
    social_links:Optional[dict] = Field(None, example={"linkedin": "https://linkedin.com/in/johndoe", "github": "https://github.com/johndoe"})  
    profile_image_url:Optional[str] = Field(None, example="https://example.com/images/johndoe.jpg")

class ProfileCreate(profileBase):
    pass