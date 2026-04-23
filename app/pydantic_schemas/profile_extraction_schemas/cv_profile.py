from typing import List, Literal
from pydantic import BaseModel, Field
from .profile_base import TechnicalSkills


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
    education: List[str] = Field(
        default_factory=list,
        description="Educational background details, including degrees, institutions, and graduation years.",
    )
    internships: List[str] = Field(
        default_factory=list,
        description="Internship experiences, if any, with necessary details.",
    )
    projects: List[str] = Field(
        default_factory=list,
        description="Notable projects, including personal, academic, or open-source contributions.",
    )
