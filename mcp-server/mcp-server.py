from mcp.server.fastmcp import FastMCP

mcp = FastMCP("swish-report-mcp", host="127.0.0.1", port=7000)

@mcp.tool()
def get_high_school_profile(player_name: str, class_year: str) -> str:
    pass

if __name__ == "__main__":
    mcp.run(transport='streamable-http')