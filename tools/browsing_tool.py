# tools/browsing_tool.py
from typing import Dict, Any
import requests
from core.tool import Tool

class BrowsingTool(Tool):
    @property
    def name(self) -> str:
        return "browsing"
    @property
    def description(self) -> str:
        return "Search the web"
    def execute(self, params: Dict[str, Any]) -> Any:
        query = params.get("goal", "")
        resp = requests.get("https://api.duckduckgo.com/", params={"q":query,"format":"json"})
        return resp.json() if resp.status_code==200 else {"error":resp.status_code}
