from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import List
import glob
import sys
from importlib.util import spec_from_file_location, module_from_spec

from .base import AbstractGenerator

# Load all python files in "generators" folder they must all have a class which implements AbstractGenerator
def generators() -> List[AbstractGenerator]:

    objects: List[AbstractGenerator] = []

    for filename in glob.iglob('src/doc_generator/generators/**/*.py', recursive=True):
        print(filename.split("/")[-1])
        modulename = filename[:-3].split("/")[-1]

        module_spec = spec_from_file_location(modulename, filename)
        if module_spec is None:
            print(f"error loading module from {filename}")
            sys.exit(1)

        module = module_from_spec(module_spec)
        if module_spec.loader is None:
            print(f"error loading module from {filename}")
            sys.exit(1)

        module_spec.loader.exec_module(module)

        obj = getattr(module, "Generator")
        new_obj = obj(modulename)
        objects.append(new_obj)
        print(f"loaded {filename}")

    return objects
