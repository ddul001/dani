# tools/rest_api_tool.py
from typing import Dict, Any
from core.tool import Tool

class RestApiTool(Tool):
    @property
    def name(self) -> str: return "rest_api"
    @property
    def description(self) -> str: return "Make REST calls"
    def execute(self, params: Dict[str, Any]) -> Any:
        return {"message":"placeholder rest api"}
