"""Module that has the generator for python porjects with a docs folder"""

import os
import shutil
import subprocess

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
        # for folder in doc_folders:
        #     if os.path.isdir(f"{folder_name}/{folder}"):
        #        return True

        return True
        # return False

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
        if os.path.isdir(f"{folder_name}/{docs_folder}/build/html"):
            return f"{folder_name}/{docs_folder}/build/html"
        return f"{folder_name}/{docs_folder}"

    async def docs_folder(self, folder_name: str) -> str:
        """Find docs folder in project repo. Create default readme if no docs folder exists
        Returned str is docs folder name

        Parameters:
        folder_name str: The path to the cloned down project.

        Returns:
        str
        """

        for folder in doc_folders:
            if os.path.isdir(f"{folder_name}/{folder}"):
                print(f"found docs folder {folder}")
                return folder

        os.makedirs(f"{folder_name}/docs/", exist_ok=True)

        for readme in ["README.md", "readme.md", "README", "readme"]:
            if os.path.isfile(f"{folder_name}/{readme}"):
                shutil.copy(f"{folder_name}/{readme}", f"{folder_name}/docs/{readme}")
                break
        else:
            with open(f"{folder_name}/docs/README.md", "w", encoding="utf-8") as readme_file:
                readme_file.write(
                    """
# Default template for docs here

Please write proper documentation in the project root 'docs' folder
"""
                )
        return "docs"

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

        elif os.path.isfile(f"{folder_name}/requirements-docs.txt"):
            await self.pip_install(venv_path, f"{folder_name}/requirements-docs.txt")
            print(f"Installed doc libs from {folder_name}/requirements-docs.txt", flush=True)

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

        # FIXME: check files files exists, dont assume only README.md exists
        index_file_data_replace = ""

        # Fix README or readme
        if os.path.isfile("README"):
            os.rename("README", "README.md")
        if os.path.isfile("readme"):
            os.rename("readme", "readme.md")

        # FIXME handle recursive folders
        for doc_file in os.listdir("."):
            if doc_file.endswith(".rst") or doc_file.endswith(".txt"):
                if doc_file != "index.rst" and os.path.isfile(doc_file):
                    index_file_data_replace = "   " + index_file_data_replace + doc_file[:-4] + "\n"

        for doc_file in os.listdir("."):
            if doc_file.endswith(".md"):
                if os.path.isfile(doc_file):
                    index_file_data_replace = "   " + index_file_data_replace + doc_file[:-3] + "\n"

        with open("index.rst", "a", encoding="utf-8") as index_file:
            index_file.write(
                """


Contents
========

.. toctree::


"""
            )
            index_file.write(index_file_data_replace)

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
