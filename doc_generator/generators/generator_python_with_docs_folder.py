import os
import subprocess

from doc_generator.base import AbstractGenerator, CodeLanguage


class Generator(AbstractGenerator):
    generator_name = "generator_python_with_docs_folder"  # Your generator name
    generator_language = CodeLanguage.PYTHON  # Your project's language
    generator_priority: int = 99  # Between 0 - 99, lowest is higest priority

    async def compatable(self, folder_name: str, language: CodeLanguage | None) -> bool:
        # Return false if current project is another language than the one we can generate for
        if language is not None and language != self.language():
            return False

        # Assume we have some docs if 'docs' folder exists
        if not os.path.isdir(f"/app/pages/generating/{folder_name}/docs"):
            return False

        return True

    async def generate(self, folder_name: str) -> str:
        curr_cwd = os.getcwd()
        os.chdir(f"/app/pages/generating/{folder_name}/docs")

        project_name = "project_name_test"
        author = "Victor Näslund"
        version = "1"
        release = "2"
        language = "en"

        subprocess.run(
            f"sh -c \"sphinx-quickstart --no-sep -p '{project_name}' -a '{author}' -v {version} -r {release} -l {language}\"",
            shell=True,
            capture_output=True,
            check=True,
        )

        with open("conf.py") as conf_file:
            conf_file_data = conf_file.read()
        conf_file_data = conf_file_data.replace("extensions = []", conf_file_data_replace)
        with open("conf.py", "w") as conf_file:
            conf_file.write(conf_file_data)

        with open("index.rst") as index_file:
            index_file_data = index_file.read()
        index_file_data = index_file_data.replace(":caption: Contents:", index_file_data_replace)
        with open("index.rst", "w") as index_file:
            index_file.write(index_file_data)

        subprocess.run(f'sh -c "make html"', shell=True, check=True, capture_output=True)

        os.chdir("_build/html")
        subprocess.run(f'sh -c "zip docs.zip -r *"', shell=True, capture_output=True, check=True)

        # Send to docat web interface
        subprocess.check_call(
            f"sh -c \"curl -X POST -F 'file=@docs.zip' http://web:5000/api/python_pkcs11/0.15\"", shell=True
        )

        path_to_doc_files = os.getcwd()
        os.chdir(f"{curr_cwd}")

        return path_to_doc_files


conf_file_data_replace = """
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


index_file_data_replace = """:caption: Contents:

   README
"""
