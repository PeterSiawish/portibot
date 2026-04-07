from typing import List
from pydantic import BaseModel, Field
from .profile_base import TechnicalSkills


class JobProfile(BaseModel):
    technical_skills: TechnicalSkills
    soft_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
