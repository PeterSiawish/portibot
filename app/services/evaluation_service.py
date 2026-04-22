from google.genai import types
from app.pydantic_schemas.evaluation_schemas.role_evaluation import EvaluationSchema
from app.pydantic_schemas.evaluation_schemas.auto_evaluation import AutoEvaluationSchema


system_instructions = """
    You are an expert software engineering career advisor.

    Your role is to analyse structured CV evaluation data and produce clear, honest, and actionable feedback for a graduate-level candidate.

    Only use the provided data. Do not assume skills, experience, or technologies not present in the input.
    
    You must:
    - Greet them briefly and speak directly to them, as if it were a real, one-on-one interaction
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


def evaluate_role(results, client):
    prompt = f"""
    You are a Senior Software Engineer and Technical Recruiter. 
    You are evaluating a graduate for a specific role.

    Analyze the following comparison results and generate a structured evaluation:
    
    COMPARISON DATA:
    {results}

    Focus on:
    - assessing readiness
    - identifying the most important strengths and gaps
    - providing a prioritised, actionable improvement plan

    Your goal is to be a "Brutally Honest Mentor." 
    - Don't sugarcoat the gaps; explain them in terms of "Hiring Risk."
    - Use industry-standard terminology (e.g., "Technical Debt," "Scalability," "CI/CD Pipeline").
    - When suggesting the 'bridge_project', make it something they can actually finish in a weekend.

    Return the response strictly following the JSON schema.
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


def evaluate_auto(results, client):
    prompt = f"""
    ANALYSIS TASK: 
    Examine the provided Match Data for the top 4 different software engineering roles. 
    Construct a comprehensive career roadmap for the candidate.

    MATCH DATA:
    {results}
    
    CRITICAL REQUIREMENTS:
    - Use a professional, encouraging, yet blunt 'mentor' tone.
    - Be extremely specific about technology stacks.
    - In 'technical_archetype', be creative but accurate.
    - For 'effort_level', be realistic based on the 'primary_blocker'.

    Return the response strictly following the JSON schema.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instructions,
            response_mime_type="application/json",
            response_schema=AutoEvaluationSchema,
        ),
    )

    # Convert to Python Dictionary before returning
    return response.parsed.model_dump()
