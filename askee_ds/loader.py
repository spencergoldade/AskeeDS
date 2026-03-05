"""
Load AskeeDS component definitions and tokens from YAML.

The Loader reads YAML files (individual or directories of them) and returns
Component objects that the Renderer can consume. Tokens are loaded into plain
dicts that the Theme wraps.

    from askee_ds import Loader

    loader = Loader()
    components = loader.load_components_dir("components/")
    tokens = loader.load_tokens_dir("tokens/")

Enable validation warnings at load time:

    loader = Loader(schema_path="components/_schema.yaml")
    components = loader.load_components_dir("components/")
    # Any schema violations print to stderr as warnings.
"""

from __future__ import annotations

import sys
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .validator import Validator


@dataclass
class PropDef:
    name: str
    type: str
    required: bool = True
    element: Optional[dict] = None


@dataclass
class Component:
    name: str
    category: str
    description: str
    status: str
    props: dict[str, PropDef]
    render: dict
    art: str = ""
    default_color_role: str = "neutral"


class Loader:

    def __init__(self, schema_path: str | Path | None = None):
        self._validator: Validator | None = None
        if schema_path is not None:
            from .validator import Validator
            self._validator = Validator.from_schema_file(schema_path)

    def load_components(self, source: str) -> dict[str, Component]:
        """Parse a YAML string containing one or more component definitions."""
        raw = yaml.safe_load(source)
        if not raw or not isinstance(raw, dict):
            return {}
        components: dict[str, Component] = {}
        for name, defn in raw.items():
            if not isinstance(defn, dict):
                continue
            props = self._parse_props(defn.get("props", {}))
            components[name] = Component(
                name=name,
                category=defn.get("category", ""),
                description=defn.get("description", ""),
                status=defn.get("status", ""),
                props=props,
                render=defn.get("render", {}),
                art=defn.get("art", ""),
                default_color_role=defn.get("default_color_role", "neutral"),
            )
        if self._validator:
            self._warn_on_errors(components)
        return components

    def load_components_dir(self, path: str | Path) -> dict[str, Component]:
        """Load all .yaml files under a directory tree."""
        root = Path(path)
        all_components: dict[str, Component] = {}
        for f in sorted(root.rglob("*.yaml")):
            if f.name.startswith("_"):
                continue
            all_components.update(self.load_components(f.read_text()))
        return all_components

    def load_tokens(self, source: str) -> dict:
        """Parse a YAML string containing token definitions."""
        return yaml.safe_load(source) or {}

    def load_tokens_dir(self, path: str | Path) -> dict:
        """Load and merge all token YAML files under a directory."""
        root = Path(path)
        merged: dict = {}
        for f in sorted(root.rglob("*.yaml")):
            data = yaml.safe_load(f.read_text())
            if data and isinstance(data, dict):
                merged.update(data)
        return merged

    def _warn_on_errors(self, components: dict[str, Component]) -> None:
        assert self._validator is not None
        errors = self._validator.validate_all(components)
        for name, msg in errors:
            print(f"Warning [{name}]: {msg}", file=sys.stderr)

    @staticmethod
    def _parse_props(raw: dict) -> dict[str, PropDef]:
        if not raw or not isinstance(raw, dict):
            return {}
        props: dict[str, PropDef] = {}
        for pname, pdef in raw.items():
            if isinstance(pdef, dict):
                props[pname] = PropDef(
                    name=pname,
                    type=pdef.get("type", "string"),
                    required=pdef.get("required", True),
                    element=pdef.get("element"),
                )
            else:
                props[pname] = PropDef(name=pname, type=str(pdef))
        return props
