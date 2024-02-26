import asyncio
import base64
from secrets import token_bytes
from git import Repo

def clone_url(url: str) -> str:
    folder_name = base64.b64encode((token_bytes(16))).hex()
    Repo.clone_from(url, f"/app/pages/generating/{folder_name}")
    return folder_name

async def preprocessing():
    url = "https://github.com/SUNET/python_x509_pkcs11.git"
    loop = asyncio.get_running_loop()
    folder_name = await loop.run_in_executor(None, clone_url, url)
    language = None
    return folder_name
