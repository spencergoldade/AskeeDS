"""Tests for the AskeeDS Loader."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = ROOT / "components"
SCHEMA_PATH = COMPONENTS_DIR / "_schema.yaml"


def test_load_components_dir(components):
    assert isinstance(components, dict)
    assert len(components) == 63


def test_load_tokens_dir(tokens):
    assert "color_roles" in tokens
    assert "sets" in tokens
    assert "bar" in tokens
    assert "conventions" in tokens


def test_component_fields(components):
    comp = components["button.icon"]
    assert comp.name == "button.icon"
    assert comp.category == "core/buttons"
    assert comp.status == "approved"
    assert "label" in comp.props
    assert "icon" in comp.props
    assert comp.props["label"].type == "string"
    assert comp.props["label"].required is True


def test_load_components_from_string(loader):
    yaml_str = """
test.comp:
  category: core/test
  description: A test component.
  status: ideated
  render:
    type: inline
    template: "hello {name}"
  props:
    name:
      type: string
      required: true
"""
    result = loader.load_components(yaml_str)
    assert "test.comp" in result
    assert result["test.comp"].description == "A test component."


def test_load_components_skips_schema(components):
    for name in components:
        assert not name.startswith("_"), f"Loaded schema file as component: {name}"


def test_loader_with_schema_validation():
    from askee_ds import Loader
    validated_loader = Loader(schema_path=SCHEMA_PATH)
    result = validated_loader.load_components_dir(COMPONENTS_DIR)
    assert len(result) == 63
