"""Module that has the generator for python porjects with a docs folder"""

import os
import subprocess

from fastapi import HTTPException

from doc_generator.base import AbstractGenerator, CodeLanguage

doc_folders: list[str] = ["docs", "doc", "documentation", "documentations"]


class Generator(AbstractGenerator):
    """Class to generate docs for python projects with a docs folder"""

    generator_name = "generator_python_with_docs_folder"  # Your generator name
    generator_language = CodeLanguage.PYTHON  # Your project's language
    generator_priority: int = 99  # Between 0 - 99, lowest is higest priority

    async def compatable(
        self, venv_path: str, folder_name: str, project_name: str, language: CodeLanguage | None
    ) -> bool:
        # Return false if current project is another language than the one we can generate for
        if language is not None and language != self.language():
            return False

        # Assume we have some docs if 'docs' folder exists
        for folder in doc_folders:
            if os.path.isdir(f"{folder_name}/{folder}"):
                return True

        return False

    async def generate(self, venv_path: str, folder_name: str, project_name: str, language: CodeLanguage | None) -> str:
        # Find documentation folder
        docs_folder = await self.docs_folder(folder_name)

        # Install requirements if any
        await self.install_docs_reqs(venv_path, folder_name, docs_folder, project_name)

        old_cwd = os.getcwd()
        os.chdir(f"{folder_name}/{docs_folder}")

        # If project dont have a Makefile we create a default one
        if not os.path.isfile("Makefile"):
            await self.create_default_sphinx_config(venv_path, folder_name, docs_folder, project_name)

        # Can be removed when cnaas-nms fixes their libs
        if project_name == "cnaas-nms":
            subprocess.run(
                f'sh -c ". {venv_path}/bin/activate && pip3 install --upgrade sphinx"',
                shell=True,
                check=True,
                capture_output=True,
            )

        try:
            subprocess.run(
                f'sh -c ". {venv_path}/bin/activate && make html"', shell=True, check=True, capture_output=True
            )

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            subprocess.run(
                f'sh -c ". {venv_path}/bin/activate && make -B"', shell=True, check=True, capture_output=True
            )

        os.chdir(f"{old_cwd}")

        if os.path.isdir(f"{folder_name}/{docs_folder}/_build/html"):
            return f"{folder_name}/{docs_folder}/_build/html"

        return f"{folder_name}/{docs_folder}"

    async def docs_folder(self, folder_name: str) -> str:
        """Find docs folder in project repo.
        Returned str is docs folder name or raise HTTPException

        Parameters:
        folder_name str: The path to the cloned down project.

        Returns:
        str
        """

        for folder in doc_folders:
            if os.path.isdir(f"{folder_name}/{folder}"):
                print(f"found docs folder {folder}")
                return folder

        raise HTTPException(200, detail="ERROR: Could not find a documentation folder")

    async def pip_install(self, venv_path: str, path: str) -> None:
        """Install python libs or projects from requirements file or folder path.

        Parameters:
        venv_path str: Path to the venv to use.
        path str: The path to the requirements file or project folder.
        """

        if os.path.isfile(path):
            install_path = f"-r {path}"
        else:
            install_path = path

        try:
            subprocess.run(
                f'sh -c ". {venv_path}/bin/activate && pip3 install {install_path}"',
                shell=True,
                timeout=600,
                capture_output=True,
                check=True,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            if os.path.isfile(path):
                with open(path, "a", encoding="utf-8") as write_file:
                    write_file.write("\npyyaml==5.3.1\nJinja2<3.2\n")

            subprocess.run(
                f'sh -c ". {venv_path}/bin/activate && pip3 install {install_path}"',
                shell=True,
                timeout=600,
                capture_output=True,
                check=True,
            )

    async def install_docs_reqs(self, venv_path: str, folder_name: str, docs_folder: str, project_name: str) -> None:
        """Install the requirements for generating docs.
        Currently the project itself is possible and from a requirements file if exists

        Parameters:
        venv_path str: Path to venv to use.
        folder_name str: Path to cloned down repo.
        docs_folder str: Path to documentation folder in the repo.
        project_name str: The name of the cloned down project.
        """

        # FIXME: Add file lock for other workers due to pip install

        # Try to install the project from pip, might be needed to
        # pip3 install ./ on project folder if fails try to download and install using pip install {project_name}
        if os.path.isfile(f"{folder_name}/requirements.txt"):
            await self.pip_install(venv_path, f"{folder_name}/requirements.txt")
            print(f"Installed libs from {folder_name}/requirements.txt", flush=True)

        elif os.path.isfile(f"{folder_name}/requirements.in"):
            await self.pip_install(venv_path, f"{folder_name}/requirements.in")
            print(f"Installed libs from {folder_name}/requirements.in", flush=True)

        try:
            await self.pip_install(venv_path, f"{folder_name}")
            print(f"Installed project from {folder_name}", flush=True)

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            subprocess.run(
                f'sh -c ". {venv_path}/bin/activate && pip3 install {project_name}"',
                shell=True,
                timeout=600,
                capture_output=True,
                check=False,
            )
            print(f"Tried to download and install project using 'pip install {project_name}'", flush=True)

        if os.path.isfile(f"{folder_name}/{docs_folder}/requirements.txt"):
            await self.pip_install(venv_path, f"{folder_name}/{docs_folder}/requirements.txt")
            print(f"Installed doc libs from {folder_name}/{docs_folder}/requirements.txt", flush=True)

        elif os.path.isfile(f"{folder_name}/{docs_folder}/requirements.in"):
            await self.pip_install(venv_path, f"{folder_name}/{docs_folder}/requirements.in")
            print(f"Installed doc libs from {folder_name}/{docs_folder}/requirements.in", flush=True)

    async def create_default_sphinx_config(
        self, venv_path: str, folder_name: str, docs_folder: str, project_name: str
    ) -> None:
        """Create a default sphinx config to generate docs with.

        Parameters:
        venv_path str: Path to venv to use.
        folder_name str: Path to cloned down repo.
        docs_folder str: Path to documentation folder in the repo.
        project_name str: The name of the cloned down project.
        """

        # FIXME
        author = "FIXME LASTNAME"
        version = "1"
        release = "2"
        human_language = "en"

        old_cwd = os.getcwd()
        os.chdir(f"{folder_name}/{docs_folder}")

        subprocess.run(
            f"sh -c \". {venv_path}/bin/activate && sphinx-quickstart --no-sep -p '{project_name}' -a '{author}' -v {version} -r {release} -l {human_language}\"",
            shell=True,
            capture_output=True,
            check=True,
        )

        with open("conf.py", encoding="utf-8") as conf_file:
            conf_file_data = conf_file.read()
        conf_file_data = conf_file_data.replace("extensions = []", CONF_FILE_DATA_REPLACE)
        with open("conf.py", "w", encoding="utf-8") as conf_file:
            conf_file.write(conf_file_data)

        # FIXME do for all doc files in dir not just README
        if os.path.isfile("README.md") or os.path.isfile(path="README.rst"):
            with open("index.rst", encoding="utf-8") as index_file:
                index_file_data = index_file.read()

            index_file_data = index_file_data.replace(":caption: Contents:", INDEX_FILE_DATA_REPLACE)
            with open("index.rst", "w", encoding="utf-8") as index_file:
                index_file.write(index_file_data)

        os.chdir(f"{old_cwd}")


CONF_FILE_DATA_REPLACE = """
extensions = ['myst_parser']

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

import os
import sys
sys.path.insert(0, os.path.abspath('..'))


"""

# FIXME: check files files exists, dont assume only README.md exists
INDEX_FILE_DATA_REPLACE = """:caption: Contents:

   README
"""
