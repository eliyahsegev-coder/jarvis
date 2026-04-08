"""
macro.py — כלי מאקרו כלכלי יומי
שולף נתוני שוק, מטבעות, ומדדים ומחזיר סיכום בעברית
"""
import yfinance as yf
import anthropic

ANTHROPIC_CLIENT = None

def _get_client():
    global ANTHROPIC_CLIENT
    if ANTHROPIC_CLIENT is None:
        ANTHROPIC_CLIENT = anthropic.Anthropic()
    return ANTHROPIC_CLIENT

def _fetch_market_data() -> dict:
    tickers = {
        "S&P 500": "^GSPC",
        "נאסד\"ק": "^IXIC",
        "דאו ג'ונס": "^DJI",
        "שקל/דולר": "ILS=X",
        "נפט גולמי": "CL=F",
        "זהב": "GC=F",
        "ת\"א 125": "TA125.TA",
    }
    data = {}
    for name, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                prev = hist["Close"].iloc[-2]
                curr = hist["Close"].iloc[-1]
                change_pct = ((curr - prev) / prev) * 100
                data[name] = {"value": round(curr, 2), "change": round(change_pct, 2)}
        except Exception:
            data[name] = {"value": "N/A", "change": 0}
    return data

def register(mcp):
    @mcp.tool()
    async def get_macro_summary() -> str:
        """שולף סיכום מאקרו כלכלי יומי: מדדים, שקל/דולר, נפט, זהב"""
        market_data = _fetch_market_data()

        lines = []
        for name, d in market_data.items():
            if d["value"] != "N/A":
                arrow = "↑" if d["change"] > 0 else "↓"
                lines.append(f"{name}: {d['value']} ({arrow}{abs(d['change'])}%)")
            else:
                lines.append(f"{name}: לא זמין")

        raw = "\n".join(lines)

        client = _get_client()
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": f"בהתבסס על הנתונים הבאים, כתוב סיכום מאקרו כלכלי קצר ומקצועי בעברית (3-4 משפטים):\n{raw}"
            }]
        )
        return response.content[0].text
