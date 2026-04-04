import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Thresholds for categorization
STRONG_THRESHOLD = 0.75
PARTIAL_THRESHOLD = 0.5


def compare_category(model, cv_list, job_list, category):
    """
    Compares a list of skills from the CV against a list of required skills from the Job.
    Returns the average score and a dictionary of matches categorized by strength.
    """

    # If the job doesn't require anything in this category, it's a perfect match by default
    if not job_list:
        return 1.0, {"strong": [], "partial": [], "missing": []}

    # If the job requires skills but the CV has none, everything is missing
    if not cv_list:
        return 0.0, {
            "strong": [],
            "partial": [],
            "missing": [
                {"category": category, "skill": s, "score": 0.0} for s in job_list
            ],
        }

    # 1. Vectorize everything at once for optimization
    cv_embeddings = model.encode(cv_list)
    job_embeddings = model.encode(job_list)

    # 2. Calculate the similarity matrix (Shape: len(job_list) x len(cv_list))
    # Each row 'i' represents a Job Skill compared against every CV Skill 'j'
    similarity_matrix = cosine_similarity(job_embeddings, cv_embeddings)

    cat_results = {"strong": [], "partial": [], "missing": []}
    scores = []

    # 3. Analyze each job requirement
    for i, job_skill in enumerate(job_list):
        best_match_idx = np.argmax(similarity_matrix[i])
        best_score = float(similarity_matrix[i][best_match_idx])
        best_cv_item = cv_list[best_match_idx]

        # If direct match, return optimal score
        if job_skill.lower().strip() == best_cv_item.lower().strip():
            best_score = 1.0

        scores.append(best_score)

        match_data = {
            "category": category,
            "job": job_skill,
            "cv": best_cv_item,
            "score": round(best_score, 2),
        }

        if best_score >= STRONG_THRESHOLD:
            cat_results["strong"].append(match_data)
        elif best_score >= PARTIAL_THRESHOLD:
            cat_results["partial"].append(match_data)
        else:
            cat_results["missing"].append(
                {
                    "category": category,
                    "missing_skill": job_skill,
                    "score": round(best_score, 2),
                }
            )

    avg_score = sum(scores) / len(scores)
    return avg_score, cat_results


def full_comparison(cv_data, job_data, model):
    """
    Orchestrates the full comparison between CV and Job Description JSONs.
    """

    results = {
        "overall_score": 0,
        "category_scores": {},
        "strengths": [],
        "partial_matches": [],
        "missing_skills": [],
    }

    # Define technical categories to iterate through
    tech_categories = [
        "languages",
        "frameworks",
        "libraries",
        "databases",
        "tools_platforms",
        "concepts",
    ]

    WEIGHTS = {
        "languages": 0.15,
        "frameworks": 0.15,
        "concepts": 0.225,
        "libraries": 0.075,
        "databases": 0.10,
        "tools_platforms": 0.10,
        "soft_skills": 0.05,
        "responsibilities": 0.15,
    }

    total_score_sum = 0.0
    total_weight_used = 0.0

    # 1. Process Technical Skills
    tech_skills_cv = cv_data.get("technical_skills", {})
    tech_skills_job = job_data.get("technical_skills", {})

    for category in tech_categories:
        cv_list = tech_skills_cv.get(category, [])
        job_list = tech_skills_job.get(category, [])

        score, cat_results = compare_category(model, cv_list, job_list, category)

        results["category_scores"][category] = round(score, 2)
        results["strengths"].extend(cat_results["strong"])
        results["partial_matches"].extend(cat_results["partial"])
        results["missing_skills"].extend(cat_results["missing"])

        if job_list:
            category_weight = WEIGHTS.get(category, 0.1)
            total_score_sum += score * (category_weight)
            total_weight_used += category_weight

    # 2. Process Soft Skills
    soft_score, soft_results = compare_category(
        model,
        cv_data.get("soft_skills", []),
        job_data.get("soft_skills", []),
        "soft_skills",
    )

    results["category_scores"]["soft_skills"] = round(soft_score, 2)
    results["strengths"].extend(soft_results["strong"])
    results["partial_matches"].extend(soft_results["partial"])
    results["missing_skills"].extend(soft_results["missing"])

    if job_data.get("soft_skills"):
        category_weight = WEIGHTS.get("soft_skills", 0.1)
        total_score_sum += soft_score * category_weight
        total_weight_used += category_weight

    # 3. Process Responsibilities
    resp_score, resp_results = compare_category(
        model,
        cv_data.get("responsibilities", []),
        job_data.get("responsibilities", []),
        "responsibilities",
    )

    results["category_scores"]["responsibilities"] = round(resp_score, 2)
    results["strengths"].extend(resp_results["strong"])
    results["partial_matches"].extend(resp_results["partial"])
    results["missing_skills"].extend(resp_results["missing"])

    if job_data.get("responsibilities"):
        category_weight = WEIGHTS.get("responsibilities", 0.1)
        total_score_sum += resp_score * category_weight
        total_weight_used += category_weight

    # 4. Calculate Weighted Overall Score
    if total_weight_used > 0:
        results["overall_score"] = round(float(total_score_sum / total_weight_used), 2)
    else:
        results["overall_score"] = 0.0

    return results
