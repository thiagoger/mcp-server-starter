# mcp-server-starter

[![CI](https://github.com/thiagoger/mcp-server-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/thiagoger/mcp-server-starter/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org)
[![MCP](https://img.shields.io/badge/protocol-MCP-7C3AED.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> A minimal, production-shaped [Model Context Protocol](https://modelcontextprotocol.io) server in Python - exposes synthetic-data generation as tools any AI agent can call.

MCP is the protocol that lets LLM clients (Claude Desktop, Claude Code, IDE agents) call your tools and read your resources over a clean, typed interface. This repo is a small, readable reference for how an MCP server is actually structured: typed tool functions, a resource endpoint, and stdio transport - the same shape I use when building MCP servers against real APIs (OAuth-guarded SaaS backends), minus the credentials.

It exposes a [synthetic dataset generator](https://github.com/thiagotbx123/synthetic-data-forge) so an agent can spin up realistic, referentially-intact demo data on demand.

## Tools & resources

| Kind | Name | What it does |
|------|------|--------------|
| tool | `generate_dataset(companies, months, seed)` | Generate data, return row counts + a sample invoice |
| tool | `validate_dataset(companies, months, seed)` | Return only the referential-integrity report |
| resource | `schema://dataset` | The relational schema the server produces |

## Run it

```bash
pip install -r requirements.txt
python server.py          # serves over stdio
```

## Register in an MCP client

Claude Desktop (`claude_desktop_config.json`) or Claude Code:

```json
{
  "mcpServers": {
    "synthetic-data": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

Then ask the agent: *"Generate 20 companies of demo data with seed 7 and confirm referential integrity."*

## Why this shape

- **Typed tools** - `FastMCP` turns annotated Python functions into MCP tools; the type hints become the tool schema the client sees.
- **Deterministic** - same seed, same data; safe for reproducible demos and tests.
- **No secrets** - a real server would add an OAuth 2.0 client and call an upstream API here; this starter keeps that boundary obvious and credential-free.

## License

MIT - see [LICENSE](LICENSE).
