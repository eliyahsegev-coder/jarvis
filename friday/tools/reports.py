"""
reports.py — כלי יצירת מצגות וסיכומים
יוצר קבצי PPTX ודוחות טקסטואליים בעברית
"""
import anthropic
from pptx import Presentation
from pptx.util import Inches, Pt
import os

ANTHROPIC_CLIENT = None

def _get_client():
    global ANTHROPIC_CLIENT
    if ANTHROPIC_CLIENT is None:
        ANTHROPIC_CLIENT = anthropic.Anthropic()
    return ANTHROPIC_CLIENT

def register(mcp):
    @mcp.tool()
    async def generate_presentation(topic: str, points: str, output_path: str = "presentation.pptx") -> str:
        """יוצר מצגת PPTX בעברית. topic=נושא, points=נקודות עיקריות מופרדות בפסיק"""
        client = _get_client()

        # בקש מ-Claude לפרק לשקפים
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""צור מבנה מצגת עסקית בעברית על הנושא: {topic}
נקודות עיקריות: {points}

החזר JSON בפורמט הבא בלבד (ללא טקסט נוסף):
{{
  "title": "כותרת המצגת",
  "slides": [
    {{"title": "כותרת שקף", "bullets": ["נקודה 1", "נקודה 2", "נקודה 3"]}},
    ...
  ]
}}

צור 5-6 שקפים מקצועיים."""
            }]
        )

        import json
        raw = response.content[0].text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)

        # בנה את ה-PPTX
        prs = Presentation()
        prs.slide_width = Inches(13.33)
        prs.slide_height = Inches(7.5)

        # שקף כותרת
        title_slide = prs.slides.add_slide(prs.slide_layouts[0])
        title_slide.shapes.title.text = data["title"]
        title_slide.shapes.title.text_frame.paragraphs[0].runs[0].font.size = Pt(36)
        title_slide.shapes.title.text_frame.paragraphs[0].runs[0].font.bold = True

        # שקפי תוכן
        for slide_data in data["slides"]:
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = slide_data["title"]
            tf = slide.placeholders[1].text_frame
            tf.clear()
            for i, bullet in enumerate(slide_data["bullets"]):
                p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
                p.text = bullet
                p.level = 0

        prs.save(output_path)
        import subprocess
        subprocess.Popen(
            ['powershell', '-c', f'Start-Process "{os.path.abspath(output_path)}"'],
            shell=True
        )
        return f"Presentation created and opened: {os.path.abspath(output_path)} ({len(data['slides'])} slides)"

    @mcp.tool()
    async def generate_summary_doc(text: str) -> str:
        """מסכם טקסט ארוך לדוח עסקי מסודר בעברית"""
        client = _get_client()
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{
                "role": "user",
                "content": f"""סכם את הטקסט הבא לדוח עסקי מסודר בעברית:

{text}

פורמט הסיכום:
- נושא מרכזי
- נקודות מפתח (3-5)
- מסקנות
- המלצות לפעולה"""
            }]
        )
        return response.content[0].text
