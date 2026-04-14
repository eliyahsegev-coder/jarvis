# Graph Report - .  (2026-04-14)

## Corpus Check
- 26 files · ~9,062 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 107 nodes · 93 edges · 24 communities detected
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]

## God Nodes (most connected - your core abstractions)
1. `agent_friday.py` - 13 edges
2. `entrypoint()` - 7 edges
3. `FridayAgent` - 6 edges
4. `build_market_db.py` - 5 edges
5. `Friday — Business Advisor AI` - 5 edges
6. `vision.py` - 4 edges
7. `_client.py` - 4 edges
8. `dev()` - 3 edges
9. `Tool registry — imports and registers all tool modules with the MCP server.` - 3 edges
10. `dashboard.py` - 3 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Communities

### Community 0 - "Community 0"
Cohesion: 0.15
Nodes (16): Agent, _build_llm(), _build_stt(), _build_tts(), dev(), _endpointing_delay(), entrypoint(), FridayAgent (+8 more)

### Community 1 - "Community 1"
Cohesion: 0.18
Nodes (5): download_ticker(), build_market_db.py — בונה מסד נתונים היסטורי ב-ChromaDB הרץ פעם אחת: python buil, מחזיר dict של {year: {open, close, high, low, count}}, ChromaDB, _client.py — Shared singleton clients for the entire Friday tool system. Avoids

### Community 2 - "Community 2"
Cohesion: 0.25
Nodes (3): Tool registry — imports and registers all tool modules with the MCP server., Register all tool groups onto the MCP server instance., register_all_tools()

### Community 3 - "Community 3"
Cohesion: 0.29
Nodes (7): Alpha Vantage, Anthropic Claude Sonnet 4.6, FastMCP, Friday — Business Advisor AI, LiveKit Agents, MCP Server, OpenAI Whisper

### Community 4 - "Community 4"
Cohesion: 0.4
Nodes (3): _get_analysis(), dashboard.py — פותח דשבורד מניה: גרף רחב למעלה, ניתוח Claude + חיפוש למטה, שולף ניתוח קצר בעברית מ-Claude על המניה

### Community 5 - "Community 5"
Cohesion: 0.4
Nodes (3): fetch_and_parse_feed(), Web tools — search, fetch pages, and global news briefings., Helper function to handle a single feed request and parse its XML.

### Community 6 - "Community 6"
Cohesion: 0.4
Nodes (2): pyautogui, vision.py — ניתוח צילום מסך עם Claude Vision מצלם את המסך ומנתח גרפים/דשבורדים פ

### Community 7 - "Community 7"
Cohesion: 0.5
Nodes (1): macro.py — כלי מאקרו כלכלי יומי שולף נתוני שוק, מטבעות, ומדדים ומחזיר סיכום בעבר

### Community 8 - "Community 8"
Cohesion: 0.67
Nodes (1): Friday MCP Server — Entry Point Run with: python server.py

### Community 9 - "Community 9"
Cohesion: 0.67
Nodes (1): wake_word.py — מאזין ל-"Hey Friday" ברקע ומפעיל dispatch אוטומטי הרץ: uv run pyt

### Community 10 - "Community 10"
Cohesion: 0.67
Nodes (2): Config, Configuration — load environment variables and app-wide settings.

### Community 11 - "Community 11"
Cohesion: 0.67
Nodes (1): Reusable prompt templates registered with the MCP server.

### Community 12 - "Community 12"
Cohesion: 0.67
Nodes (1): Data resources — expose static content or dynamic data via MCP resources.

### Community 13 - "Community 13"
Cohesion: 0.67
Nodes (1): browser.py — שליטה בדפדפן: פתיחת אתרים ומקורות רלוונטיים

### Community 14 - "Community 14"
Cohesion: 0.67
Nodes (1): business.py — כלי ניתוח עסקי מנתח רעיונות ומצבים עסקיים בעברית באמצעות Claude

### Community 15 - "Community 15"
Cohesion: 0.67
Nodes (1): digest.py — דוח בוקר אוטומטי מחבר: מאקרו כלכלי + חדשות + המלצה עסקית יומית

### Community 16 - "Community 16"
Cohesion: 0.67
Nodes (1): explainer.py — ויזואליזציה אינטראקטיבית של אירועים היסטוריים בשוק פותח HTML בדפד

### Community 17 - "Community 17"
Cohesion: 0.67
Nodes (1): market_memory.py — חיפוש סמנטי בהיסטוריה של השוק

### Community 18 - "Community 18"
Cohesion: 0.67
Nodes (1): reports.py — כלי יצירת מצגות וסיכומים יוצר קבצי PPTX ודוחות טקסטואליים בעברית

### Community 19 - "Community 19"
Cohesion: 0.67
Nodes (1): System tools — time, environment info, shell commands, etc.

### Community 20 - "Community 20"
Cohesion: 0.67
Nodes (1): Utility tools — text processing, formatting, calculations, etc.

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (0): 

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (0): 

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): OpenAI TTS

## Knowledge Gaps
- **28 isolated node(s):** `FRIDAY – Voice Agent (MCP-powered) =================================== Iron Ma`, `Get the Windows host IP by looking at the default network route.`, `F.R.I.D.A.Y. – Iron Man-style voice assistant.     All tools are provided via t`, `Wrapper to run the agent in dev mode automatically.`, `build_market_db.py — בונה מסד נתונים היסטורי ב-ChromaDB הרץ פעם אחת: python buil` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 21`** (2 nodes): `main()`, `main.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `OpenAI TTS`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.