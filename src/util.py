"""Set of functions used in the project."""

import json
import os

OUTPUT_FOLDER = "./output"


def get_variable(env_var: str) -> str:
    """Get the value of the environment variable."""
    value = os.environ.get(env_var)
    if value is None:
        with open(".env", "r") as file_p:
            for line in file_p:
                if line.startswith(env_var):
                    return line.split("=")[1].strip()
        raise ValueError(f"Please set the {env_var} environment variable.")
    return value


def create_folders(filename: str) -> None:
    """Create the folders for the output."""
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def get_contents(filename: str) -> list:
    """Open the file. If file does not exist, create it."""
    create_folders(filename)
    items = []
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file_p:
            items = json.load(file_p)
    return items


def set_contents(filename: str, items: list, remove_old: bool = False) -> None:
    """Store the items in a json file."""
    create_folders(filename)

    if remove_old and os.path.exists(filename):
        os.remove(filename)

    with open(filename, "w", encoding="utf-8") as file_p:
        json.dump(items, file_p, indent=2)
