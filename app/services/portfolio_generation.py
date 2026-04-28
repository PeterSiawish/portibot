from google.genai import types
from app.pydantic_schemas.portfolio_schemas.portfolio_schema import (
    PortfolioGenerationSchema,
)


system_instructions = """
You are a Senior Web Designer specializing in Developer Portfolios.

Your goal is to generate a high-quality, production-ready portfolio website.

STRICT RULES:
1. Output ONLY valid JSON (no markdown, no explanations)
2. Follow the schema EXACTLY
3. The HTML must be complete and functional
4. Do NOT use Em Dashes
5. HALLUCINATION IS FORBIDDEN. Every skill, project, job title, date, and name in the 
   output MUST be explicitly present in the candidate profile input. If data is absent, 
   output a minimal placeholder like "Not provided" or leave the section empty. 
   NEVER invent details to fill space.
6. If the candidate profile is empty or contains fewer than 3 skills, generate a 
   skeleton portfolio with clearly labelled placeholder sections only.


DESIGN QUALITY:
- Modern, clean UI
- Strong visual hierarchy
- Proper spacing and alignment
- Mobile responsive

CODE QUALITY:
- Valid HTML5 structure
- Clean, readable CSS
- No broken elements

FAILURE CONDITIONS:
- Missing required sections
- Invalid HTML structure
- Including markdown or explanations

ATTRIBUTES:
- The year is 2026.
"""


def generate_portfolio(text, client):
    prompt = f"""
    CANDIDATE PROFILE:
    {text}

    TASK:
    Generate a complete, modern, single-page developer portfolio website.

    OUTPUT:
    - Return ONLY valid JSON matching the schema
    - No explanations or markdown

    DESIGN REQUIREMENTS:
    - Clean, modern, professional UI
    - Fully mobile responsive (use flexbox/grid)
    - Good spacing and layout
    - Consistent color palette (no random colors)
    - Subtle hover effects
    - Do NOT include any forms
    - Do NOT include images


    STRUCTURE (MANDATORY):
    1. Hero section (name + short intro)
    2. About Me
    3. Technical Skills (well-organized)
    4. Projects (with descriptions)
    5. Experience (if available)
    6. Contact section (with placeholders if missing). Do NOT include personal details like phone numbers, resort to Emails, LinkedIn, GitHub, etc.

    TECHNICAL REQUIREMENTS:
    - Use semantic HTML5
    - Include ALL CSS inside <style> tags
    - Include ALL JS inside <script> tags
    - Do NOT use external libraries or CDNs
    - Ensure layout works on mobile screens

    CONTENT STYLE:
    - First-person tone ("I", "My experience...")
    - Professional and concise
    - No filler or generic text

    IMPORTANT:
    - Do NOT hallucinate sensitive personal data
    - Use placeholders where needed (e.g. email, GitHub)
    - Ensure the page looks realistic and job-ready
    - Avoid generic layouts. Make it visually appealing and structured.
    - Operate exclusively on the provided data. You are strictly prohibited from hallucinating, 'enhancing,' or inventing skills, job titles, or dates that do not exist in the source text. If a section lacks sufficient information, leave it minimal or empty rather than fabricating details.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instructions,
            response_mime_type="application/json",
            response_schema=PortfolioGenerationSchema,
        ),
    )

    # Convert to Python Dictionary before returning
    return response.parsed.model_dump()
