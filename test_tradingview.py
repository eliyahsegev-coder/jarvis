"""
test_tradingview.py — בדיקת אינטגרציית TradingView
הרץ: python test_tradingview.py
"""
import asyncio
from tradingview_mcp.server import (
    top_gainers,
    top_losers,
    analyze_coin,
    bollinger_scan,
    get_price,
    get_market_snapshot,
)


async def test():
    print("=== TradingView Integration Test ===\n")

    # 1. gainers
    print("1. בודק top gainers (KUCOIN / 1h)...")
    try:
        gainers = await asyncio.to_thread(top_gainers, exchange="KUCOIN", timeframe="1h", limit=5)
        print(f"   ✅ קיבלתי {len(gainers)} תוצאות")
        if gainers:
            g = gainers[0]
            print(f"   דוגמה: {g}")
    except Exception as e:
        print(f"   ❌ שגיאה: {e}")

    # 2. analyze coin
    print("\n2. בודק ניתוח BTC (BINANCE / 1h)...")
    try:
        btc = await asyncio.to_thread(analyze_coin, symbol="BTCUSDT", exchange="BINANCE", timeframe="1h")
        print(f"   ✅ RSI: {btc.get('RSI', 'N/A')} | מחיר: {btc.get('close', 'N/A')}")
    except Exception as e:
        print(f"   ❌ שגיאה: {e}")

    # 3. live price
    print("\n3. בודק מחיר חי BTCUSDT...")
    try:
        price = await asyncio.to_thread(get_price, symbol="BTCUSDT")
        print(f"   ✅ {price}")
    except Exception as e:
        print(f"   ❌ שגיאה: {e}")

    # 4. bollinger squeeze
    print("\n4. בודק Bollinger squeeze (KUCOIN / 4h)...")
    try:
        bb = await asyncio.to_thread(bollinger_scan, exchange="KUCOIN", timeframe="4h", bbw_threshold=0.05, limit=5)
        print(f"   ✅ נמצאו {len(bb)} נכסים עם squeeze")
        if bb:
            print(f"   דוגמה: {bb[0]}")
    except Exception as e:
        print(f"   ❌ שגיאה: {e}")

    # 5. market snapshot
    print("\n5. בודק market snapshot...")
    try:
        snap = await asyncio.to_thread(get_market_snapshot)
        keys = list(snap.keys())[:5] if snap else []
        print(f"   ✅ מפתחות: {keys}")
    except Exception as e:
        print(f"   ❌ שגיאה: {e}")

    print("\n=== סיום בדיקות ===")


if __name__ == "__main__":
    asyncio.run(test())
