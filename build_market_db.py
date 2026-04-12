"""
build_market_db.py — בונה מסד נתונים היסטורי ב-ChromaDB
הרץ פעם אחת: python build_market_db.py
(לא משתמש ב-pandas — עובד ישירות עם Yahoo Finance JSON)
"""
import chromadb
import requests
import ssl
import json
import time
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# עקוף SSL
ssl._create_default_https_context = ssl._create_unverified_context

# צור תיקיית data
Path("data").mkdir(exist_ok=True)

# אתחל ChromaDB מקומי
client = chromadb.PersistentClient(path="data/market_chroma_db")

print("Building Friday Historical Market Database...")
print("This will take a few minutes. Please wait...")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# ─────────────────────────────────────────────
# פונקציה: הורדת נתונים מYahoo Finance ישירות
# ─────────────────────────────────────────────
def download_ticker(symbol: str, name: str) -> dict:
    """מחזיר dict של {year: {open, close, high, low, count}}"""
    print(f"Downloading {name} ({symbol})...")
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {"interval": "1mo", "range": "max"}
        r = requests.get(url, params=params, headers=HEADERS, verify=False, timeout=20)
        data = r.json()

        result = data.get("chart", {}).get("result", [])
        if not result:
            print(f"  No data for {symbol}")
            return {}

        timestamps = result[0].get("timestamp", [])
        closes = result[0].get("indicators", {}).get("adjclose", [{}])[0].get("adjclose", [])
        quote = result[0].get("indicators", {}).get("quote", [{}])[0]
        highs = quote.get("high", [])
        lows = quote.get("low", [])

        # אגד לפי שנה
        yearly = defaultdict(lambda: {"closes": [], "highs": [], "lows": []})
        for i, ts in enumerate(timestamps):
            if ts is None:
                continue
            year = datetime.fromtimestamp(ts).year
            if i < len(closes) and closes[i] is not None:
                yearly[year]["closes"].append(closes[i])
            if i < len(highs) and highs[i] is not None:
                yearly[year]["highs"].append(highs[i])
            if i < len(lows) and lows[i] is not None:
                yearly[year]["lows"].append(lows[i])

        # המר לנתוני שנה
        annual = {}
        for year, vals in yearly.items():
            if len(vals["closes"]) < 3:
                continue
            annual[year] = {
                "open": vals["closes"][0],
                "close": vals["closes"][-1],
                "high": max(vals["highs"]) if vals["highs"] else vals["closes"][-1],
                "low": min(vals["lows"]) if vals["lows"] else vals["closes"][0],
                "count": len(vals["closes"])
            }

        years = sorted(annual.keys())
        if years:
            print(f"  Got {len(annual)} years from {years[0]} to {years[-1]}")
        return annual

    except Exception as e:
        print(f"  Error: {e}")
        return {}


# ─────────────────────────────────────────────
# פונקציה: יצירת סיכום שנתי טקסטואלי
# ─────────────────────────────────────────────
def create_yearly_summary(annual: dict, name: str, symbol: str) -> list:
    summaries = []

    for year, d in sorted(annual.items()):
        open_price = d["open"]
        close_price = d["close"]
        high = d["high"]
        low = d["low"]
        change_pct = ((close_price - open_price) / open_price * 100)

        direction = "עלה" if change_pct > 0 else "ירד"
        strength = "חזק" if abs(change_pct) > 20 else "מתון" if abs(change_pct) > 10 else "קל"

        text = (
            f"{name} בשנת {year}:\n"
            f"- {name} {direction} {abs(change_pct):.1f}% במהלך השנה ({strength})\n"
            f"- מחיר פתיחה: {open_price:.2f}, מחיר סגירה: {close_price:.2f}\n"
            f"- שיא שנתי: {high:.2f}, שפל שנתי: {low:.2f}\n"
            f"- טווח שנתי: {((high - low) / low * 100):.1f}%\n"
            f"- שנה: {year}, מדד: {name}, סמל: {symbol}"
        )

        summaries.append({
            "id": f"{symbol.replace('=', '_').replace('^', '')}_{year}",
            "text": text,
            "metadata": {
                "symbol": symbol,
                "name": name,
                "year": int(year),
                "change_pct": round(float(change_pct), 2),
                "open": round(float(open_price), 2),
                "close": round(float(close_price), 2),
                "high": round(float(high), 2),
                "low": round(float(low), 2),
            }
        })

    return summaries


# ─────────────────────────────────────────────
# Fear & Greed Index
# ─────────────────────────────────────────────
def download_fear_greed() -> list:
    print("Downloading Fear & Greed Index...")
    try:
        url = "https://api.alternative.me/fng/?limit=2000&format=json"
        r = requests.get(url, verify=False, timeout=15)
        data = r.json()

        summaries = []
        for item in data.get("data", []):
            date = datetime.fromtimestamp(int(item["timestamp"]))
            value = int(item["value"])
            classification = item["value_classification"]

            extreme_note = ""
            if value < 20:
                extreme_note = "\n- שוק בפחד קיצוני - הזדמנות קנייה היסטורית"
            elif value > 80:
                extreme_note = "\n- שוק בתאווה קיצונית - סכנת בועה"

            text = (
                f"Fear & Greed Index בתאריך {date.strftime('%Y-%m-%d')}:\n"
                f"- ערך: {value}/100\n"
                f"- סיווג: {classification}\n"
                f"- שנה: {date.year}, חודש: {date.month}"
                f"{extreme_note}"
            )

            summaries.append({
                "id": f"fear_greed_{item['timestamp']}",
                "text": text,
                "metadata": {
                    "type": "fear_greed",
                    "date": date.strftime('%Y-%m-%d'),
                    "year": date.year,
                    "value": value,
                    "classification": classification
                }
            })

        print(f"  Got {len(summaries)} Fear & Greed records")
        return summaries
    except Exception as e:
        print(f"  Error: {e}")
        return []


# ─────────────────────────────────────────────
# אירועים היסטוריים
# ─────────────────────────────────────────────
HISTORICAL_EVENTS = [
    {"year": 1929, "event": "קריסת וול סטריט — השפל הגדול. S&P 500 ירד 89% ב-3 שנים. אבטלה 25%. GDP ירד 30%. בנקים קרסו ברחבי ארה\"ב."},
    {"year": 1933, "event": "התאוששות מהשפל הגדול. Roosevelt's New Deal. שוק התחיל לעלות לאחר ירידה של 89%."},
    {"year": 1945, "event": "סוף מלחמת העולם השנייה. שוקי המניות עלו חזק. תחילת עידן הצמיחה הכלכלית."},
    {"year": 1950, "event": "מלחמת קוריאה. שוקי מניות ירדו זמנית ואז התאוששו."},
    {"year": 1962, "event": "משבר הטילים הקובני. שוק ירד 28% תוך חודשים. התאושש מהר."},
    {"year": 1971, "event": "ניקסון ביטל את הצמדת הדולר לזהב. תחילת עידן המטבעות הצפים."},
    {"year": 1973, "event": "משבר הנפט הערבי. אמברגו נפט. אינפלציה גבוהה. שוק ירד 48%."},
    {"year": 1979, "event": "אינפלציה 13% בארה\"ב. פול וולקר העלה ריבית ל-20%. שוק מניות קרס."},
    {"year": 1980, "event": "ריבית פד הגיעה ל-20%. זהב הגיע לשיא היסטורי. מיתון כלכלי."},
    {"year": 1982, "event": "תחילת שוק השוורים הגדול ביותר בהיסטוריה. ריבית ירדה. שוק עלה 15 שנה."},
    {"year": 1987, "event": "יום שני השחור — שוק קרס 22% ביום אחד. ההתאוששות הייתה מהירה."},
    {"year": 1990, "event": "מלחמת המפרץ הראשונה. מיתון קצר. שוק ירד 20% ואז התאושש."},
    {"year": 1995, "event": "תחילת בועת הדוטקום. אינטרנט ומניות טכנולוגיה עלו בצורה פרבולית."},
    {"year": 2000, "event": "פיצוץ בועת הדוטקום. נאסד\"ק ירד 78%. S&P ירד 49% ב-3 שנים."},
    {"year": 2001, "event": "פיגועי 11 ספטמבר. שוק נסגר שבוע. ירד 15% בפתיחה. מיתון."},
    {"year": 2003, "event": "מלחמת עיראק. תחילת ההתאוששות מהדוטקום. שוק עלה חזק."},
    {"year": 2007, "event": "תחילת משבר המשכנתאות הסאב-פריים. שוק נדל\"ן קרס. בנקים בסכנה."},
    {"year": 2008, "event": "קריסת ליהמן ברדרס. המשבר הפיננסי הגדול. שוק ירד 57%. ממשלות הצילו בנקים."},
    {"year": 2009, "event": "תחתית המשבר הפיננסי. Fed הוריד ריבית ל-0%. QE ראשון. שוק התחיל לעלות."},
    {"year": 2010, "event": "ביטקויין הגיע ל-$0.01 לראשונה. משבר חוב אירופאי. שוק התאושש."},
    {"year": 2013, "event": "ביטקויין קפץ מ-$13 ל-$1,200. שנת שוורים מרשימה ב-S&P 500."},
    {"year": 2015, "event": "סין הורידה שוקי מניות ברחבי העולם. Fed העלה ריבית לראשונה מאז 2008."},
    {"year": 2017, "event": "ביטקויין עלה מ-$1,000 ל-$20,000. שנת שוורים. Tax cuts בארה\"ב."},
    {"year": 2018, "event": "מלחמת סחר ארה\"ב-סין. ביטקויין קרס מ-$20K ל-$3K. שוק ירד 20%."},
    {"year": 2020, "event": "קורונה COVID-19. שוק קרס 34% ב-33 ימים — הירידה המהירה בהיסטוריה. Fed הדפיס טריליונים. שוק התאושש ועלה לשיאים."},
    {"year": 2021, "event": "GME short squeeze. ביטקויין שיא $69,000. אינפלציה מתחילה לעלות. שוקים בשיאים."},
    {"year": 2022, "event": "אינפלציה 9.1% בארה\"ב. Fed העלה ריבית מ-0% ל-4.5% בשנה אחת. נאסד\"ק ירד 33%. ביטקויין ירד 75%. משבר FTX."},
    {"year": 2023, "event": "AI boom — ChatGPT שינה הכל. Nvidia עלתה 240%. שוק התאושש חזק. אינפלציה ירדה."},
    {"year": 2024, "event": "ביטקויין שיא חדש $100,000. AI stocks בשיאים. Fed התחיל להוריד ריבית. Nvidia הגיעה לשווי $3 טריליון."},
]

# ─────────────────────────────────────────────
# בנה Collections
# ─────────────────────────────────────────────

# Collection 1: נתוני שוק שנתיים
print("\n=== Building Market Data Collection ===")
market_collection = client.get_or_create_collection(
    name="market_history",
    metadata={"description": "Historical market data by year"}
)

TICKERS = [
    ("^GSPC", "S&P 500"),
    ("^IXIC", "Nasdaq"),
    ("^DJI", "Dow Jones"),
    ("GC=F", "Gold"),
    ("SI=F", "Silver"),
    ("BTC-USD", "Bitcoin"),
    ("^VIX", "VIX Fear Index"),
    ("CL=F", "Oil"),
    ("TA125.TA", "Tel Aviv 125"),
]

all_summaries = []
for symbol, name in TICKERS:
    annual = download_ticker(symbol, name)
    if annual:
        summaries = create_yearly_summary(annual, name, symbol)
        all_summaries.extend(summaries)
    time.sleep(0.5)  # מנע חסימה מ-Yahoo

BATCH_SIZE = 50
for i in range(0, len(all_summaries), BATCH_SIZE):
    batch = all_summaries[i:i + BATCH_SIZE]
    market_collection.upsert(
        documents=[s["text"] for s in batch],
        ids=[s["id"] for s in batch],
        metadatas=[s["metadata"] for s in batch]
    )
    print(f"  Added batch {i // BATCH_SIZE + 1}/{(len(all_summaries) - 1) // BATCH_SIZE + 1}")

print(f"Market collection: {market_collection.count()} records")

# Collection 2: Fear & Greed
print("\n=== Building Fear & Greed Collection ===")
fg_collection = client.get_or_create_collection(
    name="fear_greed_history",
    metadata={"description": "Fear & Greed Index history"}
)

fg_summaries = download_fear_greed()
if fg_summaries:
    for i in range(0, len(fg_summaries), BATCH_SIZE):
        batch = fg_summaries[i:i + BATCH_SIZE]
        fg_collection.upsert(
            documents=[s["text"] for s in batch],
            ids=[s["id"] for s in batch],
            metadatas=[s["metadata"] for s in batch]
        )
    print(f"Fear & Greed collection: {fg_collection.count()} records")

# Collection 3: אירועים היסטוריים
print("\n=== Building Historical Events Collection ===")
events_collection = client.get_or_create_collection(
    name="historical_events",
    metadata={"description": "Major historical market events"}
)

events_collection.upsert(
    documents=[e["event"] for e in HISTORICAL_EVENTS],
    ids=[f"event_{e['year']}" for e in HISTORICAL_EVENTS],
    metadatas=[{"year": e["year"]} for e in HISTORICAL_EVENTS]
)
print(f"Historical events: {events_collection.count()} records")

print("\nDatabase built successfully!")
total = market_collection.count() + fg_collection.count() + events_collection.count()
print(f"Total records: {total}")
print("Location: data/market_chroma_db")
