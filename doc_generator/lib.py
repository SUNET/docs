import asyncio
import base64
from secrets import token_bytes
from typing import Any, Dict

from git import Repo

from doc_generator.base import CodeLanguage


async def detect_language(folder_name: str) -> CodeLanguage | None:
    """FIXME detect language in the repo"""
    return None


def clone_url(url: str) -> str:
    folder_name = base64.b64encode((token_bytes(16))).hex()
    Repo.clone_from(url, f"/app/pages/generating/{folder_name}")
    return folder_name


async def preprocessing(post_data: Dict[str, Any]) -> tuple[str, CodeLanguage | None]:
    # url = "https://github.com/SUNET/python_x509_pkcs11.git"
    loop = asyncio.get_running_loop()
    folder_name = await loop.run_in_executor(None, clone_url, post_data["clone_url"])
    language = await detect_language(folder_name)
    return folder_name, language
