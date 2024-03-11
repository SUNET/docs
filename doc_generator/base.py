"""Module which declare our abstract generator class"""

from abc import ABC, abstractmethod
from enum import Enum


class CodeLanguage(Enum):
    """Enum class for code languages"""

    PYTHON = 1
    JAVA = 2


class AbstractGenerator(ABC):
    """Abstract base class for generator classes"""

    generator_name: str
    generator_language: CodeLanguage
    generator_priority: int

    def __init__(self, name: str, language: CodeLanguage, priority: int) -> None:
        self.generator_name = name
        self.generator_language = language
        self.generator_priority = priority
        super().__init__()

    def name(self) -> str:
        """The generator's name

        Returns:
        str
        """

        return self.generator_name

    def priority(self) -> int:
        """The generator's priority

        Returns:
        int
        """

        return self.generator_priority

    def language(self) -> CodeLanguage:
        """The generator's code language

        Returns:
        CodeLanguage
        """

        return self.generator_language

    @abstractmethod
    async def compatable(
        self, venv_path: str, folder_name: str, project_name: str, language: CodeLanguage | None
    ) -> bool:
        """Check if a folder containing a project is compatable with this doc generator.
        See self.generate()

        Parameters:
        venv_path str: Path to python venv folder.
        folder_name str: Path to the cloned down project folder.
        project_name str: Name of the project.
        language CodeLanguage: The code language.

        Returns:
        bool
        """

    @abstractmethod
    async def generate(self, venv_path: str, folder_name: str, project_name: str, language: CodeLanguage | None) -> str:
        """Generate docs from a folder containing a project with this method
        Returned str is path to the generated docs folder, usually containing the index.html.

        Parameters:
        venv_path str: Path to python venv folder.
        folder_name str: Path to the cloned down project folder.
        project_name str: Name of the project.
        language CodeLanguage: The code language.

        Returns:
        str
        """
