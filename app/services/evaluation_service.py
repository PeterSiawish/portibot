from google.genai import types
from app.models.evaluation import EvaluationSchema


def evaluate(results, client):
    prompt = f"""
    Analyze the following comparison results and generate a structured evaluation:
    
    COMPARISON DATA:
    {results}

    Using the data above, strictly generate structured feedback following JSON schema.

    Focus on:
    - assessing readiness
    - identifying the most important strengths and gaps
    - providing a prioritised, actionable improvement plan
    """

    system_instructions = """
    You are an expert software engineering career advisor.

    Your role is to analyse structured CV evaluation data and produce clear, honest, and actionable feedback for a graduate-level candidate.

    Only use the provided data. Do not assume skills, experience, or technologies not present in the input.
    
    You must:
    - Speak directly to them, as if it were a real, one-on-one interaction
    - Be specific and avoid generic advice
    - Prioritise the most important improvements
    - Explain WHY something matters in the industry
    - Provide realistic, step-by-step actions
    - Keep feedback concise but insightful

    Do NOT:
    - Repeat raw data
    - List everything - focus on the most impactful points
    - Be overly positive or vague
    - Use Em Dashes
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instructions,
            response_mime_type="application/json",
            response_schema=EvaluationSchema,
        ),
    )

    # Convert to Python Dictionary before returning
    return response.parsed.model_dump()
