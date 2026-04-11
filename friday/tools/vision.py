"""
vision.py — ניתוח צילום מסך עם Claude Vision
מצלם את המסך ומנתח גרפים/דשבורדים פיננסיים
"""
import base64
import io
import pyautogui
import anthropic

ANTHROPIC_CLIENT = None

def _get_client():
    global ANTHROPIC_CLIENT
    if ANTHROPIC_CLIENT is None:
        ANTHROPIC_CLIENT = anthropic.Anthropic()
    return ANTHROPIC_CLIENT

def register(mcp):
    @mcp.tool()
    async def analyze_dashboard_screenshot(question: str = "") -> str:
        """מצלם את המסך, שולח ל-Claude Vision ומחזיר ניתוח של הגרף המוצג"""

        # צילום מסך
        screenshot = pyautogui.screenshot()

        # המרה ל-base64
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        image_data = base64.standard_b64encode(buffer.getvalue()).decode('utf-8')

        # שליחה ל-Claude Vision
        client = _get_client()
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "You are a professional financial analyst. "
                            "Analyze this stock dashboard screenshot. Focus on: "
                            "1) Price trend and direction "
                            "2) Key support/resistance levels visible "
                            "3) Volume patterns "
                            "4) Technical indicators if visible "
                            "5) Overall market sentiment. "
                            f"Additional context from user: {question}. "
                            "Be concise and actionable."
                        )
                    }
                ],
            }]
        )
        return response.content[0].text
