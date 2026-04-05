import numpy as np


def embed_cv_data(cv_data, model):
    """
    Converts extracted CV text into a dictionary of embeddings.
    """
    cv_embeddings = {}

    # 1. Process Technical Skills
    tech_cv = cv_data.get("technical_skills", {})
    categories = [
        "languages",
        "frameworks",
        "libraries",
        "databases",
        "tools_platforms",
        "concepts",
    ]

    cv_embeddings["technical_skills"] = {}

    for cat in categories:
        items = tech_cv.get(cat, [])
        if items:
            # model.encode returns a numpy array of vectors
            cv_embeddings["technical_skills"][cat] = model.encode(items)
        else:
            # Store empty array if no skills in this category
            cv_embeddings["technical_skills"][cat] = np.array([])

    # 2. Process Soft Skills
    soft_items = cv_data.get("soft_skills", [])
    cv_embeddings["soft_skills"] = (
        model.encode(soft_items) if soft_items else np.array([])
    )

    # 3. Process Responsibilities
    resp_items = cv_data.get("responsibilities", [])
    cv_embeddings["responsibilities"] = (
        model.encode(resp_items) if resp_items else np.array([])
    )

    return cv_embeddings
