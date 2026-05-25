"""A minimal, production-shaped MCP server.

Exposes synthetic-data generation as Model Context Protocol tools so any MCP
client (Claude Desktop, Claude Code, IDE agents) can spin up realistic,
referentially-intact demo data on demand.

Run locally:
    pip install -r requirements.txt
    python server.py            # serves over stdio

Register in an MCP client (e.g. Claude Desktop config):
    {
      "mcpServers": {
        "synthetic-data": { "command": "python", "args": ["/abs/path/server.py"] }
      }
    }
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from generator import DatasetSpec, generate, validate_integrity

mcp = FastMCP("synthetic-data")


@mcp.tool()
def generate_dataset(companies: int = 8, months: int = 18, seed: int = 42) -> dict[str, Any]:
    """Generate a referentially-intact business dataset and return row counts plus a sample.

    Args:
        companies: number of company records to create.
        months: months of invoice history per company.
        seed: random seed; the same seed always yields identical data.
    """
    data = generate(DatasetSpec(companies=companies, months_of_history=months, seed=seed))
    report = validate_integrity(data)
    return {
        "seed": seed,
        "row_counts": report.row_counts,
        "referential_integrity": "PASS" if report.ok else "FAIL",
        "violations": report.violations[:10],
        "sample_invoice": data["invoices"][0] if data["invoices"] else None,
    }


@mcp.tool()
def validate_dataset(companies: int = 8, months: int = 18, seed: int = 42) -> dict[str, Any]:
    """Generate a dataset and return only its referential-integrity report."""
    data = generate(DatasetSpec(companies=companies, months_of_history=months, seed=seed))
    report = validate_integrity(data)
    return {
        "ok": report.ok,
        "row_counts": report.row_counts,
        "violation_count": len(report.violations),
        "violations": report.violations[:25],
    }


@mcp.resource("schema://dataset")
def dataset_schema() -> str:
    """The relational schema this server produces, as a readable description."""
    return (
        "companies(id, name, industry, created_at, country)\n"
        "users(id, company_id->companies, name, role, is_active)\n"
        "subscriptions(id, company_id->companies, owner_user_id->users, plan, monthly_price, status)\n"
        "invoices(id, company_id->companies, subscription_id->subscriptions, issued_date, due_date, total, status, paid_date)\n"
        "invoice_line_items(id, invoice_id->invoices, description, quantity, unit_price, amount)\n"
    )


if __name__ == "__main__":
    mcp.run()
