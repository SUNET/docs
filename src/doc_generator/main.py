"""Main module, FastAPI runs from here"""
import asyncio
import base64
import hashlib
import os
from secrets import token_bytes
from typing import Dict, Union

from cryptography.exceptions import InvalidSignature
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.background import BackgroundTasks
from fastapi.responses import JSONResponse

from git import Repo

from .docs_folder import generate

# from .config import ACME_ROOT, KEY_TYPES, PKCS11_SIGN_API_TOKEN, ROOT_URL

# from .startup import startup

#if "_" in os.environ and "sphinx-build" in os.environ["_"]:
#    print("Running sphinx build")
#else:
#    loop = asyncio.get_running_loop()
#    startup_task = loop.create_task(startup())




# Create fastapi app
app = FastAPI()


def clone_url(url: str):
    folder_name = base64.b64encode((token_bytes(32))).hex()
    repo = Repo.clone_from(url, f"/app/pages/generating/{folder_name}")
    return folder_name


@app.post("/test1")
async def post_generator() -> JSONResponse:
    """ACME POST directory endpoint

    Returns:
    Response
    """


    url = "https://github.com/SUNET/python_x509_pkcs11.git"
    loop = asyncio.get_running_loop()
    folder_name = await loop.run_in_executor(None, clone_url, url)

    await generate(folder_name)


    return JSONResponse(status_code=200, content=f"{folder_name}")
