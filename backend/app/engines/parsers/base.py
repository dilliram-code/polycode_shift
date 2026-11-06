"""
PolyShift - Base Parser Interface
"""
from abc import ABC, abstractmethod
from typing import List
from app.engines.ir import Program

class BaseParser(ABC):
    @property
    @abstractmethod
    def language_name(self) -> str:
        pass

    @abstractmethod
    def parse(self, code: str) -> Program:
        """Parses source code string into an IR Program representation."""
        pass

    @abstractmethod
    def validate_syntax(self, code: str) -> tuple[bool, List[str]]:
        """Validates source syntax. Returns (is_valid, list_of_errors)."""
        pass

