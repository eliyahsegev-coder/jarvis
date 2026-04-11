"""
dashboard.py — פותח דשבורד מניה: גרף רחב למעלה, ניתוח Claude + חיפוש למטה
"""
import webbrowser
import tempfile
import anthropic
import json
import datetime
from pathlib import Path

ANTHROPIC_CLIENT = None

def _get_client():
    global ANTHROPIC_CLIENT
    if ANTHROPIC_CLIENT is None:
        ANTHROPIC_CLIENT = anthropic.Anthropic()
    return ANTHROPIC_CLIENT

def _get_analysis(symbol: str, question: str) -> str:
    """שולף ניתוח קצר בעברית מ-Claude על המניה"""
    client = _get_client()
    prompt = f"נתח את המניה {symbol} בעברית בצורה קצרה ומקצועית."
    if question:
        prompt += f" שאלה ספציפית: {question}"
    prompt += """

כלול:
- מה קורה עם המניה כרגע
- למה היא עולה / יורדת
- המלצה קצרה (קנה / מכור / המתן)

3-4 משפטים בלבד. היה תמציתי ומעשי."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"ניתוח לא זמין כרגע: {e}"

def register(mcp):
    @mcp.tool()
    async def open_stock_dashboard(symbol: str, question: str = "") -> str:
        """פותח דשבורד מניה: גרף חי רחב למעלה, ניתוח Claude בעברית + Google למטה"""

        symbol = symbol.upper()
        search_query = question.replace(" ", "+") if question else f"{symbol}+stock+analysis+reasons"

        # שולף ניתוח Claude לפני בניית ה-HTML
        analysis = _get_analysis(symbol, question)
        # בריחה מתווים שעלולים לשבור HTML
        analysis_html = analysis.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

        html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8"/>
  <title>FRIDAY — {symbol}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      background: #0a0a0f;
      color: #e0e0e0;
      font-family: 'Segoe UI', sans-serif;
      height: 100vh;
      display: flex;
      flex-direction: column;
    }}
    header {{
      background: #0f0f1a;
      border-bottom: 1px solid #1a1a2e;
      padding: 8px 20px;
      display: flex;
      align-items: center;
      gap: 12px;
      flex-shrink: 0;
      direction: ltr;
    }}
    header h1 {{ color: #00d4ff; font-size: 1rem; letter-spacing: 3px; }}
    .badge {{
      background: #00d4ff;
      color: #0a0a0f;
      padding: 2px 10px;
      border-radius: 4px;
      font-weight: bold;
      font-size: 0.9rem;
    }}
    .question {{ color: #666; font-size: 0.8rem; flex: 1; font-style: italic; }}
    .grid {{
      display: grid;
      grid-template-rows: 60% 40%;
      flex: 1;
      gap: 3px;
      background: #1a1a2e;
      padding: 3px;
      overflow: hidden;
    }}
    .panel {{
      background: #0a0a0f;
      position: relative;
      border-radius: 4px;
      overflow: hidden;
    }}
    .bottom-row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 3px;
    }}
    .panel-label {{
      position: absolute;
      top: 6px;
      left: 10px;
      font-size: 0.6rem;
      color: #00d4ff;
      letter-spacing: 1.5px;
      z-index: 10;
      background: rgba(10,10,15,0.85);
      padding: 2px 7px;
      border-radius: 3px;
      pointer-events: none;
      direction: ltr;
    }}
    iframe {{
      width: 100%;
      height: 100%;
      border: none;
      display: block;
    }}
    .analysis-panel {{
      padding: 32px 20px 16px;
      overflow-y: auto;
      line-height: 1.7;
      font-size: 0.92rem;
      color: #cce8ff;
      direction: rtl;
    }}
    .analysis-panel .symbol-title {{
      font-size: 1.1rem;
      color: #00d4ff;
      font-weight: bold;
      margin-bottom: 12px;
      direction: ltr;
    }}
    .analysis-panel .body-text {{
      color: #b0c8e0;
      font-size: 0.88rem;
    }}
    .analysis-panel::-webkit-scrollbar {{ width: 4px; }}
    .analysis-panel::-webkit-scrollbar-thumb {{ background: #1a1a2e; border-radius: 2px; }}
  </style>
</head>
<body>
  <header>
    <h1>FRIDAY</h1>
    <span class="badge">{symbol}</span>
    <span class="question">{question if question else "Market Dashboard"}</span>
  </header>

  <div class="grid">

    <!-- שורה עליונה: גרף רחב -->
    <div class="panel">
      <div class="panel-label">📊 LIVE CHART — {symbol}</div>
      <iframe src="https://www.tradingview.com/widgetembed/?frameElementId=tv&symbol={symbol}&interval=D&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=0a0a0f&studies=RSI%40tv-basicstudies%1EMACD%40tv-basicstudies&theme=dark&style=1&timezone=exchange&withdateranges=1&showpopupbutton=1"></iframe>
    </div>

    <!-- שורה תחתונה: ניתוח + גוגל -->
    <div class="bottom-row">

      <div class="panel">
        <div class="panel-label">🤖 FRIDAY ANALYSIS</div>
        <div class="analysis-panel">
          <div class="symbol-title">ניתוח {symbol}</div>
          <div class="body-text">{analysis_html}</div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-label">🔍 ANALYSIS &amp; REASONS</div>
        <iframe src="https://www.google.com/search?q={search_query}&igu=1"></iframe>
      </div>

    </div>
  </div>
</body>
</html>"""

        tmp = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.html',
            delete=False,
            prefix=f'friday_{symbol}_',
            encoding='utf-8'
        )
        tmp.write(html)
        tmp.close()
        webbrowser.open(f'file:///{tmp.name}')

        # שמור נתוני הדשבורד ל-JSON
        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        dashboard_data = {
            "symbol": symbol,
            "question": question,
            "timestamp": datetime.datetime.now().isoformat(),
            "analysis": analysis
        }
        (data_dir / f"{symbol}_dashboard.json").write_text(
            json.dumps(dashboard_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        return f"Opened {symbol} dashboard with Claude analysis in Hebrew."

    @mcp.tool()
    async def get_dashboard_data(symbol: str) -> str:
        """מחזיר את הנתונים שנשמרו מהדשבורד האחרון של מניה. symbol=סמל המניה"""
        data_dir = Path(__file__).parent.parent.parent / "data"
        data_file = data_dir / f"{symbol.upper()}_dashboard.json"

        if not data_file.exists():
            return f"No dashboard data found for {symbol.upper()}. Open a dashboard first."

        data = json.loads(data_file.read_text(encoding='utf-8'))
        return f"""Last dashboard for {data['symbol']} ({data['timestamp']}):
Question: {data['question']}
Analysis: {data['analysis']}"""
