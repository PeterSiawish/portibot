from google.genai import types
from app.pydantic_schemas.profile_extraction_schemas.cv_profile import CVProfile

system_instructions = """
You are an expert CV analyst specialising in software engineering recruitment.

Your goal is to accurately extract structured skill and experience data from a candidate's CV.

STRICT RULES:
1. Output ONLY valid JSON (no markdown, no explanations)
2. Follow the schema EXACTLY
3. Do NOT hallucinate or infer skills not explicitly present in the CV
4. If a field is not present in the CV, return an empty list [] or empty string ""
5. Do not make assumptions about the candidate's experience level without evidence

FAILURE CONDITIONS:
- Fabricating skills or technologies not present in the CV
- Returning fields not defined in the schema
- Including markdown or explanations in the output
"""


def extract_skills(text, client):
    prompt = f"""
    TASK:
    Extract all technical and professional skills from the provided CV content.

    CV CONTENT:
    {text}

    OUTPUT REQUIREMENTS:
    - Return ONLY valid JSON matching the schema
    - If a specific section or skill type is not present, return an empty list [] or empty string ""
    - Do not hallucinate or make up skills
    - Operate exclusively on the provided text
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instructions,
            response_mime_type="application/json",
            response_schema=CVProfile,
        ),
    )

    return response.parsed.model_dump()
