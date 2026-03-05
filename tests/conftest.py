"""Shared fixtures for the AskeeDS test suite."""

import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = ROOT / "components"
TOKENS_DIR = ROOT / "tokens"
SCHEMA_PATH = COMPONENTS_DIR / "_schema.yaml"
DECORATIONS_PATH = ROOT / "decorations" / "catalog.yaml"


@pytest.fixture(scope="session")
def loader():
    from askee_ds import Loader
    return Loader()


@pytest.fixture(scope="session")
def components(loader):
    return loader.load_components_dir(COMPONENTS_DIR)


@pytest.fixture(scope="session")
def tokens(loader):
    return loader.load_tokens_dir(TOKENS_DIR)


@pytest.fixture(scope="session")
def theme(tokens):
    from askee_ds import Theme
    return Theme(tokens)


@pytest.fixture(scope="session")
def renderer(theme):
    from askee_ds import Renderer
    return Renderer(theme)


@pytest.fixture(scope="session")
def composer(renderer, components):
    from askee_ds import Composer
    return Composer(renderer, components)


@pytest.fixture(scope="session")
def validator():
    from askee_ds import Validator
    return Validator.from_schema_file(SCHEMA_PATH)
