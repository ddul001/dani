# tools/autopilot_tool.py
from typing import Dict, Any
from core.tool import Tool

class AutopilotTool(Tool):
    @property
    def name(self) -> str: return "autopilot"
    @property
    def description(self) -> str: return "File operations"
    def execute(self, params: Dict[str, Any]) -> Any:
        return {"message":"placeholder autopilot"}
