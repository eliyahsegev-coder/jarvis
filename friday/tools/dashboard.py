"""
dashboard.py — פותח דשבורד מניה: גרף רחב למעלה, ניתוח Claude + חדשות למטה
"""
import tempfile
import json
import datetime
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from friday.tools._client import get_anthropic_client, show_in_app


def _fetch_news_html(symbol: str, question: str) -> str:
    """שולף חדשות מ-Yahoo Finance RSS ומחזיר HTML מעוצב."""
    query = question if question else symbol
    urls = [
        f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US",
        f"https://news.google.com/rss/search?q={query}+stock&hl=en-US&gl=US&ceid=US:en",
    ]

    items = []
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as r:
                tree = ET.parse(r)
                root = tree.getroot()
                for item in root.iter("item"):
                    title = item.findtext("title", "").strip()
                    link  = item.findtext("link", "#").strip()
                    pub   = item.findtext("pubDate", "").strip()[:16]
                    desc  = item.findtext("description", "").strip()
                    # strip HTML tags from description
                    import re
                    desc = re.sub(r"<[^>]+>", "", desc)[:140]
                    if title:
                        items.append({"title": title, "link": link, "pub": pub, "desc": desc})
            if len(items) >= 8:
                break
        except Exception:
            continue

    if not items:
        return '<div style="color:#666;padding:20px;font-size:0.85rem;">No news available right now.</div>'

    cards = ""
    for item in items[:10]:
        title = item["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        desc  = item["desc"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        cards += f"""
        <a class="news-card" href="{item['link']}" target="_blank">
          <div class="news-title">{title}</div>
          <div class="news-desc">{desc}</div>
          <div class="news-time">{item['pub']}</div>
        </a>"""

    return f"""
    <style>
      .news-feed {{ overflow-y: auto; height: 100%; padding: 8px; display: flex; flex-direction: column; gap: 6px; }}
      .news-card {{ display: block; background: #12121e; border: 1px solid #1e1e30; border-radius: 7px;
                   padding: 10px 12px; text-decoration: none; color: inherit; transition: border-color .2s; }}
      .news-card:hover {{ border-color: #00d4ff44; }}
      .news-title {{ font-size: 0.82rem; color: #dde; line-height: 1.4; margin-bottom: 4px; }}
      .news-desc  {{ font-size: 0.72rem; color: #778; line-height: 1.3; margin-bottom: 4px; }}
      .news-time  {{ font-size: 0.62rem; color: #445; letter-spacing: .5px; }}
    </style>
    <div class="news-feed">{cards}</div>"""


def _get_analysis(symbol: str, question: str) -> str:
    """שולף ניתוח קצר בעברית מ-Claude על המניה"""
    client = get_anthropic_client()
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
        # תגובה מיידית לפני הבנייה
        immediate = f"Opening {symbol} dashboard, boss. Give me a second..."

        analysis = _get_analysis(symbol, question)
        analysis_html = analysis.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        news_html = _fetch_news_html(symbol, question)

        html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8"/>
  <title>SACHBAK — {symbol}</title>
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
    <h1>SACHBAK</h1>
    <span class="badge">{symbol}</span>
    <span class="question">{question if question else "Market Dashboard"}</span>
  </header>

  <div class="grid">

    <div class="panel">
      <div class="panel-label">LIVE CHART — {symbol}</div>
      <iframe src="https://www.tradingview.com/widgetembed/?frameElementId=tv&symbol={symbol}&interval=D&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=0a0a0f&studies=RSI%40tv-basicstudies%1EMACD%40tv-basicstudies&theme=dark&style=1&timezone=exchange&withdateranges=1&showpopupbutton=1"></iframe>
    </div>

    <div class="bottom-row">

      <div class="panel">
        <div class="panel-label">SACHBAK ANALYSIS</div>
        <div class="analysis-panel">
          <div class="symbol-title">ניתוח {symbol}</div>
          <div class="body-text">{analysis_html}</div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-label">LATEST NEWS — {symbol}</div>
        {news_html}
      </div>

    </div>
  </div>
</body>
</html>"""

        tmp = tempfile.NamedTemporaryFile(
            mode='w', suffix='.html', delete=False,
            prefix=f'SACHBAK_{symbol}_', encoding='utf-8'
        )
        tmp.write(html)
        tmp.close()
        show_in_app(tmp.name, f"STOCK DASHBOARD — {symbol}")

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

