import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def build_html_email(analysis_data, subject):
    """Build beautiful HTML email for recruiter"""
    
    # Calculate rankings
    ranked = []
    for username, repos in analysis_data.items():
        ratings = [r['rating'] for r in repos.values()]
        avg = round(sum(ratings) / len(ratings), 1) if ratings else 0
        categories = [r['category'] for r in repos.values()]
        top_category = max(set(categories), key=categories.count) if categories else 'N/A'
        top_repos = sorted(repos.items(), 
                          key=lambda x: x[1]['rating'], 
                          reverse=True)[:3]
        ranked.append({
            'username': username,
            'avg': avg,
            'top_category': top_category,
            'top_repos': top_repos,
            'total_repos': len(repos)
        })
    
    ranked.sort(key=lambda x: x['avg'], reverse=True)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; 
                   background: #f4f6f8; margin: 0; padding: 20px; }}
            .container {{ max-width: 680px; margin: 0 auto; 
                         background: white; border-radius: 12px;
                         overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #0a0a1a, #1a1a3a);
                      padding: 32px; text-align: center; }}
            .header h1 {{ color: #00c896; font-size: 22px; margin: 0 0 8px; }}
            .header p {{ color: #7a9ab0; font-size: 12px; margin: 0; }}
            .section {{ padding: 24px 32px; border-bottom: 1px solid #eef0f3; }}
            .section-title {{ font-size: 13px; font-weight: 700; 
                             color: #333; letter-spacing: 0.08em;
                             text-transform: uppercase; margin-bottom: 16px; }}
            .recommendation {{ background: #fffbf0; border: 1px solid #ffd700;
                              border-radius: 10px; padding: 20px; }}
            .candidate-row {{ display: flex; align-items: center;
                             padding: 12px 16px; border-radius: 8px;
                             margin-bottom: 8px; }}
            .top-candidate {{ background: #fff9e6; 
                             border: 1px solid #ffd700; }}
            .runner-up {{ background: #f8f9fa;
                         border: 1px solid #e0e0e0; }}
            .medal {{ font-size: 24px; margin-right: 12px; }}
            .candidate-info {{ flex: 1; }}
            .candidate-name {{ font-size: 15px; font-weight: 700; color: #333; }}
            .candidate-meta {{ font-size: 11px; color: #888; margin-top: 2px; }}
            .score {{ font-size: 20px; font-weight: 800; color: #f59e0b; }}
            .top-badge {{ background: #f59e0b; color: white;
                         font-size: 10px; padding: 2px 8px;
                         border-radius: 4px; font-weight: 700;
                         display: block; margin-top: 4px; text-align: center; }}
            .summary-grid {{ display: flex; gap: 16px; }}
            .summary-card {{ flex: 1; background: #f8f9fa;
                            border: 1px solid #e0e0e0;
                            border-radius: 8px; padding: 16px; }}
            .summary-card.top {{ border-color: #ffd700; background: #fffbf0; }}
            .summary-username {{ font-size: 14px; font-weight: 700; 
                                color: #00c896; margin-bottom: 8px; }}
            .summary-avg {{ font-size: 20px; font-weight: 800; 
                           color: #f59e0b; float: right; margin-top: -24px; }}
            .summary-detail {{ font-size: 11px; color: #888; margin-bottom: 4px; }}
            .repo-item {{ background: #f8f9fa; border: 1px solid #e0e0e0;
                         border-radius: 8px; padding: 14px; margin-bottom: 10px; }}
            .repo-header {{ display: flex; justify-content: space-between;
                           align-items: center; margin-bottom: 6px; }}
            .repo-name {{ font-size: 13px; font-weight: 700; color: #333; }}
            .repo-score {{ font-size: 13px; font-weight: 700; color: #f59e0b; }}
            .repo-meta {{ font-size: 11px; color: #888; margin-bottom: 6px; }}
            .highlight {{ color: #00c896; font-size: 11px; margin-bottom: 3px; }}
            .suggestion {{ color: #f59e0b; font-size: 11px; }}
            .footer {{ background: #0a0a1a; padding: 20px; 
                      text-align: center; color: #4a6070; font-size: 11px; }}
            .divider {{ height: 1px; background: #eef0f3; margin: 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- HEADER -->
            <div class="header">
                <h1>🤖 NexusAI Portal</h1>
                <p>Candidate GitHub Analysis Report · Powered by Claude AI</p>
                <p style="margin-top:8px; color:#4a6070;">
                    {len(ranked)} candidate(s) analyzed
                </p>
            </div>

            <!-- RECOMMENDATION -->
            <div class="section">
                <div class="section-title">🏆 Recommendation</div>
                <div class="recommendation">
    """

    for i, r in enumerate(ranked):
        medal = ['🥇', '🥈', '🥉'][i] if i < 3 else '▪'
        css_class = 'top-candidate' if i == 0 else 'runner-up'
        html += f"""
                    <div class="candidate-row {css_class}">
                        <span class="medal">{medal}</span>
                        <div class="candidate-info">
                            <div class="candidate-name">@{r['username']}</div>
                            <div class="candidate-meta">
                                {r['top_category']} Expert · 
                                {r['total_repos']} repos analyzed
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div class="score">{r['avg']}/10</div>
                            {'<span class="top-badge">TOP CANDIDATE</span>' if i == 0 else ''}
                        </div>
                    </div>
        """

    html += """
                </div>
            </div>

            <!-- CANDIDATE SUMMARIES -->
            <div class="section">
                <div class="section-title">👤 Candidate Summaries</div>
                <div class="summary-grid">
    """

    for i, r in enumerate(ranked):
        css_class = 'top' if i == 0 else ''
        html += f"""
                    <div class="summary-card {css_class}">
                        <div class="summary-username">@{r['username']}</div>
                        <div class="summary-avg">{r['avg']}/10</div>
                        <div class="summary-detail">Primary: {r['top_category']}</div>
                        <div class="summary-detail">Repos: {r['total_repos']}</div>
                        <div class="summary-detail">
                            Best: {r['top_repos'][0][0] if r['top_repos'] else 'N/A'}
                        </div>
                    </div>
        """

    html += """
                </div>
            </div>

            <!-- TOP 3 REPOS -->
            <div class="section">
                <div class="section-title">📊 Top 3 Repos Per Candidate</div>
    """

    for r in ranked:
        html += f"""
                <div style="margin-bottom:20px;">
                    <div style="font-size:13px; font-weight:700; 
                        color:#333; margin-bottom:10px; 
                        padding-bottom:6px; border-bottom:2px solid #00c896;">
                        @{r['username']}
                    </div>
        """
        for repo_name, data in r['top_repos']:
            html += f"""
                    <div class="repo-item">
                        <div class="repo-header">
                            <span class="repo-name">📦 {repo_name}</span>
                            <span class="repo-score">{data['rating']}/10</span>
                        </div>
                        <div class="repo-meta">
                            {data['category']} · {data['rating_label']} · 
                            {', '.join(data['tech_stack'][:3])}
                        </div>
                        <div class="highlight">→ {data['highlights'][0]}</div>
                        <div class="suggestion">💡 {data['suggestions'][0]}</div>
                    </div>
            """
        html += "</div>"

    html += f"""
            </div>

            <!-- FOOTER -->
            <div class="footer">
                <p>Generated by NexusAI Portal · Claude AI Analysis</p>
                <p style="margin-top:4px; color:#2a3a4a;">
                    This report was automatically generated based on 
                    GitHub repository analysis
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def send_email(to_email, subject, analysis_data):
    """Send email via Gmail SMTP"""
    
    gmail_user = os.environ.get('GMAIL_USER', '')
    gmail_password = os.environ.get('GMAIL_APP_PASSWORD', '')

    if not gmail_user or not gmail_password:
        return False, "Gmail credentials not configured"

    try:
        html_content = build_html_email(analysis_data, subject)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = gmail_user
        msg['To'] = to_email

        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, to_email, msg.as_string())

        return True, "Email sent successfully!"

    except Exception as e:
        return False, str(e)