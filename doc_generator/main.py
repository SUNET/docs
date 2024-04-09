"""Main module, FastAPI runs from here"""

import asyncio
import os
import secrets
import shutil
import random

import motor.motor_asyncio
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .base import AbstractGenerator
from .conf import GITHUB_PAT, orgs
from .lib import postprocessing, preprocessing
from .startup import load_generators

doc_generators: list[AbstractGenerator] = load_generators()
print()
print(f"Loaded {len(doc_generators)} generators", flush=True)


# Create fastapi app
app = FastAPI()


async def background_discover_projects() -> None:
    """Discover new projects in the background"""

    # FIXME automaticly find out number of repos in org

    mongodb_client = motor.motor_asyncio.AsyncIOMotorClient("mongodb", 27017)
    db = mongodb_client["docs"]
    collection = db["projects"]

    while True:
        for org in orgs:
            for page in range(1, orgs[org] + 1):
                await asyncio.sleep(0)
                headers = {
                    "Accept": "application/vnd.github+json",
                    "Authorization": GITHUB_PAT,
                    "X-GitHub-Api-Version": "2022-11-28",
                }
                req = requests.get(
                    f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}", headers=headers, timeout=10
                )

                repos = req.json()
                for repo in repos:
                    if "language" in repo and repo["language"] == "Python":
                        old_document = await collection.find_one({"clone_url": repo["clone_url"]})
                        if old_document is None:
                            await collection.insert_one(
                                {"name": repo["name"], "clone_url": repo["clone_url"], "language": "python"}
                            )
                            print(
                                f"Discovered and inserted project {repo['name']} into db page {page} org {org}",
                                flush=True,
                            )

        await asyncio.sleep(60 * 60 * 24)  # 60*60*24 for 24 hours


async def background_update_projects() -> None:
    """Process all projects in database continuously in the background"""

    while True:
        # Assuming python language for project, fix to work for puppet as well
        print("FIXME only one background instead of one for all uvicorn workers")
        print("Updating docs for all repos", flush=True)

        mongodb_client = motor.motor_asyncio.AsyncIOMotorClient("mongodb", 27017)
        db = mongodb_client["docs"]
        collection = db["projects"]

        cursor = collection.find()

        projects = await cursor.to_list(length=5000)
        random.shuffle(projects)

        for doc in projects:
            print(f"background running for {doc['name']}", flush=True)

            post_data = {"repository": {"name": doc["name"], "clone_url": doc["clone_url"]}}
            venv_path, repo_dir, project_name, commit, language = await preprocessing(post_data)

            # If docs for this commit already has been generated
            if os.path.isdir(f"/app/data/docs/final/{project_name}/{commit}"):
                print("Docs for this commit already exists")
                shutil.rmtree(repo_dir)  # Remove cloned down repo
                continue

            # Try to find a compatable generator and generate with it
            for generator in doc_generators:
                if await generator.compatable(venv_path, repo_dir, project_name, language):
                    # Use the compatable generator to generate docs
                    print(f"Using generator {generator.name()}", flush=True)
                    generated_docs_dir = await generator.generate(venv_path, repo_dir, project_name, language)
                    break
            else:
                print("Failed to find compatable generator", flush=True)
                continue

            # Generated docs. Time to postprocess
            await postprocessing(venv_path, repo_dir, generated_docs_dir, project_name, commit)
            print(f"background finished for {doc['name']}")

        await asyncio.sleep(60 * 60 * 24)  # 60*60*24 for 24 hours

        # document = {"clone_url": "value", "kkey": "vvalue"}
        # result = await collection.insert_one(document)
        # print("result %s" % repr(result.inserted_id))
        # await asyncio.sleep(10)


@app.on_event("startup")
async def app_startup() -> None:
    """Create our background process"""
    asyncio.create_task(background_update_projects())
    asyncio.create_task(background_discover_projects())


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

    print(f"Received new generate request for url {post_data['repository']['clone_url']}", flush=True)

    # Preprocess (clone down, detect language) the project
    venv_path, repo_dir, project_name, commit, language = await preprocessing(post_data)

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

    mongodb_client = motor.motor_asyncio.AsyncIOMotorClient("mongodb", 27017)
    db = mongodb_client["docs"]
    collection = db["projects"]

    old_document = await collection.find_one({"clone_url": post_data["repository"]["clone_url"]})
    if old_document is None:
        await collection.insert_one(
            {"name": project_name, "clone_url": post_data["repository"]["clone_url"], "language": "python"}
        )
        print(f"inserted project {project_name} into db")

    return JSONResponse(status_code=201, content=f"Generated docs folder {finalized_docs_folder}")
