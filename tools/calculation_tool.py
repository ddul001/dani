# tools/calculation_tool.py
from typing import Dict, Any
import ast, math, numpy as np
from core.tool import Tool

class CalculationTool(Tool):
    @property
    def name(self) -> str: return "calculation"
    @property
    def description(self) -> str: return "Evaluate Python math"
    def execute(self, params: Dict[str, Any]) -> Any:
        expr = params.get("formula", params.get("goal",""))
        safe = {"math":math,"np":np}
        tree = ast.parse(expr, mode='eval')
        for n in ast.walk(tree):
            if isinstance(n, (ast.Import, ast.ImportFrom)): raise ValueError("No imports")
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id not in safe: raise ValueError("Unsafe call")
        return {"result": eval(compile(tree,'','eval'),{"__builtins__":{}},safe)}
