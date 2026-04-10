"""
browser.py — שליטה בדפדפן: פתיחת אתרים ומקורות רלוונטיים
"""
import webbrowser
import urllib.parse

def register(mcp):
    @mcp.tool()
    async def open_website(url: str) -> str:
        """פותח אתר בדפדפן. url=כתובת האתר המלאה"""
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opened: {url}"

    @mcp.tool()
    async def search_google(query: str) -> str:
        """מחפש ב-Google ופותח תוצאות"""
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)
        return f"Opened Google search for: {query}"

    @mcp.tool()
    async def open_financial_site(site: str) -> str:
        """פותח אתרי פיננסים מובילים. site=שם האתר"""
        sites = {
            "bloomberg": "https://www.bloomberg.com",
            "reuters": "https://www.reuters.com",
            "cnbc": "https://www.cnbc.com",
            "investing": "https://www.investing.com",
            "tradingview": "https://www.tradingview.com",
            "tase": "https://www.tase.co.il",
            "calcalist": "https://www.calcalist.co.il",
            "ynet": "https://www.ynet.co.il/economy",
            "globes": "https://www.globes.co.il",
            "marketwatch": "https://www.marketwatch.com",
        }
        url = sites.get(site.lower(), f"https://www.google.com/search?q={site}")
        webbrowser.open(url)
        return f"Opened {site}: {url}"

    @mcp.tool()
    async def search_news(topic: str) -> str:
        """מחפש חדשות עדכניות על נושא ופותח Google News"""
        url = f"https://news.google.com/search?q={urllib.parse.quote(topic)}&hl=en"
        webbrowser.open(url)
        return f"Opened news search for: {topic}"
