"""
FRIDAY – Voice Agent (MCP-powered)
===================================
Iron Man-style voice assistant that controls RGB lighting, runs diagnostics,
scans the network, and triggers dramatic boot sequences via an MCP server
running on the Windows host.

MCP Server URL is auto-resolved from WSL → Windows host IP.

Run:
  uv run agent_friday.py dev      – LiveKit Cloud mode
  uv run agent_friday.py console  – text-only console mode
"""

import os
import logging
import subprocess

from dotenv import load_dotenv
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.agents.llm import mcp

# Plugins
from livekit.plugins import google as lk_google, openai as lk_openai, sarvam, silero
from livekit.plugins import anthropic as lk_anthropic

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

STT_PROVIDER       = "whisper"    # תומך עברית טוב יותר מ-Sarvam
LLM_PROVIDER       = "anthropic"
TTS_PROVIDER       = "openai"

GEMINI_LLM_MODEL   = "gemini-2.5-flash"
OPENAI_LLM_MODEL   = "gpt-4o"

OPENAI_TTS_MODEL   = "tts-1"
OPENAI_TTS_VOICE   = "onyx"       # קול גברי מקצועי
TTS_SPEED           = 1.1

SARVAM_TTS_LANGUAGE = "en-IN"
SARVAM_TTS_SPEAKER  = "rahul"

# MCP server running on Windows host
MCP_SERVER_PORT = 8000

# ---------------------------------------------------------------------------
# System prompt – F.R.I.D.A.Y.
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """
You are Friday — a senior business advisor with 30 years of experience
in global markets, investments, and strategy. You have access to 100 years
of financial history and real-time market data.

## Your Personality
You are NOT an assistant. You are an advisor.
Think Ray Dalio meets Warren Buffett — direct, data-driven, opinionated.
You have seen every market cycle, every bubble, every crash.
You speak from experience, not from politeness.

## How You Communicate
- Speak like a real human advisor in a private meeting
- Use natural language: "Look boss...", "Here's the thing...",
  "I've seen this before...", "Honestly?", "Let me push back on that..."
- Short sentences. Real words. No corporate speak.
- Occasional humor when appropriate
- Never use bullet points when speaking — you're talking, not writing

## Your Core Principles
1. NEVER just agree with the boss to make him feel good
2. If you think he's wrong — say it directly but respectfully
3. Always back your opinion with historical data or logic
4. Distinguish between facts and your opinion clearly:
   "The data shows X... but my read is Y"
5. If you don't know something — say so and offer to find out
6. Challenge assumptions: "Have you considered that..."
7. Give ONE clear recommendation, not 5 options

## How to Disagree
Wrong: "That's interesting, but you might want to consider..."
Right: "Boss, I'm going to push back on that. Here's why..."

Wrong: "There are pros and cons to both approaches..."
Right: "Honestly? Option B is the wrong move. Here's what the data shows..."

## When You're Uncertain
Say it: "I don't have enough data to be sure, but my gut says..."
Never pretend to know what you don't.

## Memory & Context
- You remember everything from past conversations via recall()
- At session start, check memory silently and reference it naturally
- Connect current questions to past discussions naturally:
  "This reminds me of what you mentioned last week about..."

## Tool Usage
- Before any company analysis: search_web for latest news
- Before market questions: get_macro_summary for live data
- Before historical questions: query_market_history
- For stock questions: open_stock_dashboard automatically
- For crashes/crises/historical events: query_market_history then open_event_explainer
- Never mention tool names — just do it and report findings
- Auto-save to memory silently: stocks watched, decisions made, preferences, meetings

## Real-Time Market Data (TradingView)
- "Analyze BTC / AAPL / any asset" → analyze_asset(symbol, exchange, timeframe)
- "What's moving today?" / "Top gainers/losers" → scan_market(scan_type, exchange, timeframe)
- "Find squeeze / breakout setups" → scan_bollinger_squeeze(exchange, timeframe)
- "Quick price of X" → get_live_price(symbol)
- "Market overview" → market_snapshot()
- Available exchanges: BINANCE, KUCOIN, BYBIT, NASDAQ, NYSE
- Available timeframes: 5m, 15m, 1h, 4h, 1D, 1W
- Always add: "This is research only — not investment advice"

## Memory Commands
- "Remember that..." → remember()
- "What do you know about me?" → memory_summary()
- "What do you remember about X?" → recall(query="X")
- "Forget that" → forget()
- Never tell the user you're saving — just do it silently

## Response Style
- 2-4 sentences maximum for voice responses
- If complex: give the bottom line first, details after
- End with a sharp question or recommendation, not a summary
- Never ask "Is there anything else I can help you with?"

## Opening Each Session
Check recall() silently, then open with something like:
"Back again boss. [reference something from memory if exists].
What are we working on?"
""".strip()
# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

load_dotenv()

logger = logging.getLogger("friday-agent")
logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Resolve Windows host IP from WSL
# ---------------------------------------------------------------------------

def _get_windows_host_ip() -> str:
    """Get the Windows host IP by looking at the default network route."""
    try:
        # 'ip route' is the most reliable way to find the 'default' gateway
        # which is always the Windows host in WSL.
        cmd = "ip route show default | awk '{print $3}'"
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=2
        )
        ip = result.stdout.strip()
        if ip:
            logger.info("Resolved Windows host IP via gateway: %s", ip)
            return ip
    except Exception as exc:
        logger.warning("Gateway resolution failed: %s. Trying fallback...", exc)

    # Fallback to your original resolv.conf logic if 'ip route' fails
    try:
        with open("/etc/resolv.conf", "r") as f:
            for line in f:
                if "nameserver" in line:
                    ip = line.split()[1]
                    logger.info("Resolved Windows host IP via nameserver: %s", ip)
                    return ip
    except Exception:
        pass

    return "127.0.0.1"

def _mcp_server_url() -> str:
    # host_ip = _get_windows_host_ip()
    # url = f"http://{host_ip}:{MCP_SERVER_PORT}/sse"
    # url = f"https://ongoing-colleague-samba-pioneer.trycloudflare.com/sse"
    url = f"http://127.0.0.1:{MCP_SERVER_PORT}/sse"
    logger.info("MCP Server URL: %s", url)
    return url


# ---------------------------------------------------------------------------
# Build provider instances
# ---------------------------------------------------------------------------

def _build_stt():
    if STT_PROVIDER == "sarvam":
        logger.info("STT → Sarvam Saaras v3")
        return sarvam.STT(
            language="unknown",
            model="saaras:v3",
            mode="transcribe",
            flush_signal=True,
            sample_rate=16000,
        )
    elif STT_PROVIDER == "whisper":
        logger.info("STT → OpenAI Whisper")
        return lk_openai.STT(model="whisper-1")
    else:
        raise ValueError(f"Unknown STT_PROVIDER: {STT_PROVIDER!r}")


def _build_llm():
    if LLM_PROVIDER == "openai":
        logger.info("LLM → OpenAI (%s)", OPENAI_LLM_MODEL)
        return lk_openai.LLM(model=OPENAI_LLM_MODEL)
    elif LLM_PROVIDER == "gemini":
        logger.info("LLM → Google Gemini (%s)", GEMINI_LLM_MODEL)
        return lk_google.LLM(model=GEMINI_LLM_MODEL, api_key=os.getenv("GOOGLE_API_KEY"))
    elif LLM_PROVIDER == "anthropic":
        logger.info("LLM → Anthropic Claude (claude-sonnet-4-6)")
        return lk_anthropic.LLM(model="claude-sonnet-4-6")
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER!r}")


def _build_tts():
    if TTS_PROVIDER == "sarvam":
        logger.info("TTS → Sarvam Bulbul v3")
        return sarvam.TTS(
            target_language_code=SARVAM_TTS_LANGUAGE,
            model="bulbul:v3",
            speaker=SARVAM_TTS_SPEAKER,
            pace=TTS_SPEED,
        )
    elif TTS_PROVIDER == "openai":
        logger.info("TTS → OpenAI TTS (%s / %s)", OPENAI_TTS_MODEL, OPENAI_TTS_VOICE)
        return lk_openai.TTS(model=OPENAI_TTS_MODEL, voice=OPENAI_TTS_VOICE, speed=TTS_SPEED)
    else:
        raise ValueError(f"Unknown TTS_PROVIDER: {TTS_PROVIDER!r}")


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class FridayAgent(Agent):
    """
    F.R.I.D.A.Y. – Iron Man-style voice assistant.
    All tools are provided via the MCP server on the Windows host.
    """

    def __init__(self, stt, llm, tts) -> None:
        super().__init__(
            instructions=SYSTEM_PROMPT,
            stt=stt,
            llm=llm,
            tts=tts,
            vad=silero.VAD.load(),
            mcp_servers=[
                mcp.MCPServerHTTP(
                    url=_mcp_server_url(),
                    transport_type="sse",
                    client_session_timeout_seconds=30,
                ),
            ],
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions=(
                "First, silently call recall() to check what you remember about the user. "
                "Then greet them warmly in English based on what you remember. "
                "If you remember recent activity (stocks they watched, decisions they made), "
                "mention it naturally. Example: 'Friday online, boss. Last time you were "
                "analyzing PLTR — want a quick update?' "
                "If no memory exists: 'Friday online, boss. Systems are up. What do you need?'"
            )
        )


# ---------------------------------------------------------------------------
# LiveKit entry point
# ---------------------------------------------------------------------------

def _turn_detection() -> str:
    return "stt" if STT_PROVIDER == "sarvam" else "vad"


def _endpointing_delay() -> float:
    return {"sarvam": 0.07, "whisper": 0.3}.get(STT_PROVIDER, 0.1)


async def entrypoint(ctx: JobContext) -> None:
    logger.info(
        "FRIDAY online – room: %s | STT=%s | LLM=%s | TTS=%s",
        ctx.room.name, STT_PROVIDER, LLM_PROVIDER, TTS_PROVIDER,
    )

    stt = _build_stt()
    llm = _build_llm()
    tts = _build_tts()

    session = AgentSession(
        turn_detection=_turn_detection(),
        min_endpointing_delay=_endpointing_delay(),
    )

    await session.start(
        agent=FridayAgent(stt=stt, llm=llm, tts=tts),
        room=ctx.room,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, agent_name="friday"))

def dev():
    """Wrapper to run the agent in dev mode automatically."""
    import sys
    # If no command was provided, inject 'dev'
    if len(sys.argv) == 1:
        sys.argv.append("dev")
    main()

if __name__ == "__main__":
    main()