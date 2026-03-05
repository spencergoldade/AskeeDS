"""Tests for declarative screen composition."""

import pytest
import tempfile
from pathlib import Path

from askee_ds import Loader, Theme, Renderer, Composer

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = ROOT / "components"
TOKENS_DIR = ROOT / "tokens"
SCREENS_DIR = ROOT / "screens"
EXAMPLE_SCREEN = SCREENS_DIR / "examples" / "adventure_main.yaml"


@pytest.fixture(scope="module")
def composer():
    loader = Loader()
    components = loader.load_components_dir(COMPONENTS_DIR)
    tokens = loader.load_tokens_dir(TOKENS_DIR)
    theme = Theme(tokens)
    renderer = Renderer(theme)
    return Composer(renderer, components)


class TestComposeScreen:
    """Composer.compose_screen loads and renders screen YAML files."""

    def test_adventure_main_renders(self, composer):
        output = composer.compose_screen(EXAMPLE_SCREEN)
        assert isinstance(output, str)
        assert len(output) > 0

    def test_adventure_main_contains_components(self, composer):
        output = composer.compose_screen(EXAMPLE_SCREEN)
        assert "The Undercroft" in output
        assert "HP: 85/100" in output
        assert "rusty key" in output

    def test_width_override(self, composer):
        narrow = composer.compose_screen(EXAMPLE_SCREEN, available_width=50)
        wide = composer.compose_screen(EXAMPLE_SCREEN, available_width=80)
        narrow_max = max(len(line) for line in narrow.splitlines())
        wide_max = max(len(line) for line in wide.splitlines())
        assert wide_max >= narrow_max

    def test_missing_layout_raises(self, composer):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("name: bad\ndescription: no layout\nslots: {}\n")
            f.flush()
            with pytest.raises(ValueError, match="missing 'layout'"):
                composer.compose_screen(f.name)

    def test_unknown_component_raises(self, composer):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                "name: bad\n"
                "description: bad ref\n"
                "layout: layout.stack\n"
                "slots:\n"
                "  blocks:\n"
                "    - component: nonexistent.widget\n"
                "      props: {}\n"
            )
            f.flush()
            with pytest.raises(ValueError, match="nonexistent.widget"):
                composer.compose_screen(f.name)

    def test_text_slot_entry(self, composer):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                "name: text-test\n"
                "description: text entry\n"
                "layout: layout.stack\n"
                "slots:\n"
                "  blocks:\n"
                "    - text: Hello World\n"
            )
            f.flush()
            output = composer.compose_screen(f.name)
            assert "Hello World" in output

    def test_nested_layout(self, composer):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                "name: nested-test\n"
                "description: nested layout\n"
                "layout: layout.stack\n"
                "slots:\n"
                "  blocks:\n"
                "    - component: layout.stack\n"
                "      slots:\n"
                "        blocks:\n"
                "          - text: Inner content\n"
            )
            f.flush()
            output = composer.compose_screen(f.name)
            assert "Inner content" in output


class TestComposeCLI:
    """CLI compose subcommand."""

    def test_compose_help(self):
        from askee_ds.cli import main
        with pytest.raises(SystemExit):
            main(["compose", "--help"])

    def test_compose_missing_file(self):
        from askee_ds.cli import main
        result = main(["compose", "nonexistent.yaml"])
        assert result == 1

    def test_compose_adventure_main(self, capsys):
        from askee_ds.cli import main
        result = main(["compose", str(EXAMPLE_SCREEN)])
        assert result == 0
        captured = capsys.readouterr()
        assert "The Undercroft" in captured.out

    def test_compose_with_width(self, capsys):
        from askee_ds.cli import main
        result = main(["compose", str(EXAMPLE_SCREEN), "--width", "60"])
        assert result == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0
