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


def clone_url(url: str) -> tuple[str, str]:
    folder_path = base64.b64encode((token_bytes(16))).hex()
    repo = Repo.clone_from(url, f"/app/data/docs/generating/{folder_path}")
    commit = repo.commit().hexsha
    return folder_path, commit


async def preprocessing(post_data: Dict[str, Any]) -> tuple[str, str, str, CodeLanguage | None]:
    # url = "https://github.com/SUNET/python_x509_pkcs11.git"
    loop = asyncio.get_running_loop()
    repo_name = "FIXME_TYPES_HERE"
    repo_name_data = post_data["repository"].get("name", "FIXME")
    if isinstance(repo_name_data, str):
        repo_name = repo_name_data

    repo_dir, commit = await loop.run_in_executor(None, clone_url, post_data["repository"]["clone_url"])
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
