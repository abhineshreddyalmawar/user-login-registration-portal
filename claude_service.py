import random
from datetime import datetime

# ── Category mapping based on keywords ──
CATEGORIES = {
    "devops": ["ci", "cd", "deploy", "docker", 
               "kubernetes", "pipeline", "patch",
               "ansible", "terraform", "aws"],
    "web": ["flask", "django", "react", "portal",
            "login", "registration", "html", "css"],
    "data": ["data", "analytics", "ml", "ai",
             "model", "notebook", "analysis"],
    "infrastructure": ["iac", "cloud", "formation",
                      "cloudwatch", "grafana", "monitor"],
    "security": ["auth", "security", "password",
                 "encrypt", "vault", "ssl"]
}

# ── Tech stack mapping ──
TECH_STACKS = {
    "devops": ["Python", "Bash", "YAML", "Jenkins",
               "GitHub Actions", "Docker"],
    "web": ["Python", "Flask", "HTML5", "CSS3",
            "SQLite", "JavaScript"],
    "data": ["Python", "Pandas", "NumPy",
             "Jupyter", "Matplotlib"],
    "infrastructure": ["Terraform", "AWS CloudFormation",
                      "Grafana", "CloudWatch"],
    "security": ["Python", "JWT", "OAuth2",
                "Werkzeug", "SSL/TLS"]
}

# ── Highlights per category ──
HIGHLIGHTS = {
    "devops": [
        "Implements automated CI/CD pipeline",
        "Uses infrastructure as code principles",
        "Follows DevOps best practices",
        "Includes automated testing stages",
        "Supports multi-environment deployment"
    ],
    "web": [
        "Clean MVC architecture",
        "Secure authentication system",
        "Responsive UI design",
        "RESTful API endpoints",
        "Database integration"
    ],
    "data": [
        "Efficient data processing pipeline",
        "Clear data visualization",
        "Modular analysis structure",
        "Reproducible results",
        "Well-documented methodology"
    ],
    "infrastructure": [
        "Scalable cloud architecture",
        "Monitoring and alerting setup",
        "Cost-optimized resources",
        "High availability design",
        "Infrastructure as code"
    ],
    "security": [
        "Implements security best practices",
        "Proper credential management",
        "Secure communication protocols",
        "Access control mechanisms",
        "Audit logging capabilities"
    ]
}

# ── Suggestions per category ──
SUGGESTIONS = {
    "devops": [
        "Add automated rollback mechanism",
        "Include performance benchmarking",
        "Add Slack/email notifications",
        "Implement blue-green deployment",
        "Add container health checks"
    ],
    "web": [
        "Add API rate limiting",
        "Implement Redis caching",
        "Add unit and integration tests",
        "Implement OAuth2 login",
        "Add API documentation"
    ],
    "data": [
        "Add data validation layer",
        "Implement model versioning",
        "Add performance metrics",
        "Include data lineage tracking",
        "Add automated reporting"
    ],
    "infrastructure": [
        "Add disaster recovery plan",
        "Implement auto-scaling",
        "Add cost monitoring alerts",
        "Include security scanning",
        "Add compliance checks"
    ],
    "security": [
        "Add multi-factor authentication",
        "Implement session timeout",
        "Add brute force protection",
        "Include security audit logs",
        "Add penetration testing"
    ]
}


def detect_category(repo_name, description=""):
    """Detect repo category from name and description"""
    text = (repo_name + " " + description).lower()

    scores = {}
    for category, keywords in CATEGORIES.items():
        score = sum(1 for kw in keywords if kw in text)
        scores[category] = score

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "devops"


def calculate_rating(repo_name, description=""):
    """Calculate a realistic rating based on repo details"""
    base = 6.0

    # Bonus for having description
    if description and len(description) > 20:
        base += 0.5

    # Bonus for keywords
    positive = ["ci", "cd", "automated", "secure",
                "test", "docker", "deploy", "monitor"]
    text = (repo_name + " " + description).lower()
    bonus = sum(0.2 for kw in positive if kw in text)

    rating = min(9.5, base + bonus)
    return round(rating, 1)


def analyze_repo(repo_name, description="", language=""):
    """
    Mock Claude analysis of a GitHub repository
    In future: replace with real Anthropic API call
    """
    # Detect category
    category = detect_category(repo_name, description)

    # Calculate rating
    rating = calculate_rating(repo_name, description)

    # Get tech stack
    tech_stack = TECH_STACKS.get(category, ["Python"])
    if language and language not in tech_stack:
        tech_stack = [language] + tech_stack[:3]

    # Pick highlights (3 random)
    highlights = random.sample(
        HIGHLIGHTS.get(category, HIGHLIGHTS["devops"]), 3
    )

    # Pick suggestions (2 random)
    suggestions = random.sample(
        SUGGESTIONS.get(category, SUGGESTIONS["devops"]), 2
    )

    # Build analysis result
    return {
        "repo_name": repo_name,
        "category": category.upper(),
        "rating": rating,
        "rating_label": get_rating_label(rating),
        "tech_stack": tech_stack[:4],
        "highlights": highlights,
        "suggestions": suggestions,
        "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model": "claude-mock-v1"
    }


def get_rating_label(rating):
    """Convert rating to label"""
    if rating >= 9:
        return "Excellent"
    elif rating >= 8:
        return "Very Good"
    elif rating >= 7:
        return "Good"
    elif rating >= 6:
        return "Fair"
    else:
        return "Needs Work"