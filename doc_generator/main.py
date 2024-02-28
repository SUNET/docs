"""Main module, FastAPI runs from here"""

import json
import os
from typing import List

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from .base import AbstractGenerator
from .lib import postprocessing, preprocessing
from .startup import load_generators

doc_generators: List[AbstractGenerator] = load_generators()
print()
print(f"Loaded {len(doc_generators)} generators", flush=True)

# Create fastapi app
app = FastAPI()


@app.post("/git_repo")
async def post_generator(req: Request) -> JSONResponse:
    print(f"Received new generate request", flush=True)
    post_data = await req.json()  # Check for valid data
    # print(json.dumps(post_data))

    if "repository" not in post_data or "clone_url" not in post_data["repository"]:
        return JSONResponse(status_code=200, content=f"Nothing to do, no 'clone_url' in post data")

    # Preprocess (clone down, detect language) the project
    repo_dir, repo_name, commit, language = await preprocessing(post_data)

    # If docs for this commit already has been generated
    if os.path.isdir(f"/app/data/docs/final/{repo_name}/{commit}"):
        print("Docs for this commit already exists")
        return JSONResponse(status_code=200, content=f"Docs for this commit already exists")

    # Try to find a compatable generator and generate with it
    for generator in doc_generators:
        if await generator.compatable(repo_dir, language):
            # Use the compatable generator to generate docs
            print(f"Using generator {generator.name()}", flush=True)
            generated_docs_dir = await generator.generate(repo_dir)
            break
    else:
        print("Failed to find compatable generator")
        return JSONResponse(status_code=500, content=f"Failed to find compatable generator for project")

    # Generated docs. Time to postprocess
    finalized_docs_folder = await postprocessing(repo_dir, generated_docs_dir, repo_name, commit)

    return JSONResponse(status_code=201, content=f"Generated docs folder {finalized_docs_folder}")
