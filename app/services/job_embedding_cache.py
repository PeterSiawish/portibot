JOB_DATA = {}
JOB_EMBEDDINGS = {}


def preload_jobs(app, model):
    """
    Called once during app startup.
    Loads JSONs and encodes them into JOB_EMBEDDINGS.
    """
    import os
    import json
    import numpy as np

    job_data_path = app.config.get("JOB_DATA_DIR")

    for filename in os.listdir(job_data_path):
        if not filename.endswith(".json"):
            continue

        role = filename.replace(".json", "")
        file_path = os.path.join(job_data_path, filename)

        with open(file_path, "r") as f:
            data = json.load(f)

        JOB_DATA[role] = data
        JOB_EMBEDDINGS[role] = {
            "technical_skills": {},
            "soft_skills": np.array([]),
            "responsibilities": np.array([]),
        }

        # 1. Technical Skills
        tech = data.get("technical_skills", {})
        for category, items in tech.items():
            if items:
                JOB_EMBEDDINGS[role]["technical_skills"][category] = model.encode(items)

        # 2. Soft Skills
        soft = data.get("soft_skills", [])
        if soft:
            JOB_EMBEDDINGS[role]["soft_skills"] = model.encode(soft)

        # 3. Responsibilities
        resp = data.get("responsibilities", [])
        if resp:
            JOB_EMBEDDINGS[role]["responsibilities"] = model.encode(resp)
