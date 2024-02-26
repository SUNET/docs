from abc import ABC, abstractmethod
from enum import Enum


class CodeLanguage(Enum):
    PYTHON = 1
    JAVA = 2


class AbstractGenerator(ABC):
    """Abstract base class for database classes"""

    generator_name: str
    generator_language: CodeLanguage
    generator_priority: int

    def __init__(self, name: str, language: CodeLanguage, priority: int) -> None:
        self.generator_name = name
        self.generator_language = language
        self.generator_priority = priority
        super().__init__()

    def name(self) -> str:
        return self.generator_name

    def priority(self) -> int:
        return self.generator_priority

    def language(self) -> CodeLanguage:
        return self.generator_language

    @abstractmethod
    async def compatable(self, folder_name: str, language: CodeLanguage | None) -> bool:
        """fixme"""

    @abstractmethod
    async def generate(self, folder_name: str) -> str:
        """fixme"""
