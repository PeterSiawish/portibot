from typing import List, Literal
from pydantic import BaseModel, Field


class SkillImpact(BaseModel):
    skill: str = Field(description="The name of the skill (e.g., 'Unit Testing')")
    importance_weight: Literal["Critical", "Highly Desirable", "Nice-to-Have"] = Field(
        description="The priority level of this skill for the specific role."
    )
    industry_context: str = Field(
        description="A brief explanation of how this skill is used daily in this specific role."
    )
    learning_resource_type: str = Field(
        description="Suggested way to learn: e.g., 'Official Documentation', 'Open Source Contribution', or 'Portfolio Project'"
    )


class ProjectIdea(BaseModel):
    title: str = Field(
        description="A creative title for a mini-project to prove a missing skill."
    )
    description: str = Field(
        description="A 2-sentence prompt of what to build to bridge a specific gap."
    )
    technologies: List[str] = Field(
        description="The specific stack to use (e.g., ['PyTest', 'Docker', 'GitHub Actions'])."
    )


class MarketPosition(BaseModel):
    salary_readiness: str = Field(
        description="Assessment of whether their current skills command a junior, mid, or intern-level salary for this role."
    )
    competitive_edge: str = Field(
        description="The one 'X-factor' the candidate has that others might lack."
    )
    hiring_risk: str = Field(
        description="The biggest concern a hiring manager would have (e.g., 'Lacks experience with deployment')."
    )


class EvaluationSchema(BaseModel):
    # Professional Narrative
    verdict: str = Field(
        description="A 5-6 sentence executive summary. Be blunt, professional, and mentor-like."
    )
    readiness_level: str = Field(
        description="Classification: 'Intern Ready', 'Junior Ready', 'Mid-Level Transition', or 'Foundational Development Needed'."
    )
    readiness_score: int = Field(
        ge=0, le=100, description="Numerical match percentage."
    )

    # Technical Breakdown
    top_strengths: List[SkillImpact] = Field(
        description="3-4 existing skills and why they are high-impact for this specific role."
    )
    critical_gaps: List[SkillImpact] = Field(
        description="The top 4 missing areas that would cause a 'Reject' in an interview."
    )

    # Actionable Growth
    bridge_project: ProjectIdea = Field(
        description="A specific project recommendation that addresses multiple gaps at once."
    )
    step_by_step_roadmap: List[str] = Field(
        description="A chronological 4-week plan to become 'Interview Ready'."
    )

    # Recruitment Insights
    market_positioning: MarketPosition = Field(
        description="How the candidate sits relative to the current Software Engineering graduate market."
    )
    interview_advice: str = Field(
        description="One specific tip on how to talk about their current experience to mask their gaps."
    )

    final_thought: str = Field(
        description="Wrap up the evaluation with a sentence or two."
    )
