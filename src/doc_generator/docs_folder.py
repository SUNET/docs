import subprocess
import os

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


async def generate(folder_name: str):

    curr_cwd = os.getcwd()
    os.chdir(f"/app/pages/generating/{folder_name}/docs")

    project_name = "project_name_test"
    author = "Victor Näslund"
    version = "1"
    release = "2"
    language = "en"
    subprocess.check_call(f"sh -c \"sphinx-quickstart --no-sep -p '{project_name}' -a '{author}' -v {version} -r {release} -l {language}\"", shell=True)

    with open("conf.py") as conf_file:
        conf_file_data = conf_file.read()

    print(conf_file_data)

    conf_file_data = conf_file_data.replace('extensions = []', conf_file_data_replace)

    with open("conf.py", "w") as conf_file:
        conf_file.write(conf_file_data)



    with open("index.rst") as index_file:
        index_file_data = index_file.read()

    print(index_file_data)

    index_file_data = index_file_data.replace(':caption: Contents:', index_file_data_replace)

    with open("index.rst", "w") as index_file:
        index_file.write(index_file_data)



    subprocess.check_call(f"sh -c \"make html\"", shell=True)

    os.chdir("_build/html")
    subprocess.check_call(f"sh -c \"zip docs.zip -r *\"", shell=True)
    subprocess.check_call(f"sh -c \"curl -X POST -F 'file=@docs.zip' http://web:5000/api/python_pkcs11/0.11\"", shell=True)



    os.chdir(f"{curr_cwd}")
