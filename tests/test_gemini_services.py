"""
test_gemini_services.py: Unit tests for Gemini API service functions.

Tests cover three functions:
  - extract_skills(text, client)
  - evaluate_role(results, client)
  - generate_portfolio(cv_data, client)

Strategy: the Gemini client is replaced with a MagicMock that intercepts
the generate_content() call and returns a fake response object whose
.parsed attribute is a real, fully instantiated Pydantic schema object.

This approach tests:
  - That each function correctly calls generate_content()
  - That response.parsed.model_dump() is called and its output returned
  - That the returned dict contains all expected top-level keys
  - That the function handles edge cases (empty input, missing fields)

No real API calls are made to incur no additional costs.

Run with:  pytest tests/test_gemini_services.py -v
"""

from unittest.mock import MagicMock

from app.services.skill_extraction import extract_skills
from app.services.evaluation_service import evaluate_role, evaluate_auto
from app.services.portfolio_generation import generate_portfolio

from app.pydantic_schemas.profile_extraction_schemas.profile_base import TechnicalSkills
from app.pydantic_schemas.profile_extraction_schemas.cv_profile import CVProfile
from app.pydantic_schemas.evaluation_schemas.role_evaluation import (
    EvaluationSchema,
    SkillImpact,
    ProjectIdea,
    MarketPosition,
)
from app.pydantic_schemas.evaluation_schemas.auto_evaluation import (
    AutoEvaluationSchema,
    RoleComparison,
    CareerPivot,
)
from app.pydantic_schemas.portfolio_schemas.portfolio_schema import (
    PortfolioGenerationSchema,
)


# Helpers: build minimal valid Pydantic instances for mock responses


def make_mock_client(parsed_object):
    """
    Returns a MagicMock Gemini client whose generate_content() call
    returns a response object with .parsed set to the given Pydantic instance.
    """
    mock_response = MagicMock()
    mock_response.parsed = parsed_object

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    return mock_client


def make_cv_profile() -> CVProfile:
    """Minimal valid CVProfile instance to use as a mock API response."""
    return CVProfile(
        technical_skills=TechnicalSkills(
            languages=["Python", "JavaScript"],
            frameworks=["Flask", "React"],
            libraries=["NumPy"],
            databases=["PostgreSQL"],
            tools_platforms=["Docker", "Git"],
            concepts=["REST APIs", "OOP"],
        ),
        soft_skills=["Communication", "Teamwork"],
        experience_level="Entry",
        responsibilities=["Built REST APIs using Flask"],
        education=["BSc Software Engineering, 2025"],
        internships=[],
        projects=["Portfolio website generator"],
    )


def make_evaluation_schema() -> EvaluationSchema:
    """Minimal valid EvaluationSchema instance to use as a mock API response."""
    skill = SkillImpact(
        skill="Unit Testing",
        importance_weight="Critical",
        industry_context="Used daily to ensure code reliability.",
        learning_resource_type="Official Documentation",
    )
    project = ProjectIdea(
        title="Test-Driven Flask API",
        description="Build a REST API with full pytest coverage. Deploy with Docker.",
        technologies=["Flask", "PyTest", "Docker"],
    )
    market = MarketPosition(
        salary_readiness="Junior-level salary range.",
        competitive_edge="Strong Python foundation.",
        hiring_risk="Lacks deployment experience.",
    )
    return EvaluationSchema(
        verdict="A solid candidate with room to grow.",
        readiness_level="Junior Ready",
        readiness_score=72,
        top_strengths=[skill],
        critical_gaps=[skill],
        bridge_project=project,
        step_by_step_roadmap=["Week 1: Learn Docker", "Week 2: Write tests"],
        market_positioning=market,
        interview_advice="Frame your projects in terms of business impact.",
        final_thought="Keep building and stay consistent.",
    )


def make_auto_evaluation_schema() -> AutoEvaluationSchema:
    """Minimal valid AutoEvaluationSchema instance to use as a mock API response."""
    role_comparison = RoleComparison(
        role="Backend Engineer",
        score=0.78,
        match_narrative="Strong Python skills align well. Lacks cloud experience.",
        key_overlap=["Python", "Flask", "PostgreSQL"],
        primary_blocker="No cloud deployment experience.",
    )
    pivot = CareerPivot(
        target_role="DevOps Engineer",
        effort_level="Medium (3-6 months)",
        pivot_strategy="Learn Docker and CI/CD pipelines via a personal project.",
    )
    return AutoEvaluationSchema(
        technical_archetype="Python Software Engineer",
        executive_summary="A promising graduate with strong fundamentals.",
        best_fit_role="Backend Engineer",
        top_competency_rankings=[role_comparison],
        skill_synergy="Python and SQL are transferable across backend and data roles.",
        market_readiness_gap=["Cloud Deployment", "Unit Testing", "Documentation"],
        alternative_pathway=pivot,
        immediate_milestones=["1. Build a FastAPI project", "2. Learn Docker basics"],
        long_term_vision="In 2-3 years, you could be a mid-level engineer.",
    )


def make_portfolio_schema() -> PortfolioGenerationSchema:
    """Minimal valid PortfolioGenerationSchema instance to use as a mock API response."""
    return PortfolioGenerationSchema(
        html_code="<!DOCTYPE html><html><head></head><body><h1>Test Portfolio</h1></body></html>",
        filename="peter_portfolio.html",
    )


# extract_skills:


class TestExtractSkills:

    def test_returns_a_dict(self):
        """extract_skills must return a dictionary."""
        client = make_mock_client(make_cv_profile())
        result = extract_skills("Sample CV text", client)
        assert isinstance(result, dict)

    def test_generate_content_called_once(self):
        """generate_content must be called exactly once per extract_skills call."""
        client = make_mock_client(make_cv_profile())
        extract_skills("Sample CV text", client)
        client.models.generate_content.assert_called_once()

    def test_result_contains_technical_skills(self):
        """Result must contain a technical_skills key."""
        client = make_mock_client(make_cv_profile())
        result = extract_skills("Sample CV text", client)
        assert "technical_skills" in result

    def test_result_contains_all_top_level_keys(self):
        """Result must contain all expected top-level keys from CVProfile."""
        client = make_mock_client(make_cv_profile())
        result = extract_skills("Sample CV text", client)
        for key in [
            "technical_skills",
            "soft_skills",
            "experience_level",
            "responsibilities",
            "education",
            "internships",
            "projects",
        ]:
            assert key in result, f"Missing key: {key}"

    def test_technical_skills_contains_all_subcategories(self):
        """technical_skills in result must contain all defined subcategories."""
        client = make_mock_client(make_cv_profile())
        result = extract_skills("Sample CV text", client)
        for key in [
            "languages",
            "frameworks",
            "libraries",
            "databases",
            "tools_platforms",
            "concepts",
        ]:
            assert key in result["technical_skills"], f"Missing subcategory: {key}"

    def test_languages_is_a_list(self):
        """technical_skills.languages must be a list in the returned dict."""
        client = make_mock_client(make_cv_profile())
        result = extract_skills("Sample CV text", client)
        assert isinstance(result["technical_skills"]["languages"], list)

    def test_experience_level_is_valid_literal(self):
        """experience_level must be one of the defined Literal values."""
        client = make_mock_client(make_cv_profile())
        result = extract_skills("Sample CV text", client)
        valid_levels = ["Entry", "Mid", "Senior", "Lead", "Not Specified"]
        assert result["experience_level"] in valid_levels

    def test_empty_cv_text_still_calls_api(self):
        """
        Even with empty input text, extract_skills must still call the API
        rather than short-circuiting, the API handles empty inputs via
        its system instructions.
        """
        client = make_mock_client(make_cv_profile())
        extract_skills("", client)
        client.models.generate_content.assert_called_once()


# evaluate_role:


class TestEvaluateRole:

    def test_returns_a_dict(self):
        """evaluate_role must return a dictionary."""
        client = make_mock_client(make_evaluation_schema())
        result = evaluate_role({"role": "backend", "score": 0.7}, client)
        assert isinstance(result, dict)

    def test_generate_content_called_once(self):
        """generate_content must be called exactly once per evaluate_role call."""
        client = make_mock_client(make_evaluation_schema())
        evaluate_role({}, client)
        client.models.generate_content.assert_called_once()

    def test_result_contains_all_top_level_keys(self):
        """Result must contain all expected top-level keys from EvaluationSchema."""
        client = make_mock_client(make_evaluation_schema())
        result = evaluate_role({}, client)
        for key in [
            "verdict",
            "readiness_level",
            "readiness_score",
            "top_strengths",
            "critical_gaps",
            "bridge_project",
            "step_by_step_roadmap",
            "market_positioning",
            "interview_advice",
            "final_thought",
        ]:
            assert key in result, f"Missing key: {key}"

    def test_readiness_score_is_integer(self):
        """readiness_score must be an integer in the returned dict."""
        client = make_mock_client(make_evaluation_schema())
        result = evaluate_role({}, client)
        assert isinstance(result["readiness_score"], int)

    def test_readiness_score_within_valid_range(self):
        """readiness_score must be between 0 and 100 inclusive."""
        client = make_mock_client(make_evaluation_schema())
        result = evaluate_role({}, client)
        assert 0 <= result["readiness_score"] <= 100

    def test_top_strengths_is_a_list(self):
        """top_strengths must be a list in the returned dict."""
        client = make_mock_client(make_evaluation_schema())
        result = evaluate_role({}, client)
        assert isinstance(result["top_strengths"], list)

    def test_bridge_project_is_a_dict(self):
        """
        bridge_project must be a dict in the returned output (not a
        Pydantic object) since model_dump() is called before returning.
        """
        client = make_mock_client(make_evaluation_schema())
        result = evaluate_role({}, client)
        assert isinstance(result["bridge_project"], dict)

    def test_bridge_project_contains_required_fields(self):
        """bridge_project dict must contain title, description, and technologies."""
        client = make_mock_client(make_evaluation_schema())
        result = evaluate_role({}, client)
        for key in ["title", "description", "technologies"]:
            assert (
                key in result["bridge_project"]
            ), f"Missing key in bridge_project: {key}"


# evaluate_auto:


class TestEvaluateAuto:

    def test_returns_a_dict(self):
        """evaluate_auto must return a dictionary."""
        client = make_mock_client(make_auto_evaluation_schema())
        result = evaluate_auto({}, client)
        assert isinstance(result, dict)

    def test_result_contains_all_top_level_keys(self):
        """Result must contain all expected top-level keys from AutoEvaluationSchema."""
        client = make_mock_client(make_auto_evaluation_schema())
        result = evaluate_auto({}, client)
        for key in [
            "technical_archetype",
            "executive_summary",
            "best_fit_role",
            "top_competency_rankings",
            "skill_synergy",
            "market_readiness_gap",
            "alternative_pathway",
            "immediate_milestones",
            "long_term_vision",
        ]:
            assert key in result, f"Missing key: {key}"

    def test_top_competency_rankings_is_a_list(self):
        """top_competency_rankings must be a list."""
        client = make_mock_client(make_auto_evaluation_schema())
        result = evaluate_auto({}, client)
        assert isinstance(result["top_competency_rankings"], list)

    def test_alternative_pathway_is_a_dict(self):
        """alternative_pathway must be a dict after model_dump()."""
        client = make_mock_client(make_auto_evaluation_schema())
        result = evaluate_auto({}, client)
        assert isinstance(result["alternative_pathway"], dict)

    def test_alternative_pathway_contains_required_fields(self):
        """alternative_pathway must contain target_role, effort_level, pivot_strategy."""
        client = make_mock_client(make_auto_evaluation_schema())
        result = evaluate_auto({}, client)
        for key in ["target_role", "effort_level", "pivot_strategy"]:
            assert key in result["alternative_pathway"], f"Missing key: {key}"


# generate_portfolio:


class TestGeneratePortfolio:

    def test_returns_a_dict(self):
        """generate_portfolio must return a dictionary."""
        client = make_mock_client(make_portfolio_schema())
        result = generate_portfolio({"technical_skills": {}}, client)
        assert isinstance(result, dict)

    def test_generate_content_called_once(self):
        """generate_content must be called exactly once per generate_portfolio call."""
        client = make_mock_client(make_portfolio_schema())
        generate_portfolio({}, client)
        client.models.generate_content.assert_called_once()

    def test_result_contains_html_code(self):
        """Result must contain an html_code key."""
        client = make_mock_client(make_portfolio_schema())
        result = generate_portfolio({}, client)
        assert "html_code" in result

    def test_result_contains_filename(self):
        """Result must contain a filename key."""
        client = make_mock_client(make_portfolio_schema())
        result = generate_portfolio({}, client)
        assert "filename" in result

    def test_html_code_is_a_string(self):
        """html_code must be a string."""
        client = make_mock_client(make_portfolio_schema())
        result = generate_portfolio({}, client)
        assert isinstance(result["html_code"], str)

    def test_html_code_starts_with_doctype(self):
        """
        html_code must begin with <!DOCTYPE html>, confirming the schema
        enforces a complete HTML document structure rather than a fragment.
        """
        client = make_mock_client(make_portfolio_schema())
        result = generate_portfolio({}, client)
        assert result["html_code"].strip().startswith("<!DOCTYPE html")

    def test_filename_ends_with_html(self):
        """filename must end with .html as defined by the schema."""
        client = make_mock_client(make_portfolio_schema())
        result = generate_portfolio({}, client)
        assert result["filename"].endswith(".html")

    def test_empty_input_still_calls_api(self):
        """generate_portfolio must call the API even with empty cv_data."""
        client = make_mock_client(make_portfolio_schema())
        generate_portfolio({}, client)
        client.models.generate_content.assert_called_once()
