# Friday — Business Advisor AI

> *A Jarvis-level AI business advisor running on your personal device.*

Friday is a voice-powered AI assistant that gives you real-time market data, business analysis, presentations, and browser control — all hands-free.

---

## How it works

```
Microphone ──► STT (OpenAI Whisper)
                    │
                    ▼
             LLM (Claude Sonnet 4.6)  ◄──────► MCP Server (FastMCP / SSE)
                    │                              ├─ macro       (market data)
                    ▼                              ├─ business    (SWOT analysis)
             TTS (OpenAI onyx)                     ├─ reports     (PPTX generator)
                    │                              ├─ browser     (open websites)
                    ▼                              ├─ digest      (morning briefing)
             Speaker / LiveKit room                └─ web         (news & search)
```

---

## Quick Start

### Option A — One click (recommended)

```bat
double-click start_friday.bat
```

Starts LiveKit Server, MCP Server, and the Voice Agent automatically, then opens a dispatch to connect.

### Option B — Manual (3 terminals)

**Terminal 1 — LiveKit Server**
```powershell
cd C:\claude\jarvis\friday-tony-stark-demo\livekit
.\livekit-server.exe --dev
```

**Terminal 2 — MCP Server**
```powershell
cd C:\claude\jarvis\friday-tony-stark-demo
uv run friday
```

**Terminal 3 — Voice Agent**
```powershell
cd C:\claude\jarvis\friday-tony-stark-demo
uv run friday_voice
```

### Connect via Playground

1. Open https://agents-playground.livekit.io
2. Enter:
   - **LiveKit URL:** `ws://localhost:7880`
   - **API Key:** `devkey`
   - **API Secret:** `secret`
3. Click **Connect** → click the microphone → talk to Friday

---

## Tools

| Module | Tools | What it does |
|--------|-------|-------------|
| `macro.py` | `get_macro_summary` | Real-time market data: S&P 500, Nasdaq, Dow Jones, oil, gold, USD/ILS via Alpha Vantage |
| `business.py` | `analyze_business`, `daily_briefing` | SWOT analysis, risks, strategic recommendations |
| `reports.py` | `generate_presentation`, `generate_summary_doc` | Creates PPTX presentations and auto-opens them |
| `browser.py` | `open_website`, `search_google`, `open_financial_site`, `search_news` | Opens Bloomberg, Reuters, CNBC, TradingView, Google News, and more |
| `digest.py` | `morning_digest`, `deep_research` | Daily briefing with markets + insights + action items; deep multi-step business research |
| `web.py` | `get_world_news`, `fetch_url`, `open_world_monitor` | Live RSS headlines from BBC, CNBC, NYT, Al Jazeera |

---

## Example Voice Commands

- *"Give me the morning briefing"*
- *"What are the markets doing today?"*
- *"Analyze my SaaS business idea"*
- *"Open Bloomberg"*
- *"Search for news about AI regulation"*
- *"Make a presentation about our Q2 strategy"*
- *"Research the EV market"*

---

## Project Structure

```
friday-tony-stark-demo/
├── start_friday.bat        ← one-click launch (all systems)
├── setup_startup.bat       ← add Friday to Windows startup
├── wake_word.py            ← "Hey Friday" wake word listener
├── server.py               ← MCP server entry point
├── agent_friday.py         ← LiveKit voice agent
├── pyproject.toml
├── .env.example
│
├── friday/
│   └── tools/
│       ├── macro.py        ← market data (Alpha Vantage)
│       ├── business.py     ← SWOT & business analysis
│       ├── reports.py      ← PPTX presentations
│       ├── browser.py      ← browser control
│       ├── digest.py       ← morning briefing & research
│       └── web.py          ← news & web fetch
│
└── livekit/
    ├── livekit-server.exe  ← local LiveKit server (download separately)
    ├── lk.exe              ← LiveKit CLI
    └── start_livekit.bat
```

> **Note:** `livekit-server.exe` and `lk.exe` are not tracked in git (too large).
> Download from [livekit/livekit releases](https://github.com/livekit/livekit/releases) and place in `livekit/`.

---

## Environment Variables

Copy `.env.example` → `.env` and fill in:

| Variable | Required | Where to get it |
|----------|----------|----------------|
| `LIVEKIT_URL` | ✅ | `ws://localhost:7880` (local dev) |
| `LIVEKIT_API_KEY` | ✅ | `devkey` (local dev) |
| `LIVEKIT_API_SECRET` | ✅ | `secret` (local dev) |
| `OPENAI_API_KEY` | ✅ | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) — used for STT (Whisper) and TTS |
| `ANTHROPIC_API_KEY` | ✅ | [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) — used for LLM (Claude Sonnet) and all business tools |
| `ALPHA_VANTAGE_API_KEY` | ✅ | [alphavantage.co](https://www.alphavantage.co/support/#api-key) — free tier: 25 req/day |
| `GOOGLE_API_KEY` | optional | [aistudio.google.com](https://aistudio.google.com/projects) — only if switching LLM to Gemini |
| `PORCUPINE_ACCESS_KEY` | optional | [console.picovoice.ai](https://console.picovoice.ai/) — free, for wake word activation |

---

## Wake Word (Optional)

To activate Friday hands-free with a voice command:

1. Get a free key at https://console.picovoice.ai/
2. Add `PORCUPINE_ACCESS_KEY=your_key` to `.env`
3. Run: `uv run python wake_word.py`

---

## Add to Windows Startup

To have Friday start automatically when Windows boots:

```bat
double-click setup_startup.bat
```

---

## Tech Stack

- **[LiveKit Agents](https://github.com/livekit/agents)** — real-time voice pipeline
- **OpenAI Whisper** — STT (strong multilingual support)
- **Anthropic Claude Sonnet 4.6** — LLM
- **OpenAI TTS** (`onyx` voice) — TTS
- **[FastMCP](https://github.com/jlowin/fastmcp)** — MCP server framework
- **Alpha Vantage** — real-time market data
- **[uv](https://github.com/astral-sh/uv)** — Python package manager

---

## License

MIT
