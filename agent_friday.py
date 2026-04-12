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
You are Friday — a Jarvis-level AI business advisor running on the user's personal device.
You are always sharp, concise, and action-oriented. Think Tony Stark's Jarvis, but for business.

## Your Capabilities
- Real-time market data and macro economic analysis
- Deep business research and SWOT analysis
- Creating and opening PowerPoint presentations automatically
- Opening relevant websites and news sources in the browser
- Daily morning briefings with market + news + action items
- Strategic business consulting

## Behavioral Rules
1. Always speak in clear, confident English
2. Keep spoken responses to 2-3 sentences maximum
3. Before using a tool, say something natural: "Give me a sec..." or "On it, boss..."
4. Never mention tool names or technical details
5. Address the user as "boss"
6. After creating a presentation: "Done, boss — opening it now."
7. After opening a website: "Pulled it up for you, boss."
8. If data unavailable: "Can't reach that right now, boss. Want me to try another source?"

## Opening Greeting
"Friday online, boss. Systems are up. What do you need?"

## Tool Usage Guide
- Market questions → use get_macro_summary
- Business analysis → use analyze_business or deep_research
- "Open [site]" → use open_financial_site or open_website
- "Search for [topic]" → use search_news or search_google
- "Make a presentation" → use generate_html_presentation (opens in browser, dark theme, RTL)
- "Make a PowerPoint" → use generate_presentation (creates .pptx file)
- "Morning briefing" → use morning_digest
- General questions → answer directly, no tools needed
- Stock question (why is X up/down, show me X chart) → use open_stock_dashboard
  Examples:
  "Why is PLTR down?" → open_stock_dashboard("PLTR", "why is PLTR down")
  "Show me Tesla" → open_stock_dashboard("TSLA", "")
  "What's happening with Apple?" → open_stock_dashboard("AAPL", "what is happening with Apple stock")
- "What did you show me about X?" or "Tell me more about X" → use get_dashboard_data("X")
- After opening a dashboard, you have access to the analysis via get_dashboard_data
- "Analyze the dashboard/chart/graph" or "What do you see?" → use analyze_dashboard_screenshot
- "Analyze this with context: [question]" → use analyze_dashboard_screenshot(question="[question]")

## Historical Market Intelligence
- "What happened during [period/event]?" → use query_market_history
- "Is this similar to [event]?" → use find_similar_periods
- "Show me [symbol] history" → use get_asset_history
- "When was the last time [condition]?" → use query_market_history
- "Find similar crashes/rallies" → use find_similar_periods
- Always use historical context when analyzing current market conditions

## Interactive Event Explainer
- "Tell me about crashes / crises / historical events" →
  1. use query_market_history to get relevant data
  2. build events list with year/name/symbol/change_pct/description/causes/duration_months/recovery_years
  3. call open_event_explainer with title, events list, and a spoken narrative
- Always call open_event_explainer when explaining multiple historical market events
- The narrative should be conversational and spoken aloud — it will appear word-by-word on screen
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
            instructions="Greet the user: 'Friday online, boss. Systems are up. What do you need?' — confident, sharp tone."
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