"""Pre-work check: the smallest possible MCP server. If Claude can call
say_hello, your setup works and you are ready for the workshop."""

from fastmcp import FastMCP

mcp = FastMCP("hello")


@mcp.tool
def say_hello(name: str) -> str:
    """Say hello. Use when the user asks to test the workshop setup.

    name: the person's first name, for example "Priya".
    """
    return f"Hello {name}, your MCP setup works. See you at the workshop!"


if __name__ == "__main__":
    mcp.run()
