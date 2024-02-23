# Central documentation system

# Deploy

```bash
docker compose build && docker compose up
```

# Demo functionality

```bash
curl -vk -X POST localhost:8080/test1
```
view at

http://localhost:8000

# To add support to generate docs for a new type of project

* Create a new python file in 'generators' folder.
* Create a class called 'Generator' which implement 'AbstractGenerator'.
* Your generator with automatically loaded and used.
* The idea is a loop over all generators and use one which is compatable with the project we are trying to generate docs for.
* See example code below or look at existing generators.

```python
from src.doc_generator.base import AbstractGenerator, CodeLanguage

class Generator(AbstractGenerator):

    # Your projects language
    def language(self) -> CodeLanguage:
        return CodeLanguage.PYTHON

    async def compatable(self, language: CodeLanguage, folder_name: str) -> bool:
    """
    # Code to check if the repo is compatable with your doc generator
    # Path to your git cloned project are /app/pages/generating/{folder_name}
    """

        if self.language() != language:
            return False

        # Assume we have some docs to generate if 'docs' folder exists
        if not os.path.isdir(f"/app/pages/generating/{folder_name}/docs"):
            return False

        return True

    # Your code to generate sphinx docs for a project with your layout
    async def generate(self, folder_name: str) -> str:
        """Your code here, return folder path to the sphinx generated html folder"""
```