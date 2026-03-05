"""Tests for the interaction spec system."""

import pytest
from pathlib import Path

from askee_ds import Loader, Validator
from askee_ds.loader import Component

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = ROOT / "components"
TOKENS_DIR = ROOT / "tokens"
SCHEMA_PATH = COMPONENTS_DIR / "_schema.yaml"


@pytest.fixture(scope="module")
def loader():
    return Loader()


@pytest.fixture(scope="module")
def components(loader):
    return loader.load_components_dir(COMPONENTS_DIR)


@pytest.fixture(scope="module")
def validator():
    return Validator.from_schema_file(SCHEMA_PATH)


class TestInteractionLoading:
    """Loader correctly parses interaction specs from YAML."""

    def test_button_has_interaction(self, components):
        btn = components["button.text"]
        assert btn.interaction.get("focusable") is True

    def test_button_icon_has_interaction(self, components):
        btn = components["button.icon"]
        assert btn.interaction.get("focusable") is True
        actions = btn.interaction.get("actions", [])
        assert len(actions) == 1
        assert actions[0]["name"] == "activate"

    def test_choice_wheel_has_navigation(self, components):
        wheel = components["choice-wheel.inline"]
        assert wheel.interaction.get("focusable") is True
        actions = wheel.interaction.get("actions", [])
        action_names = [a["name"] for a in actions]
        assert "select_next" in action_names
        assert "select_prev" in action_names
        assert "confirm" in action_names

    def test_display_only_has_no_interaction(self, components):
        status = components["status-bar.default"]
        assert status.interaction == {}

    def test_interaction_defaults_to_empty(self):
        comp = Component(
            name="test.no-interaction",
            category="core",
            status="approved",
            description="No interaction block",
            props={},
            render={"type": "inline", "template": "hello"},
        )
        assert comp.interaction == {}


class TestInteractionValidation:
    """Validator catches invalid interaction specs."""

    def test_valid_interaction_passes(self, validator):
        comp = Component(
            name="test.valid-interaction",
            category="core/buttons",
            status="approved",
            description="Button with valid interaction",
            props={},
            render={"type": "inline", "template": "[ OK ]"},
            interaction={
                "focusable": True,
                "actions": [
                    {"name": "activate", "keys": ["enter", "space"]},
                ],
            },
        )
        errors = validator.validate(comp)
        assert len(errors) == 0

    def test_invalid_interaction_field(self, validator):
        comp = Component(
            name="test.bad-field",
            category="core/buttons",
            status="approved",
            description="Unknown interaction field",
            props={},
            render={"type": "inline", "template": "x"},
            interaction={"focusable": True, "unknown_field": "bad"},
        )
        errors = validator.validate(comp)
        field_errors = [e for e in errors if "unknown_field" in e[1]]
        assert len(field_errors) == 1

    def test_focusable_must_be_bool(self, validator):
        comp = Component(
            name="test.bad-focusable",
            category="core/buttons",
            status="approved",
            description="focusable is not bool",
            props={},
            render={"type": "inline", "template": "x"},
            interaction={"focusable": "yes"},
        )
        errors = validator.validate(comp)
        focusable_errors = [e for e in errors if "focusable" in e[1]]
        assert len(focusable_errors) == 1

    def test_action_missing_name(self, validator):
        comp = Component(
            name="test.bad-action",
            category="core/buttons",
            status="approved",
            description="Action without name",
            props={},
            render={"type": "inline", "template": "x"},
            interaction={
                "focusable": True,
                "actions": [{"keys": ["enter"]}],
            },
        )
        errors = validator.validate(comp)
        name_errors = [e for e in errors if "missing 'name'" in e[1]]
        assert len(name_errors) == 1

    def test_invalid_key_value(self, validator):
        comp = Component(
            name="test.bad-key",
            category="core/buttons",
            status="approved",
            description="Invalid key name",
            props={},
            render={"type": "inline", "template": "x"},
            interaction={
                "focusable": True,
                "actions": [
                    {"name": "activate", "keys": ["enter", "ctrl+z"]},
                ],
            },
        )
        errors = validator.validate(comp)
        key_errors = [e for e in errors if "ctrl+z" in e[1]]
        assert len(key_errors) == 1

    def test_all_approved_components_validate(self, validator, components):
        """Every approved component with interaction metadata passes validation."""
        errors = validator.validate_all(components)
        assert len(errors) == 0
