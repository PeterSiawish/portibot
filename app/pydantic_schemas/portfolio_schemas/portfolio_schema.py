from pydantic import BaseModel, Field


class PortfolioGenerationSchema(BaseModel):
    html_code: str = Field(
        description="""
    COMPLETE HTML DOCUMENT ONLY.
    Requirements:
    - Must start with <!DOCTYPE html>
    - Must contain <html>, <head>, and <body>
    - Must include <style> and <script> tags internally
    - Must be fully functional when opened in a browser
    - DO NOT include markdown (e.g. ```html)
    - DO NOT include explanations
    
    If the candidate profile was empty or sparse, the HTML must contain only placeholder content, no invented skills or experience.
    """
    )

    filename: str = Field(description="Format: 'firstname_portfolio.html'")
