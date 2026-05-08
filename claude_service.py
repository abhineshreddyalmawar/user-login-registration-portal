import anthropic
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Initialize Anthropic client
client = anthropic.Anthropic(
    api_key=os.environ.get('ANTHROPIC_API_KEY')
)

def analyze_repo(repo_name, description="", language=""):
    """
    Real Claude Haiku analysis of GitHub repository
    """
    try:
        prompt = f"""Analyze this GitHub repository and provide a structured assessment.

Repository: {repo_name}
Description: {description or 'No description provided'}
Primary Language: {language or 'Unknown'}

Provide analysis in this EXACT JSON format with no other text:
{{
    "category": "one of: DEVOPS, WEB, DATA, INFRASTRUCTURE, SECURITY, MOBILE, AI/ML",
    "rating": <number between 1.0 and 10.0>,
    "rating_label": "one of: Excellent, Very Good, Good, Fair, Needs Work",
    "tech_stack": ["tech1", "tech2", "tech3", "tech4"],
    "highlights": [
        "specific strength 1",
        "specific strength 2", 
        "specific strength 3"
    ],
    "suggestions": [
        "specific improvement 1",
        "specific improvement 2"
    ]
}}

Base your analysis on:
- Repository name and description
- Primary programming language
- Common patterns in this type of project
- Industry best practices

Return ONLY the JSON object, no other text."""

        message = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse response
        response_text = message.content[0].text.strip()

        # Clean JSON if needed
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]

        result = json.loads(response_text)

        # Add metadata
        result['repo_name'] = repo_name
        result['analyzed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result['model'] = 'claude-haiku-4-5'

        return result

    except Exception as e:
        # Fallback to basic analysis if API fails
        return {
            "repo_name": repo_name,
            "category": detect_category_basic(repo_name, description),
            "rating": 6.5,
            "rating_label": "Fair",
            "tech_stack": [language] if language else ["Unknown"],
            "highlights": [
                "Repository identified successfully",
                "Basic analysis completed",
                "Manual review recommended"
            ],
            "suggestions": [
                "Add detailed README",
                "Include project description"
            ],
            "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": "fallback",
            "error": str(e)
        }


def detect_category_basic(repo_name, description=""):
    """Basic category detection as fallback"""
    text = (repo_name + " " + description).lower()

    if any(w in text for w in ["ci", "cd", "deploy", "pipeline", "patch"]):
        return "DEVOPS"
    elif any(w in text for w in ["flask", "django", "react", "portal", "web"]):
        return "WEB"
    elif any(w in text for w in ["data", "analytics", "ml", "ai", "etl"]):
        return "DATA"
    elif any(w in text for w in ["iac", "terraform", "cloud", "aws"]):
        return "INFRASTRUCTURE"
    elif any(w in text for w in ["security", "auth", "encrypt"]):
        return "SECURITY"
    else:
        return "DEVOPS"