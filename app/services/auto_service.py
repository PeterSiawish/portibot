import os, json
from flask import current_app
from app.services.skill_comparison import full_comparison

DEFINED_ROLES = [
    "ai_ml",
    "frontend",
    "backend",
    "data_scientist",
    "devops",
    "fullstack",
    "game_dev",
    "mobile",
]


def run_auto_match(cv_data, model):
    results = []

    # Path to your job_data folder (using your config logic)
    job_data_path = current_app.config.get("JOB_DATA_DIR")

    for role in DEFINED_ROLES:
        file_path = os.path.join(job_data_path, f"{role}.json")

        with open(file_path, "r") as f:
            job_data = json.load(f)

        # Run the existing comparison
        comparison = full_comparison(cv_data, job_data, model)

        results.append(
            {
                "role": role,
                "score": comparison["overall_score"],
                # "details": comparison,
            }
        )

    # Sort by highest score first
    return sorted(results, key=lambda x: x["score"], reverse=True)
