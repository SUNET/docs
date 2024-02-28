import asyncio
import base64
import os
import shutil
from secrets import token_bytes
from typing import Any, Dict

from git import Repo

from doc_generator.base import CodeLanguage


async def detect_language(folder_name: str) -> CodeLanguage | None:
    """FIXME detect language in the repo"""
    return None


def clone_url(url: str, commit: str | None) -> tuple[str, str]:
    folder_path = base64.b64encode((token_bytes(16))).hex()
    repo = Repo.clone_from(url, f"/app/data/docs/generating/{folder_path}")

    # checkout specified commit
    if commit is not None:
        new_head = repo.create_head(f"generating_docs_{folder_path}")
        new_head.set_commit(commit)
        new_head.checkout()

    commit = repo.commit().hexsha
    return f"/app/data/docs/generating/{folder_path}", commit


async def preprocessing(post_data: Dict[str, Any]) -> tuple[str, str, str, CodeLanguage | None]:
    # url = "https://github.com/SUNET/python_x509_pkcs11.git"
    loop = asyncio.get_running_loop()
    repo_name = "fixme"
    post_data_commit = None

    # Better handling of types
    repo_name_data = post_data["repository"].get("name", "FIXME")
    if isinstance(repo_name_data, str):
        repo_name = repo_name_data
    if "head_commit" in post_data:
        commit_data = post_data["head_commit"].get("id", "FIXME")
        if isinstance(commit_data, str):
            post_data_commit = commit_data

    repo_dir, commit = await loop.run_in_executor(
        None, clone_url, post_data["repository"]["clone_url"], post_data_commit
    )
    language = await detect_language(repo_dir)
    return repo_dir, repo_name, commit, language


async def postprocessing(repo_dir: str, docs_dir: str, repo_name: str, commit: str) -> str:
    """
    Postprocessing, currently only moving the generated docs html folder
    and delete the repo folder.
    """

    os.makedirs(f"/app/data/docs/final/{repo_name}/", exist_ok=True)
    os.rename(docs_dir, f"/app/data/docs/final/{repo_name}/{commit}")
    shutil.rmtree(repo_dir)

    return f"/app/data/docs/final/{repo_name}/{commit}"
