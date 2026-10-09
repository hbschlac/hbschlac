"""End-to-end check: spawn the MCP server over stdio, list its tools, call two of them.

    uv run --directory rx-compare python scripts/mcp_smoke.py
"""
from __future__ import annotations

import asyncio
import json
import pathlib
import sys

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

ROOT = pathlib.Path(__file__).resolve().parents[1]


async def main() -> int:
    params = StdioServerParameters(command=sys.executable, args=["-m", "rxcompare.server"], cwd=str(ROOT))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = sorted(t.name for t in (await session.list_tools()).tools)
            print("tools:", tools)
            expected = {"search_drug", "compare_prices", "check_quote", "fair_price", "list_sources"}
            assert expected <= set(tools), f"missing tools: {expected - set(tools)}"

            res = await session.call_tool(
                "check_quote",
                {"drug": "atorvastatin", "strength": "40mg", "zip_code": "94612", "quoted_price": 30.0},
            )
            payload = json.loads(res.content[0].text)
            print("check_quote:", payload["verdict"])
            assert payload["cheaper_options"], "expected something cheaper than $30"

            res = await session.call_tool(
                "compare_prices", {"drug": "lisinopril", "strength": "10mg", "zip_code": "43081"}
            )
            payload = json.loads(res.content[0].text)
            for q in payload["quotes"]:
                print(f"  {q['program']:32} ${q['price']:.2f}  {q['fulfillment']}")
            prices = [q["price"] for q in payload["quotes"]]
            assert prices == sorted(prices), "quotes must be cheapest-first"
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
