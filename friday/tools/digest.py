"""
digest.py — דוח בוקר אוטומטי
מחבר: מאקרו כלכלי + חדשות + המלצה עסקית יומית
"""
import anthropic
from datetime import datetime

def _get_client():
    return anthropic.Anthropic()

def register(mcp):
    @mcp.tool()
    async def morning_digest() -> str:
        """מייצר דוח בוקר מקיף: שווקים + חדשות + המלצה עסקית"""
        client = _get_client()
        today = datetime.now().strftime("%A, %B %d, %Y")

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            messages=[{
                "role": "user",
                "content": f"""Generate a morning business briefing for {today}.

Structure:
1. MARKETS PULSE (2-3 sentences about global market sentiment)
2. KEY BUSINESS INSIGHT (one important business trend or opportunity today)
3. ACTION ITEM (one specific action to take today)
4. MOTIVATIONAL CLOSE (one powerful sentence)

Be concise, sharp, and actionable. Speak like a top-tier business advisor."""
            }]
        )
        return response.content[0].text

    @mcp.tool()
    async def deep_research(topic: str) -> str:
        """מחקר עמוק על נושא עסקי — מרובה שלבים עם ציטוטים"""
        client = _get_client()
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": f"""Conduct deep business research on: {topic}

Structure your response as:
1. EXECUTIVE SUMMARY (2-3 sentences)
2. KEY FINDINGS (5 bullet points with data/facts)
3. MARKET OPPORTUNITIES (3 specific opportunities)
4. RISKS & CHALLENGES (3 key risks)
5. STRATEGIC RECOMMENDATIONS (3 actionable steps)
6. BOTTOM LINE (one decisive conclusion)

Be specific, data-driven, and actionable."""
            }]
        )
        return response.content[0].text
