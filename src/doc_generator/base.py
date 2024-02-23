from enum import Enum
from abc import ABC, abstractmethod

class CodeLanguage(Enum):
    PYTHON = 1
    JAVA = 2

class AbstractGenerator(ABC):
    """Abstract base class for database classes"""

    def __init__(self, name: str) -> None:
        self.generator_name = name
        super().__init__()

    def name(self) -> str:
        return self.generator_name

    @abstractmethod
    def language(self) -> CodeLanguage:
        """fixme"""

    @abstractmethod
    async def compatable(self, language: CodeLanguage, folder_name: str) -> bool:
        """fixme"""

    @abstractmethod
    async def generate(self, folder_name: str) -> str:
        """fixme"""

# FIXME check code language in repo
async def detect_language(folder_name: str) -> CodeLanguage:
    return CodeLanguage.PYTHON
