"""
vision.py — ניתוח צילום מסך עם Claude Vision
מצלם את חלון האפליקציה (Electron) או את כל המסך כגיבוי
"""
import base64
import io
from friday.tools._client import get_anthropic_client


def _capture_screen() -> bytes:
    """Capture screen: try Electron app window first, fallback to pyautogui."""
    # Try Electron Command Center first (best quality, app-specific)
    try:
        import urllib.request
        with urllib.request.urlopen('http://127.0.0.1:9001/screenshot', timeout=2) as r:
            if r.status == 200:
                return r.read()
    except Exception:
        pass

    # Fallback: full desktop screenshot via pyautogui
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        buf = io.BytesIO()
        screenshot.save(buf, format='PNG')
        return buf.getvalue()
    except Exception as e:
        raise RuntimeError(f"Could not capture screen: {e}")


def register(mcp):
    @mcp.tool()
    async def analyze_dashboard_screenshot(question: str = "") -> str:
        """מצלם את מסך האפליקציה ומנתח אותו עם Claude Vision.
        קורא אוטומטית כשצריך לראות מה מוצג על המסך."""

        png_bytes = _capture_screen()
        image_data = base64.standard_b64encode(png_bytes).decode('utf-8')

        client = get_anthropic_client()
        prompt = (
            "You are a professional financial analyst looking at the user's screen. "
            "Describe exactly what you see: charts, prices, data, UI elements. "
            "Then provide your analysis: trends, key levels, signals, actionable insights. "
        )
        if question:
            prompt += f"The user specifically asked: {question}. Address this directly."
        else:
            prompt += "Give a concise but complete analysis of everything visible."

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
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
                    {"type": "text", "text": prompt}
                ],
            }]
        )
        return response.content[0].text

    @mcp.tool()
    async def watch_screen() -> str:
        """מצלם את המסך ומחזיר תיאור מלא של מה שמוצג כרגע — קרא אוטומטית לפני כל תשובה שקשורה למה שהמשתמש רואה."""

        png_bytes = _capture_screen()
        image_data = base64.standard_b64encode(png_bytes).decode('utf-8')

        client = get_anthropic_client()
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
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
                            "Describe what you see on this screen in 2-3 sentences. "
                            "Focus on: what app/content is visible, any numbers or data shown, "
                            "and the current state. Be brief and factual."
                        )
                    }
                ],
            }]
        )
        return response.content[0].text
