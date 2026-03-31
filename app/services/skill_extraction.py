from typing import List
from pydantic import BaseModel, Field


# The following classes define the expected structure of the JSON response from the Gemini API.
class Project(BaseModel):
    title: str
    tech_stack: List[str]
    core_features: List[str] = Field(description="5-10 word summary of the system")


class TechSkills(BaseModel):
    languages: List[str]
    frameworks: List[str]
    libraries: List[str]
    databases: List[str]
    tools_platforms: List[str]
    concepts: List[str]


class SoftSkills(BaseModel):
    interpersonal: List[str]
    methodologies: List[str]


class CVData(BaseModel):
    name: str
    technical_skills: TechSkills
    soft_skills: SoftSkills
    projects_brief: List[Project]


def extract_skills(text, client):
    prompt = f"""
    Extract all technical and professional skills from the CV.
    If a specific section or skill type is not present in the CV, return an empty list [] for that field. Do not infer or hallucinate skills.

    CV Content:
    {text}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": CVData,
        },
    )

    return response.parsed
