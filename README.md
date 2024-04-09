# Central documentation system

# Deploy

```bash
docker compose build && docker compose up
```

# Update config variables in docs_generator/conf.py
This is for autodiscover new projects to generate docs for.
The demo functionality below will still work without this.


# Demo functionality

```bash
# Can be any repo you want. Post data is the same dict format as githubs webhook feature
curl -vk -X POST localhost:8080/git_repo -H 'content-type: application/json' \
-d '{"repository": {"name": "pyff", "clone_url": "https://github.com/IdentityPython/pyFF.git"}}'
```
view at

http://localhost:8000

# To add support to generate docs for a new type of project

* Create a new python file starting with 'generator_' in 'doc_generator/generators' folder.
* In the file create a class called 'Generator' which implement our 'AbstractGenerator'. See example below.
* Your generator will automatically load.
* The idea is a loop over all generators and use one which is compatable with the project we are trying to generate docs for.
* See example code below or look at existing generators.

```python
import os
from doc_generator.base import AbstractGenerator, CodeLanguage

class Generator(AbstractGenerator):
    generator_name = "generator_<LANGUAGE>_<DESCRIPTION>" # Name of your doc generator
    generator_language = CodeLanguage.PYTHON # Your project's language
    generator_priority: int = 10 # Between 0 - 99, lowest is higest priority

    async def compatable(self, venv_path: str, folder_name: str, project_name: str, language: CodeLanguage | None) -> bool:
        """Check if a folder containing a project is compatable with this doc generator.
        See self.generate()

        Parameters:
        venv_path str: Path to python venv folder.
        folder_name str: Path to the cloned down project folder.
        project_name str: Name of the project.
        language CodeLanguage | None: The code language.

        Returns:
        bool
        """

        # Example code below

        if language is not None and self.language() != language:
            return False

        # Assume we have some docs to generate if 'docs' folder exists
        if not os.path.isdir(f"{folder_name}/docs"):
            return False

        return True

    async def generate(self, venv_path: str, folder_name: str, project_name: str, language: CodeLanguage | None) -> str:
        """Generate docs from a folder containing a project with this method
        Returned str is path to the generated docs folder, usually containing the index.html.

        Parameters:
        venv_path str: Path to python venv folder.
        folder_name str: Path to the cloned down project folder.
        project_name str: Name of the project.
        language CodeLanguage | None: The code language.

        Returns:
        str
        """

        # Your code here...
```

# Contribute / for developers

```bash
mypy --strict --namespace-packages --cache-dir=/dev/null --namespace-packages doc_generator/ \
&& isort --line-length 120 doc_generator/ && black -l 120 doc_generator/ && pylint --max-line-length 120 doc_generator/*
```
