"""
AskeeDS schema validator — checks component definitions against _schema.yaml.

Reads the meta-schema from components/_schema.yaml and validates loaded
component dicts for structural correctness: required fields, allowed values,
prop shapes, and render spec integrity.

    from askee_ds import Loader, Validator

    loader = Loader()
    components = loader.load_components_dir("components/")
    validator = Validator.from_schema_file("components/_schema.yaml")
    errors = validator.validate_all(components)
    for name, msg in errors:
        print(f"{name}: {msg}")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .loader import Component


class Validator:
    """Validates Component objects against the AskeeDS meta-schema."""

    def __init__(self, schema: dict):
        comp = schema.get("component", {})
        self._required_fields = set(comp.get("required_fields", []))
        self._optional_fields = set(comp.get("optional_fields", []))
        self._all_fields = self._required_fields | self._optional_fields | {"props"}
        self._status_values = set(comp.get("status_values", []))
        self._category_prefixes = list(comp.get("category_prefixes", []))

        prop = schema.get("prop", {})
        self._prop_required_fields = set(prop.get("required_fields", []))
        self._prop_type_values = set(prop.get("type_values", []))
        self._prop_optional_fields = set(prop.get("optional_fields", []))

        self._color_role_values = set(comp.get("color_role_values", []))

        render = schema.get("render", {})
        self._render_type_values = set(render.get("type_values", []))
        self._section_types = set(render.get("section_types", []))
        self._border_values = set(render.get("border_values", []))

        interaction = schema.get("interaction", {})
        self._interaction_fields = set(interaction.get("optional_fields", []))
        self._interaction_key_values = set(interaction.get("key_values", []))

    @classmethod
    def from_schema_file(cls, path: str | Path) -> "Validator":
        """Load a validator from a _schema.yaml file."""
        text = Path(path).read_text(encoding="utf-8")
        schema = yaml.safe_load(text) or {}
        return cls(schema)

    def validate(self, component: Component) -> list[tuple[str, str]]:
        """Validate a single Component. Returns (name, error) tuples."""
        errors: list[tuple[str, str]] = []
        name = component.name

        if not component.category:
            errors.append((name, "missing required field: category"))
        elif not any(
            component.category.startswith(p) for p in self._category_prefixes
        ):
            errors.append(
                (name, f"category '{component.category}' does not start "
                       f"with an allowed prefix: {self._category_prefixes}")
            )

        if not component.description:
            errors.append((name, "missing required field: description"))

        if not component.status:
            errors.append((name, "missing required field: status"))
        elif component.status not in self._status_values:
            errors.append(
                (name, f"invalid status '{component.status}'; "
                       f"allowed: {sorted(self._status_values)}")
            )

        if component.default_color_role != "neutral" and self._color_role_values:
            if component.default_color_role not in self._color_role_values:
                errors.append(
                    (name, f"default_color_role '{component.default_color_role}' "
                           f"is not valid; allowed: {sorted(self._color_role_values)}")
                )

        if not component.render:
            errors.append((name, "missing required field: render"))
        else:
            errors.extend(self._validate_render(name, component.render))

        for pname, pdef in component.props.items():
            errors.extend(self._validate_prop(name, pname, pdef))

        if component.interaction:
            errors.extend(self._validate_interaction(name, component.interaction))

        return errors

    def validate_all(
        self, components: dict[str, Component]
    ) -> list[tuple[str, str]]:
        """Validate every component in a dict. Returns all (name, error) tuples."""
        errors: list[tuple[str, str]] = []
        for comp in components.values():
            errors.extend(self.validate(comp))
        return errors

    def _validate_prop(
        self, comp_name: str, prop_name: str, pdef: Any
    ) -> list[tuple[str, str]]:
        errors: list[tuple[str, str]] = []
        if pdef.type not in self._prop_type_values:
            errors.append(
                (comp_name, f"prop '{prop_name}' has invalid type "
                            f"'{pdef.type}'; allowed: {sorted(self._prop_type_values)}")
            )
        return errors

    def _validate_render(
        self, comp_name: str, render: dict
    ) -> list[tuple[str, str]]:
        errors: list[tuple[str, str]] = []
        rtype = render.get("type", "")

        if rtype not in self._render_type_values:
            errors.append(
                (comp_name, f"render type '{rtype}' is not valid; "
                            f"allowed: {sorted(self._render_type_values)}")
            )
            return errors

        if rtype == "box":
            border = render.get("border", "single")
            if border not in self._border_values:
                errors.append(
                    (comp_name, f"border style '{border}' is not valid; "
                                f"allowed: {sorted(self._border_values)}")
                )
            for i, section in enumerate(render.get("sections", [])):
                stype = section.get("type", "")
                if stype not in self._section_types:
                    errors.append(
                        (comp_name, f"section[{i}] type '{stype}' is not "
                                    f"valid; allowed: {sorted(self._section_types)}")
                    )

        return errors

    def _validate_interaction(
        self, comp_name: str, interaction: dict,
    ) -> list[tuple[str, str]]:
        errors: list[tuple[str, str]] = []

        for key in interaction:
            if key not in self._interaction_fields:
                errors.append(
                    (comp_name, f"interaction field '{key}' is not valid; "
                                f"allowed: {sorted(self._interaction_fields)}")
                )

        focusable = interaction.get("focusable")
        if focusable is not None and not isinstance(focusable, bool):
            errors.append(
                (comp_name, "interaction.focusable must be a boolean")
            )

        for i, action in enumerate(interaction.get("actions", [])):
            if not isinstance(action, dict):
                errors.append(
                    (comp_name, f"interaction.actions[{i}] must be a dict")
                )
                continue
            if "name" not in action:
                errors.append(
                    (comp_name, f"interaction.actions[{i}] missing 'name'")
                )
            if self._interaction_key_values:
                for key in action.get("keys", []):
                    if key not in self._interaction_key_values:
                        errors.append(
                            (comp_name,
                             f"interaction.actions[{i}] key '{key}' "
                             f"is not valid; allowed: "
                             f"{sorted(self._interaction_key_values)}")
                        )

        return errors
