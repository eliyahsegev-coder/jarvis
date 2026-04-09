"""
macro.py — כלי מאקרו כלכלי יומי
שולף נתוני שוק, מטבעות, ומדדים ומחזיר סיכום בעברית
"""
import os
import httpx
import anthropic

ANTHROPIC_CLIENT = None

def _get_client():
    global ANTHROPIC_CLIENT
    if ANTHROPIC_CLIENT is None:
        ANTHROPIC_CLIENT = anthropic.Anthropic()
    return ANTHROPIC_CLIENT

def _fetch_market_data() -> dict:
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")

    tickers = {
        "S&P 500":      {"type": "quote",    "symbol": "SPY"},
        'נאסד"ק':       {"type": "quote",    "symbol": "QQQ"},
        "דאו ג'ונס":    {"type": "quote",    "symbol": "DIA"},
        "נפט גולמי":    {"type": "quote",    "symbol": "CL=F"},
        "זהב":          {"type": "quote",    "symbol": "GLD"},
        'ת"א 125':      {"type": "quote",    "symbol": "TA125.TA"},
        "שקל/דולר":     {"type": "fx",       "symbol": "USD/ILS"},
    }

    data = {}

    with httpx.Client(verify=False, timeout=10) as client:
        for name, cfg in tickers.items():
            try:
                if cfg["type"] == "fx":
                    url = (
                        f"https://www.alphavantage.co/query"
                        f"?function=CURRENCY_EXCHANGE_RATE"
                        f"&from_currency=USD&to_currency=ILS"
                        f"&apikey={api_key}"
                    )
                    resp = client.get(url).json()
                    rate = resp["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
                    data[name] = {"value": round(float(rate), 4), "change": 0}
                else:
                    url = (
                        f"https://www.alphavantage.co/query"
                        f"?function=GLOBAL_QUOTE"
                        f"&symbol={cfg['symbol']}"
                        f"&apikey={api_key}"
                    )
                    resp = client.get(url).json()
                    quote = resp["Global Quote"]
                    price = float(quote["05. price"])
                    change_pct = quote["10. change percent"].replace("%", "")
                    data[name] = {"value": round(price, 2), "change": round(float(change_pct), 2)}
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
