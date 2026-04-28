"""
test_comparison.py: Unit tests for the CV evaluation algorithm in app/services/skill_comparison.py.

Tests cover two functions:
  - compare_category(cv_embeddings, job_embeddings, cv_list, job_list, category)
  - full_comparison(cv_data, cv_embeddings, job_data, job_embeddings, role, first_name)

Strategy: rather than mocking the embedding model, we construct small numpy
vectors manually that produce known cosine similarity scores. This lets us
test the classification logic (strong/partial/missing thresholds) and the
weighted scoring in full, with zero external dependencies.

Cosine similarity between two identical unit vectors = 1.0
Cosine similarity between two orthogonal vectors   = 0.0
We use linear combinations to produce scores in between.

Run with: pytest tests/test_comparison.py -v
"""

import numpy as np

from app.services.skill_comparison import compare_category, full_comparison


# Helpers: construct vectors with known cosine similarity


def unit(v):
    """Return the unit vector of v."""
    v = np.array(v, dtype=float)
    return v / np.linalg.norm(v)


# Two orthogonal basis vectors in 3D space, similarity = 0.0
VEC_A = unit([1, 0, 0])
VEC_B = unit([0, 1, 0])

# A vector at ~45 degrees to VEC_A, similarity to VEC_A ≈ 0.707
VEC_MID = unit([1, 1, 0])

# A vector very close to VEC_A, similarity > 0.75
VEC_CLOSE = unit([1, 0.2, 0])

# A vector between PARTIAL and STRONG thresholds, similarity ~0.55
# [1, 1.5, 0] normalised produces cos similarity with VEC_A of ~0.555
VEC_PARTIAL = unit([1, 1.5, 0])


def row(v):
    """Reshape a 1D vector into a 2D row matrix as sklearn expects."""
    return np.array(v).reshape(1, -1)


# compare_category: edge cases (no embeddings needed)


class TestCompareCategoryEdgeCases:

    def test_empty_job_list_returns_perfect_score(self):
        """
        If the job requires nothing in a category, the candidate scores 1.0
        by default, they cannot be penalised for a non-requirement.
        """
        score, results = compare_category(
            cv_embeddings=row(VEC_A),
            job_embeddings=row(VEC_A),
            cv_list=["Python"],
            job_list=[],
            category="languages",
        )
        assert score == 1.0
        assert results == {"strong": [], "partial": [], "missing": []}

    def test_empty_cv_list_returns_zero_score(self):
        """
        If the job requires skills but the candidate has none listed,
        every required skill is classified as missing and the score is 0.0.
        """
        score, results = compare_category(
            cv_embeddings=np.array([]),
            job_embeddings=row(VEC_A),
            cv_list=[],
            job_list=["Python", "Django"],
            category="languages",
        )
        assert score == 0.0
        assert len(results["missing"]) == 2
        assert results["strong"] == []
        assert results["partial"] == []

    def test_empty_cv_missing_items_contain_correct_category(self):
        """Missing skill entries must record the correct category label."""
        _, results = compare_category(
            cv_embeddings=np.array([]),
            job_embeddings=row(VEC_A),
            cv_list=[],
            job_list=["Docker"],
            category="tools_platforms",
        )
        assert results["missing"][0]["category"] == "tools_platforms"
        assert results["missing"][0]["score"] == 0.0

    def test_both_lists_empty_returns_perfect_score(self):
        """If neither side has skills in a category, score should be 1.0."""
        score, results = compare_category(
            cv_embeddings=np.array([]),
            job_embeddings=np.array([]),
            cv_list=[],
            job_list=[],
            category="libraries",
        )
        assert score == 1.0


# compare_category: classification thresholds


class TestCompareCategoryClassification:

    def test_exact_string_match_scores_1(self):
        """
        When the job skill and the best CV match are identical strings,
        the score must be forced to 1.0 regardless of vector similarity.
        """
        score, results = compare_category(
            cv_embeddings=row(VEC_A),
            job_embeddings=row(VEC_A),
            cv_list=["Python"],
            job_list=["Python"],
            category="languages",
        )
        assert score == 1.0
        assert len(results["strong"]) == 1
        assert results["strong"][0]["score"] == 1.0

    def test_exact_match_case_insensitive(self):
        """
        Exact string matching must be case-insensitive: 'python' and 'Python'
        are the same skill.
        """
        score, results = compare_category(
            cv_embeddings=row(VEC_A),
            job_embeddings=row(VEC_A),
            cv_list=["python"],
            job_list=["Python"],
            category="languages",
        )
        assert score == 1.0
        assert len(results["strong"]) == 1

    def test_high_similarity_classified_as_strong(self):
        """
        A cosine similarity >= 0.75 (but not an exact string match)
        must be classified as a strong match.
        """
        # VEC_CLOSE vs VEC_A produces similarity > 0.75
        _, results = compare_category(
            cv_embeddings=row(VEC_CLOSE),
            job_embeddings=row(VEC_A),
            cv_list=["backend development"],
            job_list=["server-side engineering"],
            category="concepts",
        )
        assert len(results["strong"]) == 1
        assert results["strong"][0]["score"] >= 0.75

    def test_medium_similarity_classified_as_partial(self):
        """
        A cosine similarity >= 0.50 and < 0.75 must be classified as partial.
        """
        # VEC_PARTIAL vs VEC_A produces similarity between 0.5 and 0.75
        from sklearn.metrics.pairwise import cosine_similarity as cos_sim

        actual_score = float(cos_sim(row(VEC_A), row(VEC_PARTIAL))[0][0])
        assert (
            0.50 <= actual_score < 0.75
        ), f"Test vector misconfigured: score was {actual_score}"

        _, results = compare_category(
            cv_embeddings=row(VEC_PARTIAL),
            job_embeddings=row(VEC_A),
            cv_list=["related skill"],
            job_list=["target skill"],
            category="frameworks",
        )
        assert len(results["partial"]) == 1
        assert 0.50 <= results["partial"][0]["score"] < 0.75

    def test_low_similarity_classified_as_missing(self):
        """
        A cosine similarity < 0.50 must be classified as missing.
        VEC_A and VEC_B are orthogonal (similarity = 0.0).
        """
        _, results = compare_category(
            cv_embeddings=row(VEC_B),
            job_embeddings=row(VEC_A),
            cv_list=["unrelated skill"],
            job_list=["required skill"],
            category="databases",
        )
        assert len(results["missing"]) == 1
        assert results["missing"][0]["score"] < 0.50

    def test_boundary_exactly_at_strong_threshold(self):
        """
        A score of exactly 0.75 must be classified as strong, not partial
        (boundary value >= 0.75 is strong).
        """
        # Construct a vector whose cosine similarity with VEC_A is exactly 0.75
        # cos(angle) = 0.75 -> we solve for the vector components
        target = 0.75
        y = np.sqrt(1 - target**2)
        vec_boundary = unit([target, y, 0])

        from sklearn.metrics.pairwise import cosine_similarity as cos_sim

        actual = float(cos_sim(row(VEC_A), row(vec_boundary))[0][0])
        assert abs(actual - 0.75) < 1e-6, f"Boundary vector misconfigured: {actual}"

        _, results = compare_category(
            cv_embeddings=row(vec_boundary),
            job_embeddings=row(VEC_A),
            cv_list=["borderline skill"],
            job_list=["required skill"],
            category="concepts",
        )
        assert len(results["strong"]) == 1
        assert len(results["partial"]) == 0

    def test_boundary_exactly_at_partial_threshold(self):
        """
        A score of exactly 0.50 must be classified as partial, not missing
        (boundary value >= 0.50 is partial).
        """
        target = 0.50
        y = np.sqrt(1 - target**2)
        vec_boundary = unit([target, y, 0])

        from sklearn.metrics.pairwise import cosine_similarity as cos_sim

        actual = float(cos_sim(row(VEC_A), row(vec_boundary))[0][0])
        assert abs(actual - 0.50) < 1e-6, f"Boundary vector misconfigured: {actual}"

        _, results = compare_category(
            cv_embeddings=row(vec_boundary),
            job_embeddings=row(VEC_A),
            cv_list=["borderline skill"],
            job_list=["required skill"],
            category="concepts",
        )
        assert len(results["partial"]) == 1
        assert len(results["missing"]) == 0

    def test_multiple_job_skills_best_match_selected(self):
        """
        When the CV has multiple skills, each job skill should match against
        the best available CV skill, not just the first.
        """
        # CV has two skills: one close to VEC_A, one orthogonal
        cv_vecs = np.vstack([row(VEC_B), row(VEC_A)])  # best match is VEC_A
        _, results = compare_category(
            cv_embeddings=cv_vecs,
            job_embeddings=row(VEC_A),
            cv_list=["unrelated", "Python"],
            job_list=["Python"],
            category="languages",
        )
        # Should find the best match (VEC_A vs VEC_A), not the worst
        assert len(results["strong"]) == 1

    def test_match_data_contains_required_fields(self):
        """
        Every match entry (strong or partial) must contain
        category, job, cv, and score fields.
        """
        _, results = compare_category(
            cv_embeddings=row(VEC_A),
            job_embeddings=row(VEC_A),
            cv_list=["Python"],
            job_list=["Python"],
            category="languages",
        )
        match = results["strong"][0]
        assert "category" in match
        assert "job" in match
        assert "cv" in match
        assert "score" in match

    def test_missing_data_contains_required_fields(self):
        """
        Every missing entry must contain category, missing_skill, and score.
        """
        _, results = compare_category(
            cv_embeddings=row(VEC_B),
            job_embeddings=row(VEC_A),
            cv_list=["unrelated"],
            job_list=["Docker"],
            category="tools_platforms",
        )
        missing = results["missing"][0]
        assert "category" in missing
        assert "missing_skill" in missing
        assert "score" in missing


# full_comparison: weighted scoring and result structure


def make_minimal_cv_data(**overrides):
    """
    Returns a minimal CV data dict with all required fields.
    Individual categories can be overridden for specific tests.
    """
    base = {
        "technical_skills": {
            "languages": [],
            "frameworks": [],
            "libraries": [],
            "databases": [],
            "tools_platforms": [],
            "concepts": [],
        },
        "soft_skills": [],
        "responsibilities": [],
    }
    base.update(overrides)
    return base


def make_minimal_embeddings(**overrides):
    """Returns a minimal embeddings dict with empty arrays by default."""
    base = {
        "technical_skills": {
            "languages": np.array([]),
            "frameworks": np.array([]),
            "libraries": np.array([]),
            "databases": np.array([]),
            "tools_platforms": np.array([]),
            "concepts": np.array([]),
        },
        "soft_skills": np.array([]),
        "responsibilities": np.array([]),
    }
    base.update(overrides)
    return base


class TestFullComparison:

    def test_result_contains_required_top_level_keys(self):
        """
        The result dict must contain all expected top-level keys
        regardless of input content.
        """
        result = full_comparison(
            cv_data=make_minimal_cv_data(),
            cv_embeddings=make_minimal_embeddings(),
            job_data=make_minimal_cv_data(),
            job_embeddings=make_minimal_embeddings(),
            role="backend",
            first_name="Peter",
        )
        for key in [
            "first_name",
            "role",
            "overall_score",
            "category_scores",
            "strengths",
            "partial_matches",
            "missing_skills",
        ]:
            assert key in result, f"Missing key: {key}"

    def test_first_name_and_role_passed_through(self):
        """first_name and role must be preserved exactly in the result."""
        result = full_comparison(
            cv_data=make_minimal_cv_data(),
            cv_embeddings=make_minimal_embeddings(),
            job_data=make_minimal_cv_data(),
            job_embeddings=make_minimal_embeddings(),
            role="frontend",
            first_name="Alice",
        )
        assert result["first_name"] == "Alice"
        assert result["role"] == "frontend"

    def test_empty_cv_against_empty_job_scores_zero(self):
        """
        When both CV and job data are empty across all categories,
        the overall score should be 0.0 as no weights are applied.
        """
        result = full_comparison(
            cv_data=make_minimal_cv_data(),
            cv_embeddings=make_minimal_embeddings(),
            job_data=make_minimal_cv_data(),
            job_embeddings=make_minimal_embeddings(),
            role="backend",
            first_name="Test",
        )
        assert result["overall_score"] == 0.0

    def test_perfect_match_scores_1(self):
        """
        When CV and job data are identical (same skills, same vectors),
        the overall score should be 1.0.
        """
        cv_data = make_minimal_cv_data(
            **{
                "technical_skills": {
                    "languages": ["Python"],
                    "frameworks": [],
                    "libraries": [],
                    "databases": [],
                    "tools_platforms": [],
                    "concepts": [],
                },
                "soft_skills": [],
                "responsibilities": [],
            }
        )
        job_data = make_minimal_cv_data(
            **{
                "technical_skills": {
                    "languages": ["Python"],
                    "frameworks": [],
                    "libraries": [],
                    "databases": [],
                    "tools_platforms": [],
                    "concepts": [],
                },
                "soft_skills": [],
                "responsibilities": [],
            }
        )
        cv_emb = make_minimal_embeddings()
        cv_emb["technical_skills"]["languages"] = row(VEC_A)

        job_emb = make_minimal_embeddings()
        job_emb["technical_skills"]["languages"] = row(VEC_A)

        result = full_comparison(cv_data, cv_emb, job_data, job_emb, "backend", "Test")
        assert result["overall_score"] == 1.0

    def test_strengths_populated_on_strong_matches(self):
        """Strong matches must appear in the strengths list."""
        cv_data = make_minimal_cv_data(
            **{
                "technical_skills": {
                    "languages": ["Python"],
                    "frameworks": [],
                    "libraries": [],
                    "databases": [],
                    "tools_platforms": [],
                    "concepts": [],
                },
                "soft_skills": [],
                "responsibilities": [],
            }
        )
        job_data = make_minimal_cv_data(
            **{
                "technical_skills": {
                    "languages": ["Python"],
                    "frameworks": [],
                    "libraries": [],
                    "databases": [],
                    "tools_platforms": [],
                    "concepts": [],
                },
                "soft_skills": [],
                "responsibilities": [],
            }
        )
        cv_emb = make_minimal_embeddings()
        cv_emb["technical_skills"]["languages"] = row(VEC_A)
        job_emb = make_minimal_embeddings()
        job_emb["technical_skills"]["languages"] = row(VEC_A)

        result = full_comparison(cv_data, cv_emb, job_data, job_emb, "backend", "Test")
        assert len(result["strengths"]) >= 1

    def test_missing_skills_populated_on_no_cv_match(self):
        """Skills the CV has no match for must appear in missing_skills."""
        cv_data = make_minimal_cv_data()  # no skills at all
        job_data = make_minimal_cv_data(
            **{
                "technical_skills": {
                    "languages": ["Python"],
                    "frameworks": [],
                    "libraries": [],
                    "databases": [],
                    "tools_platforms": [],
                    "concepts": [],
                },
                "soft_skills": [],
                "responsibilities": [],
            }
        )
        job_emb = make_minimal_embeddings()
        job_emb["technical_skills"]["languages"] = row(VEC_A)

        result = full_comparison(
            cv_data, make_minimal_embeddings(), job_data, job_emb, "backend", "Test"
        )
        assert len(result["missing_skills"]) >= 1

    def test_overall_score_is_between_0_and_1(self):
        """The overall score must always be in the valid range [0.0, 1.0]."""
        cv_data = make_minimal_cv_data(
            **{
                "technical_skills": {
                    "languages": ["Java"],
                    "frameworks": [],
                    "libraries": [],
                    "databases": [],
                    "tools_platforms": [],
                    "concepts": [],
                },
                "soft_skills": [],
                "responsibilities": [],
            }
        )
        job_data = make_minimal_cv_data(
            **{
                "technical_skills": {
                    "languages": ["Python"],
                    "frameworks": [],
                    "libraries": [],
                    "databases": [],
                    "tools_platforms": [],
                    "concepts": [],
                },
                "soft_skills": [],
                "responsibilities": [],
            }
        )
        cv_emb = make_minimal_embeddings()
        cv_emb["technical_skills"]["languages"] = row(VEC_B)
        job_emb = make_minimal_embeddings()
        job_emb["technical_skills"]["languages"] = row(VEC_A)

        result = full_comparison(cv_data, cv_emb, job_data, job_emb, "backend", "Test")
        assert 0.0 <= result["overall_score"] <= 1.0

    def test_category_scores_present_for_all_categories(self):
        """category_scores must contain an entry for every evaluated category."""
        result = full_comparison(
            cv_data=make_minimal_cv_data(),
            cv_embeddings=make_minimal_embeddings(),
            job_data=make_minimal_cv_data(),
            job_embeddings=make_minimal_embeddings(),
            role="backend",
            first_name="Test",
        )
        expected_categories = [
            "languages",
            "frameworks",
            "libraries",
            "databases",
            "tools_platforms",
            "concepts",
            "soft_skills",
            "responsibilities",
        ]
        for cat in expected_categories:
            assert cat in result["category_scores"], f"Missing category: {cat}"
