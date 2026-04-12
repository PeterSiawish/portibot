from typing import List, Literal
from pydantic import BaseModel, Field


class RoleComparison(BaseModel):
    role: str = Field(description="The name of the job role (e.g., 'Backend Engineer')")
    score: float = Field(
        description="The 0-1 similarity score from the matching engine"
    )
    match_narrative: str = Field(
        description="A 2-sentence explanation of why the candidate fits or struggles with this specific role."
    )
    key_overlap: List[str] = Field(
        description="The top 3 skills the candidate possesses that are most relevant to THIS role."
    )
    primary_blocker: str = Field(
        description="The single most significant missing skill or experience preventing a higher score."
    )


class CareerPivot(BaseModel):
    target_role: str = Field(
        description="A role the candidate didn't score highest in, but has high potential for."
    )
    effort_level: Literal[
        "Low (1-3 months)", "Medium (3-6 months)", "High (6+ months)"
    ] = Field(
        description="How much work is needed to pivot: 'Low (1-3 months)', 'Medium (3-6 months)', 'High (6+ months)'."
    )
    pivot_strategy: str = Field(
        description="One specific piece of advice on how to transition toward this role."
    )


class AutoEvaluationSchema(BaseModel):
    # Overall Picture
    technical_archetype: str = Field(
        description=(
            "A formal, industry-standard professional title based on the candidate's core expertise. Examples: 'Junior Backend Engineer', 'Full-Stack Developer', 'Machine Learning Research Intern', or 'Software Engineer (DevOps focus)'. Avoid flowery language or creative metaphors."
        )
    )
    executive_summary: str = Field(
        description="A deep-dive paragraph (5-6 sentences) synthesizing their overall marketability and current standing in the graduate job market."
    )

    # Comparative Analysis
    best_fit_role: str = Field(
        description="The role with the highest semantic and technical alignment."
    )
    top_competency_rankings: List[RoleComparison] = Field(
        description="A detailed breakdown of the top 3-4 roles to show the candidate their options."
    )

    # Strategic Growth
    skill_synergy: str = Field(
        description="Explain which skills are 'transferable' across multiple roles they scored well in."
    )
    market_readiness_gap: List[str] = Field(
        description="A list of 3 high-level industry 'soft' requirements missing (e.g., 'Cloud Deployment', 'Unit Testing', 'Documentation')."
    )

    # The Pivot Logic
    alternative_pathway: CareerPivot = Field(
        description="An 'outside the box' recommendation based on their latent skills."
    )

    # Closing Actions
    immediate_milestones: List[str] = Field(
        description="4 specific, chronological tasks (e.g., 1. Build a FastAPI project, 2. Learn Docker basics)."
    )
    long_term_vision: str = Field(
        description="A final motivating statement about where this candidate could be in 2-3 years if they follow the plan."
    )
