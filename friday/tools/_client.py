"""
_client.py — Shared singleton clients for the entire Friday tool system.
Avoids re-initializing Anthropic and ChromaDB on every tool call.
"""
import anthropic
import chromadb
from pathlib import Path

# ── Anthropic ────────────────────────────────────────────────────
_anthropic_client = None

def get_anthropic_client() -> anthropic.Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic()
    return _anthropic_client


# ── ChromaDB ─────────────────────────────────────────────────────
_chroma_client = None
_chroma_collections = None

def get_chroma_collections() -> dict:
    global _chroma_client, _chroma_collections
    if _chroma_collections is None:
        DB_PATH = str(Path(__file__).parent.parent.parent / "data" / "market_chroma_db")
        _chroma_client = chromadb.PersistentClient(path=DB_PATH)
        _chroma_collections = {
            "market":     _chroma_client.get_or_create_collection("market_history"),
            "fear_greed": _chroma_client.get_or_create_collection("fear_greed_history"),
            "events":     _chroma_client.get_or_create_collection("historical_events"),
        }
    return _chroma_collections
