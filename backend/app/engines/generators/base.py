"""
PolyShift - Base Code Generator Interface
"""
from abc import ABC, abstractmethod
from app.engines.ir import Program

class BaseGenerator(ABC):
    @property
    @abstractmethod
    def target_language(self) -> str:
        pass

    @abstractmethod
    def generate(self, program: Program) -> str:
        """Translates an IR Program into target language source code."""
        pass

