"""Module for common functionality for the doc generators"""

import asyncio
import base64
import os
import shutil
import subprocess
from secrets import token_bytes
from typing import Any, Dict

import requests
from git import Repo

from doc_generator.base import CodeLanguage


async def detect_language(folder_name: str) -> CodeLanguage | None:
    """FIXME Implement this"""

    return None


def clone_url(url: str, commit: str | None) -> tuple[str, str]:
    """Clone down a code repo. Code is not async due to the git lib is not async.

    Returned data is tuple[str, str].
    The path to cloned down and checked out repo and commit

    Parameters:
    url str: Url to the git repo.
    commit str | None: Checkout this specific commit if not None.

    Returns:
    tuple[str, str]
    """

    folder_path = base64.b64encode((token_bytes(16))).hex()
    repo = Repo.clone_from(url, f"/app/data/docs/generating/{folder_path}")

    # checkout specified commit
    if commit is not None:
        new_head = repo.create_head(f"generating_docs_{folder_path}")
        new_head.set_commit(commit)
        new_head.checkout()

    commit = repo.commit().hexsha
    repo.close()
    return f"/app/data/docs/generating/{folder_path}", commit


async def upload_to_docat(finalized_docs_folder: str, repo_dir: str, project_name: str) -> None:
    """Upload generated docs to docat system.

    Parameters:
    finalized_docs_folder str: Path to generated docs folder.
    repo_dir str: Path to cloned down and checked out project repo.
    project_name str: The project's name.
    """

    old_cwd = os.getcwd()
    os.chdir(f"{finalized_docs_folder}")
    subprocess.run('sh -c "zip docs.zip -r *"', shell=True, capture_output=True, check=True)

    repo = Repo(f"{repo_dir}")
    number_of_commits = sum(1 for _ in repo.iter_commits())
    repo.close()

    os.chdir(f"{finalized_docs_folder}")

    with open("docs.zip", mode="rb") as zip_file:
        files = {"file": zip_file}
        requests.post(
            f"http://web:5000/api/{project_name}/{number_of_commits}",
            files=files,
            timeout=10,
        )

    os.chdir(old_cwd)


async def preprocessing(post_data: Dict[str, Any]) -> tuple[str, str, str, str, CodeLanguage | None]:
    """Preprocess the doc generation.
    Clone down the repo. Analyse the code language and stuff before generating docs.

    Returned data is a tuple of venv path, project path, project name, project commit, code language

    Parameters:
    post_data Dict[str, Any]: Json data from the http client. Should be the same or a subset of a github webhook.

    Returns:
    tuple[str, str, str, str, CodeLanguage | None]
    """

    # url = "https://github.com/SUNET/python_x509_pkcs11.git"
    loop = asyncio.get_running_loop()
    project_name = post_data["repository"]["clone_url"].split("/")[-1].split(".git")[0]
    post_data_commit = None

    # Better handling of types
    project_name_data = post_data["repository"]
    if isinstance(project_name_data, str):
        project_name = project_name_data

    if "head_commit" in post_data:
        commit_data = post_data["head_commit"]
        if isinstance(commit_data, str):
            post_data_commit = commit_data

    # Clone the repo
    repo_dir, commit = await loop.run_in_executor(
        None, clone_url, post_data["repository"]["clone_url"], post_data_commit
    )
    venv_name = repo_dir.split("/")[-1]

    # Create new venv
    subprocess.run(
        f'sh -c "python3 -m venv /app/data/docs/venvs/{venv_name}"', shell=True, check=True, capture_output=True
    )

    subprocess.run(
        f'sh -c ". /app/data/docs/venvs/{venv_name}/bin/activate && pip3 install sphinx myst-parser"',
        shell=True,
        capture_output=True,
        check=True,
    )

    language = await detect_language(repo_dir)
    return f"/app/data/docs/venvs/{venv_name}", repo_dir, project_name, commit, language


async def postprocessing(venv_path: str, repo_dir: str, docs_dir: str, project_name: str, commit: str) -> str:
    """Postprocess the doc generation.
    Move the generate docs to storage, remove the cloned down project and its venv.

    Returned str is the path to the generate docs new storage location

    Parameters:
    venv_path str: Path to venv for this project.
    repo_dir str: Path to the cloned down project.
    docs_dir str: Path to the generated docs for this project.
    project_name str: The projects name.
    commit str: The projects commit the generated docs are for.

    Returns:
    str
    """

    await upload_to_docat(f"{docs_dir}", repo_dir, project_name)

    os.makedirs(f"/app/data/docs/final/{project_name}/", exist_ok=True)

    # Remove old generate docs for this commit, will be replaced here below.
    if os.path.isdir(f"/app/data/docs/final/{project_name}/{commit}"):
        shutil.rmtree(f"/app/data/docs/final/{project_name}/{commit}")

    os.rename(docs_dir, f"/app/data/docs/final/{project_name}/{commit}")
    shutil.rmtree(repo_dir)  # remove cloned down repo
    shutil.rmtree(venv_path)  # remove the repos venv

    return f"./data/docs/final/{project_name}/{commit}"
