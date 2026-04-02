from typing import List, Literal
from pydantic import BaseModel, Field
from .base import TechnicalSkills


class CVProfile(BaseModel):
    technical_skills: TechnicalSkills
    soft_skills: List[str] = Field(
        default_factory=list,
        description="Interpersonal and professional qualities (e.g., Leadership, Agile, Communication).",
    )
    experience_level: Literal["Entry", "Mid", "Senior", "Lead", "Not Specified"] = (
        Field(
            default="Not Specified",
            description="The seniority level mentioned or inferred from the content.",
        )
    )
    responsibilities: List[str] = Field(
        default_factory=list,
        description="Detailed bullet points describing work history, duties, and achievements.",
    )
