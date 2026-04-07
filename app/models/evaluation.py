from typing import List
from pydantic import BaseModel, Field


class CriticalGap(BaseModel):
    skill: str = Field(description="The name of the missing skill or concept")
    industry_reason: str = Field(
        description="Brief explanation of why this skill is important in the target role"
    )


class Readiness(BaseModel):
    readiness: str = Field(
        description="Level: e.g., 'Entry-Level Ready', 'Needs Foundational Work', or 'Near-Mid Level'"
    )
    overall_readiness: int = Field(
        description="A numerical representation out of 100 that showcases their overall level."
    )


class EvaluationSchema(BaseModel):
    verdict: str = Field(
        description="A 4-5 sentence professional summary paragraph of the candidate's profile."
    )
    readiness: Readiness
    strengths_analysis: List[str] = Field(
        description="3 key strengths that make the candidate stand out for this specific role"
    )
    critical_gaps: List[CriticalGap] = Field(
        description="The most impactful missing skills with industry context"
    )
    action_plan: List[str] = Field(
        description="4 step-by-step technical goals to reach role-readiness"
    )
    next_step: str = Field(
        description="The single most important thing the candidate should do today"
    )
