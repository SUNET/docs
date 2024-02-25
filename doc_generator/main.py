"""Main module, FastAPI runs from here"""
import asyncio
import base64
from secrets import token_bytes
from typing import List

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from git import Repo

from .base import AbstractGenerator
from .startup import generators

doc_generators: List[AbstractGenerator] = generators()
print()
print(f"Loaded {len(doc_generators)} generators", flush=True)


# Create fastapi app
app = FastAPI()


def clone_url(url: str) -> str:
    folder_name = base64.b64encode((token_bytes(16))).hex()
    repo = Repo.clone_from(url, f"/app/pages/generating/{folder_name}")
    return folder_name


@app.post("/test1")
async def post_generator() -> JSONResponse:
    print(f"Received new generate request", flush=True)

    url = "https://github.com/SUNET/python_x509_pkcs11.git"
    loop = asyncio.get_running_loop()
    folder_name = await loop.run_in_executor(None, clone_url, url)
    language = None

    # language = await detect_language(folder_name)

    # Try to find a compatable generator and generate with it
    for generator in doc_generators:
        if await generator.compatable(folder_name, language):
            print(f"Using generator {generator.name()}", flush=True)
            generated_docs_folder = await generator.generate(folder_name)
            break
    else:
        print("Failed to find compatable generator")
        return JSONResponse(status_code=500, content=f"Failed to find compatable generator for project")

    return JSONResponse(status_code=200, content=f"Generated docs folder {generated_docs_folder}")
