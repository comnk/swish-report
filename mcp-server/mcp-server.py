from mcp.server.fastmcp import FastMCP
from mcp_server_helper_functions import *
mcp = FastMCP("swish-report-mcp", host="127.0.0.1", port=7000)

@mcp.tool()
def get_high_school_ranking_profile(player_name: str, class_year: str) -> str:
    rankings = fetch_player_rankings(player_name, class_year)
    return f"Ranking results for {player_name} from the class of {class_year}: {rankings}"

@mcp.tool()
def get_player_ranking_history(player_name, class_year):
    pass

if __name__ == "__main__":
    mcp.run(transport='streamable-http')