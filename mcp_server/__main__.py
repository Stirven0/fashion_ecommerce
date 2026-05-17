import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fashion_store"))

from mcp_server.server import mcp

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
