from app.models.cv_profile import CVProfile


def extract_skills(text, client):
    prompt = f"""
    Extract all technical and professional skills from the CV.
    If a specific section or skill type is not present in the CV, return an empty list [] or string "" for that field. Do not infer or hallucinate skills.

    CV Content:
    {text}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": CVProfile,
        },
    )

    # Convert to Python Dictionary before returning
    return response.parsed.model_dump()
