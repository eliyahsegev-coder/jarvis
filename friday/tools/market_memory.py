"""
market_memory.py — חיפוש סמנטי בהיסטוריה של השוק
"""
from friday.tools._client import get_anthropic_client, get_chroma_collections


def register(mcp):
    @mcp.tool()
    async def query_market_history(question: str, n_results: int = 5) -> str:
        """מחפש בהיסטוריה של 100 שנות שוק הון ומחזיר תקופות דומות.
        question=שאלה בעברית או אנגלית על השוק"""
        try:
            cols = get_chroma_collections()

            market_results = cols["market"].query(query_texts=[question], n_results=n_results)
            events_results = cols["events"].query(query_texts=[question], n_results=3)
            fg_results     = cols["fear_greed"].query(query_texts=[question], n_results=3)

            context_parts = []

            if market_results["documents"][0]:
                context_parts.append("נתוני שוק רלוונטיים:")
                for doc in market_results["documents"][0]:
                    context_parts.append(f"- {doc}")

            if events_results["documents"][0]:
                context_parts.append("\nאירועים היסטוריים דומים:")
                for doc in events_results["documents"][0]:
                    context_parts.append(f"- {doc}")

            if fg_results["documents"][0]:
                context_parts.append("\nFear & Greed היסטורי:")
                for doc in fg_results["documents"][0][:2]:
                    context_parts.append(f"- {doc}")

            context = "\n".join(context_parts)

            client = get_anthropic_client()
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": f"""Based on this historical market data, answer the question concisely and insightfully.

Question: {question}

Historical Data Found:
{context}

Provide:
1. Direct answer to the question
2. Historical parallels (if relevant)
3. Key insight or pattern
4. Actionable takeaway for today

Be concise, sharp, and use specific data points."""
                }]
            )

            return response.content[0].text

        except Exception as e:
            return f"Database error: {e}. Make sure to run build_market_db.py first."

    @mcp.tool()
    async def find_similar_periods(description: str) -> str:
        """מוצא תקופות היסטוריות דומות למצב הנוכחי.
        description=תיאור המצב הנוכחי"""
        try:
            cols = get_chroma_collections()

            results = cols["market"].query(query_texts=[description], n_results=5)
            events  = cols["events"].query(query_texts=[description], n_results=3)

            docs  = results["documents"][0] + events["documents"][0]
            metas = results["metadatas"][0]
            years = [m.get("year") for m in metas if "year" in m]
            context = "\n".join(docs)

            client = get_anthropic_client()
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=400,
                messages=[{
                    "role": "user",
                    "content": f"""Find historical parallels to this market situation:

Current situation: {description}

Similar historical periods found: {years}

Historical data:
{context}

Compare:
1. How similar are these periods? (percentage similarity)
2. What happened NEXT in each similar period?
3. Average outcome after similar situations
4. Key differences from today
5. Most likely scenario based on history"""
                }]
            )

            return f"Similar historical periods: {years}\n\n{response.content[0].text}"

        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    async def get_asset_history(symbol: str, start_year: int = 2000) -> str:
        """מחזיר היסטוריה של נכס מסוים משנה מסוימת.
        symbol=סמל הנכס, start_year=שנת התחלה"""
        try:
            cols = get_chroma_collections()

            results = cols["market"].query(
                query_texts=[f"{symbol} performance history"],
                n_results=30,
                where={"year": {"$gte": start_year}}
            )

            if not results["documents"][0]:
                return f"No data found for {symbol} from {start_year}"

            metas = results["metadatas"][0]
            years_data = sorted(metas, key=lambda x: x.get("year", 0))

            summary = f"Historical data for {symbol} from {start_year}:\n\n"
            for m in years_data:
                if m.get("symbol", "").upper() == symbol.upper():
                    change = m.get("change_pct", 0)
                    arrow = "↑" if change > 0 else "↓"
                    summary += f"{m.get('year')}: {arrow}{abs(change):.1f}%\n"

            if len(summary) > 60:
                return summary

            return "\n".join(results["documents"][0])

        except Exception as e:
            return f"Error: {e}"
