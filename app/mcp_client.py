import re
from typing import Dict

from langchain_mcp_adapters.client import MultiServerMCPClient

from app.config import ROOT_DIR


def detect_tool_needs(text: str) -> Dict[str, bool]:
    lowered = text.lower()
    weather = bool(re.search(r"\b(weather|forecast|rain|temperature|hot|humid)\b", lowered))
    currency = bool(re.search(r"\b(convert|conversion|exchange|rate)\b", lowered)) and bool(
        re.search(r"\b(inr|sgd|usd|eur|gbp|jpy|aud|cad)\b", lowered)
    )
    return {"weather": weather, "currency": currency}


class MCPTravelTools:
    async def _call(self, question: str, needs: Dict[str, bool]):
        client = MultiServerMCPClient({
            "travel": {
                "command": "python",
                "args": [str(ROOT_DIR / "travel_mcp" / "travel_mcp_server.py")],
                "transport": "stdio",
            }
        })
        tools = await client.get_tools()
        by_name = {tool.name: tool for tool in tools}
        results = {}
        if needs["weather"] and "get_weather_forecast" in by_name:
            results["weather"] = await by_name["get_weather_forecast"].ainvoke({"location": "Singapore", "days": 3})
        if needs["currency"] and "convert_currency" in by_name:
            match = re.search(r"([\d,]+(?:\.\d+)?)\s*(?:in|)?\s*(INR|SGD|USD|EUR|GBP|JPY|AUD|CAD)", question, re.I)
            target = re.search(r"(?:to|into)\s*(INR|SGD|USD|EUR|GBP|JPY|AUD|CAD)", question, re.I)
            if match and target:
                results["currency"] = await by_name["convert_currency"].ainvoke({
                    "amount": float(match.group(1).replace(",", "")),
                    "from_currency": match.group(2).upper(),
                    "to_currency": target.group(1).upper(),
                })
        return results

    def invoke(self, question: str, needs: Dict[str, bool]):
        import asyncio
        return asyncio.run(self._call(question, needs))
