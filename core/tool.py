# core/tool.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class Tool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        pass
