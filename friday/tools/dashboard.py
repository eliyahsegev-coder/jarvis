"""
dashboard.py — פותח דשבורד מחולק ל-4 חלונות על מניה
"""
import webbrowser
import tempfile

def register(mcp):
    @mcp.tool()
    async def open_stock_dashboard(symbol: str, question: str = "") -> str:
        """פותח דשבורד מחולק ל-4 על מניה. symbol=סמל המניה (לדוגמה PLTR), question=שאלה על המניה"""

        symbol = symbol.upper()
        search_query = question.replace(" ", "+") if question else f"{symbol}+stock+analysis"
        news_query = f"{symbol}+stock"

        html = f"""<!DOCTYPE html>
<html lang="en">
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
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      flex: 1;
      gap: 3px;
      background: #1a1a2e;
      padding: 3px;
    }}
    .panel {{
      background: #0a0a0f;
      position: relative;
      border-radius: 4px;
      overflow: hidden;
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
    }}
    iframe {{
      width: 100%;
      height: 100%;
      border: none;
      display: block;
    }}
  </style>
</head>
<body>
  <header>
    <h1>FRIDAY</h1>
    <span class="badge">{symbol}</span>
    <span class="question">{question if question else f"Market Dashboard"}</span>
  </header>

  <div class="grid">
    <div class="panel">
      <div class="panel-label">📊 LIVE CHART</div>
      <iframe src="https://www.tradingview.com/widgetembed/?frameElementId=tv&symbol={symbol}&interval=D&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=0a0a0f&studies=RSI%40tv-basicstudies&theme=dark&style=1&timezone=exchange&withdateranges=1&showpopupbutton=1"></iframe>
    </div>

    <div class="panel">
      <div class="panel-label">📰 LATEST NEWS</div>
      <iframe src="https://news.google.com/search?q={news_query}&hl=en&gl=US&ceid=US:en"></iframe>
    </div>

    <div class="panel">
      <div class="panel-label">📈 TECHNICAL ANALYSIS</div>
      <iframe src="https://www.tradingview.com/widgetembed/?frameElementId=tv2&symbol={symbol}&interval=W&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=0a0a0f&studies=MACD%40tv-basicstudies%1EBB%40tv-basicstudies&theme=dark&style=1&timezone=exchange&withdateranges=1"></iframe>
    </div>

    <div class="panel">
      <div class="panel-label">🔍 ANALYSIS & REASONS</div>
      <iframe src="https://www.google.com/search?q={search_query}&igu=1"></iframe>
    </div>
  </div>
</body>
</html>"""

        # שמור קובץ זמני ופתח בדפדפן
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
        return f"Opened {symbol} dashboard — live chart, news, technical analysis, and search results for: '{question}'"
