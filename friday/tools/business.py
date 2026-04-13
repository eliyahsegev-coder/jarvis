"""
business.py — כלי ניתוח עסקי
מנתח רעיונות ומצבים עסקיים בעברית באמצעות Claude
"""
from friday.tools._client import get_anthropic_client


def register(mcp):
    @mcp.tool()
    async def analyze_business(description: str) -> str:
        """מנתח רעיון או מצב עסקי ומחזיר ניתוח SWOT והמלצות בעברית"""
        client = get_anthropic_client()
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""נתח את הדברים הבאים כיועץ עסקי בכיר. כתוב בעברית בלבד.

תיאור: {description}

כלול:
1. ניתוח SWOT (חוזקות, חולשות, הזדמנויות, איומים)
2. 3 סיכונים עיקריים
3. 3 המלצות אסטרטגיות
4. מסקנה קצרה

היה ממוקד ומעשי."""
            }]
        )
        return response.content[0].text

    @mcp.tool()
    async def daily_briefing() -> str:
        """מחזיר דוח בוקר עסקי: תובנה + המלצה אחת לפעולה"""
        client = get_anthropic_client()
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=250,
            messages=[{
                "role": "user",
                "content": """כתוב דוח בוקר עסקי קצר בעברית לבעל עסק קטן-בינוני בישראל.
כלול:
1. תובנה עסקית אחת חשובה לתחילת היום
2. המלצה אחת לפעולה מיידית
3. משפט מסכם מעורר השראה

היה תמציתי ומעשי."""
            }]
        )
        return response.content[0].text
