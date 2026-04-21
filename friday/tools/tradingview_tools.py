"""
tradingview_tools.py — ניתוח שוק בזמן אמת דרך TradingView (ללא API key)
"""
import asyncio

try:
    from tradingview_mcp.server import (
        top_gainers,
        top_losers,
        analyze_coin,
        bollinger_scan,
        get_price,
        get_market_snapshot,
    )
    TRADINGVIEW_AVAILABLE = True
except ImportError:
    TRADINGVIEW_AVAILABLE = False
    print("⚠️  tradingview-mcp לא מותקן — tools שוק לא זמינים")


def register(mcp):

    @mcp.tool()
    async def analyze_asset(
        symbol: str,
        exchange: str = "BINANCE",
        timeframe: str = "1h"
    ) -> str:
        """ניתוח טכני מלא לנכס — קריפטו או מניה בזמן אמת.
        symbol=לדוגמה BTCUSDT / AAPL / MSFT,
        exchange=BINANCE/KUCOIN/BYBIT/NASDAQ/NYSE,
        timeframe=5m/15m/1h/4h/1D/1W"""
        if not TRADINGVIEW_AVAILABLE:
            return "שגיאה: ספריית TradingView לא מותקנת."

        try:
            data = await asyncio.to_thread(
                analyze_coin,
                symbol=symbol,
                exchange=exchange,
                timeframe=timeframe
            )

            if data.get("error"):
                return f"TradingView: {data['error']} ({symbol})"

            # תמיכה בשני פורמטים: indicators nested או flat
            ind  = data.get("indicators", data)
            rsi  = ind.get("RSI", "N/A")
            rsi_note = ""
            if isinstance(rsi, (int, float)):
                if rsi < 30:   rsi_note = " [oversold]"
                elif rsi > 70: rsi_note = " [overbought]"

            close  = ind.get("close", "N/A")
            change = data.get("changePercent", ind.get("change_pct", "N/A"))

            return (
                f"{symbol} | {exchange} | {timeframe}\n"
                f"---\n"
                f"מחיר: {close}\n"
                f"שינוי: {change}%\n"
                f"---\n"
                f"RSI (14): {rsi}{rsi_note}\n"
                f"MACD: {ind.get('MACD.macd', ind.get('macd', 'N/A'))}\n"
                f"BB עליון: {ind.get('BB_upper', ind.get('BB.upper', 'N/A'))}\n"
                f"BB תחתון: {ind.get('BB_lower', ind.get('BB.lower', 'N/A'))}\n"
                f"---\n"
                f"SMA 20: {ind.get('SMA20', 'N/A')}\n"
                f"EMA 50: {ind.get('EMA50', 'N/A')}\n"
                f"נפח: {ind.get('volume', 'N/A')}\n"
                f"לצרכי מחקר בלבד — אין המלצת השקעה"
            )
        except Exception as e:
            return f"שגיאה בשליפת נתונים עבור {symbol}: {e}"

    @mcp.tool()
    async def scan_market(
        scan_type: str = "gainers",
        exchange: str = "BINANCE",
        timeframe: str = "1h",
        limit: int = 10
    ) -> str:
        """סריקת שוק — מציאת העולים או היורדים הגדולים ביותר.
        scan_type=gainers/losers,
        exchange=BINANCE/KUCOIN/BYBIT/NASDAQ/NYSE,
        timeframe=5m/15m/1h/4h/1D,
        limit=כמות תוצאות"""
        if not TRADINGVIEW_AVAILABLE:
            return "שגיאה: ספריית TradingView לא מותקנת."

        try:
            if scan_type == "gainers":
                data = await asyncio.to_thread(
                    top_gainers, exchange=exchange, timeframe=timeframe, limit=limit
                )
                title = f"🚀 {limit} העולים הגדולים ביותר"
            else:
                data = await asyncio.to_thread(
                    top_losers, exchange=exchange, timeframe=timeframe, limit=limit
                )
                title = f"📉 {limit} היורדים הגדולים ביותר"

            if not data:
                return f"לא נמצאו תוצאות עבור {exchange} | {timeframe}"

            lines = [f"{title} | {exchange} | {timeframe}", "━" * 35]
            for i, item in enumerate(data, 1):
                symbol = item.get("symbol", item.get("name", "N/A"))
                change = item.get("changePercent", item.get("change_pct", 0))
                ind    = item.get("indicators", {})
                price  = ind.get("close", item.get("close", item.get("price", "N/A")))
                arrow  = "+" if float(change or 0) > 0 else "-"
                lines.append(f"{i}. [{arrow}] {symbol} | {float(change or 0):+.2f}% | {price}")

            lines.append("⚠️ לצרכי מחקר בלבד")
            return "\n".join(lines)
        except Exception as e:
            return f"שגיאה בסריקת שוק: {e}"

    @mcp.tool()
    async def scan_bollinger_squeeze(
        exchange: str = "BINANCE",
        timeframe: str = "1h",
        bbw_threshold: float = 0.05,
        limit: int = 10
    ) -> str:
        """מחפש נכסים עם Bollinger Band squeeze — לפני פריצה אפשרית.
        exchange=BINANCE/KUCOIN/BYBIT,
        timeframe=5m/15m/1h/4h,
        bbw_threshold=רוחב מקסימלי (0.05=צפוף מאוד)"""
        if not TRADINGVIEW_AVAILABLE:
            return "שגיאה: ספריית TradingView לא מותקנת."

        try:
            data = await asyncio.to_thread(
                bollinger_scan,
                exchange=exchange,
                timeframe=timeframe,
                bbw_threshold=bbw_threshold,
                limit=limit
            )

            if not data:
                return f"לא נמצאו נכסים עם squeeze ב-{exchange} | {timeframe} | BBW≤{bbw_threshold}"

            lines = [
                f"🎯 Bollinger Squeeze | {exchange} | {timeframe}",
                f"BBW מקסימלי: {bbw_threshold}",
                "━" * 35
            ]
            for i, item in enumerate(data, 1):
                symbol = item.get("name", item.get("symbol", "N/A"))
                bbw    = item.get("BBW", item.get("bbw", "N/A"))
                try:
                    bbw_fmt = f"{float(bbw):.4f}"
                except Exception:
                    bbw_fmt = str(bbw)
                lines.append(f"{i}. {symbol} | BBW: {bbw_fmt}")

            lines.append("⚠️ לצרכי מחקר בלבד")
            return "\n".join(lines)
        except Exception as e:
            return f"שגיאה בסריקת Bollinger: {e}"

    @mcp.tool()
    async def get_live_price(symbol: str) -> str:
        """שולף מחיר חי לנכס בודד.
        symbol=לדוגמה BTCUSDT / ETHUSDT / AAPL"""
        if not TRADINGVIEW_AVAILABLE:
            return "שגיאה: ספריית TradingView לא מותקנת."

        try:
            data = await asyncio.to_thread(get_price, symbol=symbol)
            if not data:
                return f"לא נמצא מחיר עבור {symbol}"
            price  = data.get("price", data.get("close", "N/A"))
            change = data.get("change_pct", data.get("change", "N/A"))
            return f"{symbol}: ${price}  ({change}%)"
        except Exception as e:
            return f"שגיאה בשליפת מחיר {symbol}: {e}"

    @mcp.tool()
    async def market_snapshot() -> str:
        """תמונת שוק כללית — מדדים עיקריים בזמן אמת"""
        if not TRADINGVIEW_AVAILABLE:
            return "שגיאה: ספריית TradingView לא מותקנת."

        try:
            data = await asyncio.to_thread(get_market_snapshot)
            if not data:
                return "לא ניתן לשלוף snapshot כרגע"
            lines = ["📊 Market Snapshot", "━" * 30]
            for k, v in data.items():
                lines.append(f"{k}: {v}")
            lines.append("⚠️ לצרכי מחקר בלבד")
            return "\n".join(lines)
        except Exception as e:
            return f"שגיאה ב-market snapshot: {e}"
