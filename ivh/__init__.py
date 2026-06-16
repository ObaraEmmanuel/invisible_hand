__version__ = "2026.0.3"

import pathlib

ROOT_DIR = pathlib.Path(__file__).parent.parent.absolute()
MODULE_DIR = ROOT_DIR / "ivh"


def get_resource(name: str) -> pathlib.Path:
    return MODULE_DIR / "resources" / name


def get_layout(name: str) -> pathlib.Path:
    return MODULE_DIR / "layouts" / name
