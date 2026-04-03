from sklearn.metrics.pairwise import cosine_similarity

STRONG_THRESHOLD = 0.75
PARTIAL_THRESHOLD = 0.5


def compare_category(model, cv_list, job_list, category):
    if not job_list:
        return 0, [], [], []

    if not cv_list:
        return (
            0,
            [],
            [],
            [{"category": category, "skill": skill, "score": 0} for skill in job_list],
        )

    cv_embeddings = model.encode(cv_list)
    job_embeddings = model.encode(job_list)

    strong_matches = []
    partial_matches = []
    missing_skills = []

    scores = []

    for i, job_skill in enumerate(job_list):
        similarities = cosine_similarity([job_embeddings[i]], cv_embeddings)[0]

        best_score = max(similarities)
        best_match = cv_list[similarities.argmax()]

        scores.append(best_score)

        if best_score >= STRONG_THRESHOLD:
            strong_matches.append(
                {
                    "category": category,
                    "job": job_skill,
                    "cv": best_match,
                    "score": float(best_score),
                }
            )

        elif best_score >= PARTIAL_THRESHOLD:
            partial_matches.append(
                {
                    "category": category,
                    "job": job_skill,
                    "cv": best_match,
                    "score": float(best_score),
                }
            )

        else:
            missing_skills.append(
                {"category": category, "skill": job_skill, "score": float(best_score)}
            )

    # Average score for category
    category_score = float(sum(scores) / len(scores))

    return category_score, strong_matches, partial_matches, missing_skills


def full_comparison(cv_data, job_data, model):
    results = {
        "category_scores": {},
        "strengths": [],
        "partial_matches": [],
        "missing_skills": [],
    }

    categories = [
        "languages",
        "frameworks",
        "libraries",
        "databases",
        "tools_platforms",
        "concepts",
    ]

    total_score = 0
    count = 0

    # Technical skills
    for category in categories:
        cv_list = cv_data["technical_skills"].get(category, [])
        job_list = job_data["technical_skills"].get(category, [])

        score, strong, partial, missing = compare_category(
            model, cv_list, job_list, category
        )

        results["category_scores"][category] = round(score, 2)

        results["strengths"].extend(strong)
        results["partial_matches"].extend(partial)
        results["missing_skills"].extend(missing)

        if job_list:
            total_score += score
            count += 1

    # Soft skills
    score, strong, partial, missing = compare_category(
        model,
        cv_data.get("soft_skills", []),
        job_data.get("soft_skills", []),
        "soft_skills",
    )

    results["category_scores"]["soft_skills"] = round(score, 2)

    results["strengths"].extend(strong)
    results["partial_matches"].extend(partial)
    results["missing_skills"].extend(missing)

    if job_data.get("soft_skills"):
        total_score += score
        count += 1

    overall_score = total_score / count if count > 0 else 0

    results["overall_score"] = float(round(overall_score, 2))

    return results
