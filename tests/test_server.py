"""Tests: generator integrity + that the MCP server registers its tools."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from generator import DatasetSpec, generate, validate_integrity  # noqa: E402


def test_referential_integrity():
    report = validate_integrity(generate(DatasetSpec(companies=12, seed=7)))
    assert report.ok, report.violations


def test_determinism():
    assert generate(DatasetSpec(seed=5)) == generate(DatasetSpec(seed=5))


def test_mcp_server_exposes_tools():
    import server
    tools = asyncio.run(server.mcp.list_tools())
    names = {t.name for t in tools}
    assert {"generate_dataset", "validate_dataset"} <= names


def test_generate_tool_returns_pass():
    import server
    out = server.generate_dataset(companies=10, seed=3)
    assert out["referential_integrity"] == "PASS"
    assert out["row_counts"]["companies"] == 10
