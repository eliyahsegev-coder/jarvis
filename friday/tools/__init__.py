"""
Tool registry — imports and registers all tool modules with the MCP server.
"""
from friday.tools import web, system, utils, macro, business, reports, browser, digest, dashboard, vision, market_memory, explainer, memory, tradingview_tools

def register_all_tools(mcp):
    """Register all tool groups onto the MCP server instance."""
    web.register(mcp)
    system.register(mcp)
    utils.register(mcp)
    macro.register(mcp)
    business.register(mcp)
    reports.register(mcp)
    browser.register(mcp)
    digest.register(mcp)
    dashboard.register(mcp)
    vision.register(mcp)
    market_memory.register(mcp)
    explainer.register(mcp)
    memory.register(mcp)
    tradingview_tools.register(mcp)
