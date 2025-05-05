# tools/scraping_tool.py
from typing import Dict, Any
from core.tool import Tool

class ScrapingTool(Tool):
    @property
    def name(self) -> str: return "scraping"
    @property
    def description(self) -> str: return "Scrape webpages"
    def execute(self, params: Dict[str, Any]) -> Any:
        return {"message":"placeholder scraping"}
