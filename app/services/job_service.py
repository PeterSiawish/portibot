import json
import os

# Import the pydantic model schema here later


def load_job_data(role):
    file_path = os.path.join("jobs", f"{role}.json")

    if not os.path.exists(file_path):
        raise ValueError("Invalid role selected")

    with open(file_path, "r") as f:
        data = json.load(f)

    # job_model = JobModel(**data)

    return job_model.model_dump()
