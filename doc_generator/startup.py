"""Module for startup functions"""

import glob
import sys
from importlib.util import module_from_spec, spec_from_file_location

from .base import AbstractGenerator


def load_generators() -> list[AbstractGenerator]:
    """Load doc generators from all python files in the generators folder
    they must all have a class called 'Generator' which implements AbstractGenerator
    FIXME validate the python file and Generator class.

    Returns:
    list[AbstractGenerator]

    """

    objects: list[AbstractGenerator] = []

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

        generator_class = getattr(module, "Generator")
        class_object: AbstractGenerator = generator_class(
            generator_class.generator_name, generator_class.generator_language, generator_class.generator_priority
        )
        objects.append(class_object)
        print(f"loaded generator {class_object.name()} from {filename}")

    # Sort on priority
    objects = sorted(objects, key=lambda obj: obj.generator_priority)

    return objects
