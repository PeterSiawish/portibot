from typing import List
from pydantic import BaseModel, Field


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
