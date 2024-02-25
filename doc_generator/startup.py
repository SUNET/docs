import glob
import sys
from importlib.util import module_from_spec, spec_from_file_location
from typing import List

from .base import AbstractGenerator


# Load all python files in "generators" folder they must all have a class which implements AbstractGenerator
def generators() -> List[AbstractGenerator]:
    objects: List[AbstractGenerator] = []

    for filename in glob.iglob("doc_generator/generators/**/*.py", recursive=True):
        modulename = filename[:-3].split("/")[-1]
        if not modulename.startswith("generator_"):
            continue

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
        new_obj = obj(obj.generator_name, obj.generator_language, obj.generator_priority)
        objects.append(new_obj)
        print(f"loaded generator {obj.generator_name} from {filename}")

    return objects
