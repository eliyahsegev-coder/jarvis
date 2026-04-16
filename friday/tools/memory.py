"""
memory.py — זיכרון אישי מתמיד לפריידי
שומר ומשלף מידע אישי בין שיחות
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from friday.tools._client import get_anthropic_client

DB_PATH = Path(__file__).parent.parent.parent / "data" / "friday_memory.db"


def _get_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def register(mcp):

    @mcp.tool()
    async def remember(category: str, content: str) -> str:
        """שומר מידע בזיכרון האישי של פריידי.
        category=קטגוריה (decisions/stocks/meetings/preferences/facts),
        content=התוכן לשמירה"""
        conn = _get_db()
        now = datetime.now().isoformat()
        conn.execute(
            "INSERT INTO memories (category, content, created_at, updated_at) VALUES (?,?,?,?)",
            (category, content, now, now)
        )
        conn.commit()
        conn.close()
        return f"Remembered: [{category}] {content}"

    @mcp.tool()
    async def recall(query: str = "", category: str = "") -> str:
        """שולף זיכרונות רלוונטיים.
        query=מה לחפש, category=קטגוריה ספציפית (אופציונלי)"""
        conn = _get_db()
        if category:
            rows = conn.execute(
                "SELECT category, content, created_at FROM memories WHERE category=? ORDER BY updated_at DESC LIMIT 20",
                (category,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT category, content, created_at FROM memories ORDER BY updated_at DESC LIMIT 30"
            ).fetchall()
        conn.close()

        if not rows:
            return "No memories found."

        if query:
            client = get_anthropic_client()
            memories_text = "\n".join([f"[{r[0]}] {r[1]} ({r[2][:10]})" for r in rows])
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=400,
                messages=[{
                    "role": "user",
                    "content": f"From these memories, find what's relevant to: '{query}'\n\n{memories_text}\n\nReturn only relevant items, concisely."
                }]
            )
            return response.content[0].text

        return "\n".join([f"[{r[0]}] {r[1]} ({r[2][:10]})" for r in rows])

    @mcp.tool()
    async def forget(memory_id: int) -> str:
        """מוחק זיכרון לפי ID"""
        conn = _get_db()
        conn.execute("DELETE FROM memories WHERE id=?", (memory_id,))
        conn.commit()
        conn.close()
        return f"Memory {memory_id} deleted."

    @mcp.tool()
    async def memory_summary() -> str:
        """מחזיר סיכום של כל מה שפריידי זוכר עלייך"""
        conn = _get_db()
        rows = conn.execute(
            "SELECT category, COUNT(*) as count FROM memories GROUP BY category"
        ).fetchall()
        recent = conn.execute(
            "SELECT category, content FROM memories ORDER BY updated_at DESC LIMIT 5"
        ).fetchall()
        conn.close()

        if not rows:
            return "No memories yet, boss. Start talking and I'll remember everything."

        stats = "\n".join([f"- {r[0]}: {r[1]} items" for r in rows])
        recent_text = "\n".join([f"- [{r[0]}] {r[1]}" for r in recent])

        return f"Memory Summary:\n{stats}\n\nMost Recent:\n{recent_text}"
