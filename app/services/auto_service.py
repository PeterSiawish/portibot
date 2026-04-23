from app.services.skill_comparison import full_comparison


def run_auto_match(cv_data, cv_embeddings, job_data, job_embeddings, first_name):
    results = []

    for role in job_data.keys():
        if role not in job_data or role not in job_embeddings:
            continue

        role_data = job_data[role]
        role_data_embedding = job_embeddings[role]

        # Run the existing comparison
        comparison = full_comparison(
            cv_data, cv_embeddings, role_data, role_data_embedding, role, first_name
        )

        results.append(
            {
                "role": role,
                "score": comparison["overall_score"],
                "details": comparison,
            }
        )

    # Sort by highest score first
    return sorted(results, key=lambda x: x["score"], reverse=True)
