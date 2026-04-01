from typing import List, Literal
from pydantic import BaseModel, Field


# The following Pydantic classes define the expected structure of the JSON response from the Gemini API.
class TechnicalSkills(BaseModel):
    languages: List[str] = Field(
        default_factory=list,
        description="Programming languages only (e.g., Python, TypeScript).",
    )
    frameworks: List[str] = Field(
        default_factory=list,
        description="Web or application frameworks (e.g., Flask, React, Django).",
    )
    libraries: List[str] = Field(
        default_factory=list,
        description="Software libraries and packages (e.g., NumPy, Redux, OpenCV).",
    )
    databases: List[str] = Field(
        default_factory=list,
        description="Database management systems (e.g., PostgreSQL, MongoDB).",
    )
    tools_platforms: List[str] = Field(
        default_factory=list,
        description="DevOps tools, cloud providers, and version control (e.g., AWS, Docker, Git).",
    )
    concepts: List[str] = Field(
        default_factory=list,
        description="High-level technical methodologies or architectural patterns (e.g., Microservices, OOP, RESTful APIs).",
    )


class ProfessionalProfile(BaseModel):
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
            "response_schema": ProfessionalProfile,
        },
    )

    return response.parsed
