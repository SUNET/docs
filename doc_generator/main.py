"""Main module, FastAPI runs from here"""

from typing import List

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from .base import AbstractGenerator
from .lib import preprocessing
from .startup import load_generators

doc_generators: List[AbstractGenerator] = load_generators()
print()
print(f"Loaded {len(doc_generators)} generators", flush=True)

# Create fastapi app
app = FastAPI()


@app.post("/test1")
async def post_generator(req: Request) -> JSONResponse:
    print(f"Received new generate request", flush=True)
    post_data = await req.json()  # Check for valid data

    # Preprocess (clone down, detect language) the project
    folder_name, language = await preprocessing(post_data)

    # Try to find a compatable generator and generate with it
    for generator in doc_generators:
        if await generator.compatable(folder_name, language):
            # Use the compatable generator to generate docs
            print(f"Using generator {generator.name()}", flush=True)
            generated_docs_folder = await generator.generate(folder_name)
            break
    else:
        print("Failed to find compatable generator")
        return JSONResponse(status_code=500, content=f"Failed to find compatable generator for project")

    return JSONResponse(status_code=200, content=f"Generated docs folder {generated_docs_folder}")
