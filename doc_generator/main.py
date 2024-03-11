"""Main module, FastAPI runs from here"""

import os
import shutil

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .base import AbstractGenerator
from .lib import postprocessing, preprocessing
from .startup import load_generators

doc_generators: list[AbstractGenerator] = load_generators()
print()
print(f"Loaded {len(doc_generators)} generators", flush=True)

# Create fastapi app
app = FastAPI()


@app.post("/git_repo")
async def post_generator(req: Request) -> JSONResponse:
    """HTTP POST endpoint. It should contain a json body
    with the same or a subset of keys that a github webhook has
    """

    # Reset cwd
    os.chdir("/app")

    post_data = await req.json()  # Check for valid data
    # print(json.dumps(post_data))

    if "repository" not in post_data or "clone_url" not in post_data["repository"]:
        return JSONResponse(status_code=200, content='Nothing to do, no \'"repository"["clone_url"]\' in post data')

    # Preprocess (clone down, detect language) the project
    venv_path, repo_dir, project_name, commit, language = await preprocessing(post_data)
    print(f"Received new generate request for project {project_name}", flush=True)

    # If docs for this commit already has been generated
    if os.path.isdir(f"/app/data/docs/final/{project_name}/{commit}"):
        print("Docs for this commit already exists")
        shutil.rmtree(repo_dir)  # Remove cloned down repo
        return JSONResponse(status_code=200, content="Docs for this commit already exists")

    # Try to find a compatable generator and generate with it
    for generator in doc_generators:
        if await generator.compatable(venv_path, repo_dir, project_name, language):
            # Use the compatable generator to generate docs
            print(f"Using generator {generator.name()}", flush=True)
            generated_docs_dir = await generator.generate(venv_path, repo_dir, project_name, language)
            break
    else:
        print("Failed to find compatable generator")
        return JSONResponse(status_code=200, content="Failed to find compatable generator for project")

    # Generated docs. Time to postprocess
    finalized_docs_folder = await postprocessing(venv_path, repo_dir, generated_docs_dir, project_name, commit)

    return JSONResponse(status_code=201, content=f"Generated docs folder {finalized_docs_folder}")
