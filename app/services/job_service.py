import json, os
from app.models.job_profile import JobProfile


def load_job_data(role):
    file_path = os.path.join("job_data", f"{role}.json")

    if not os.path.exists(file_path):
        raise ValueError(
            f"Invalid role selected: {role}. Please select a different role."
        )

    with open(file_path, "r") as f:
        data = json.load(f)

    job_model = JobProfile(**data)

    return job_model.model_dump()
