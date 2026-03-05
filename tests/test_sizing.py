"""Tests for the declarative sizing model."""

import pytest
from pathlib import Path

from askee_ds.sizing import resolve_width, resolve_height, DEFAULT_WIDTH

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = ROOT / "components"
TOKENS_DIR = ROOT / "tokens"


class TestResolveWidth:
    """resolve_width: spec + available → concrete width."""

    def test_fixed_integer(self):
        assert resolve_width({"width": 44}, available=80) == 44

    def test_fixed_integer_ignores_available(self):
        assert resolve_width({"width": 44}, available=120) == 44

    def test_fill_uses_available(self):
        assert resolve_width({"width": "fill"}, available=100) == 100

    def test_fill_uses_default_when_omitted(self):
        assert resolve_width({"width": "fill"}) == DEFAULT_WIDTH

    def test_content_uses_available_as_upper_bound(self):
        assert resolve_width({"width": "content"}, available=60) == 60

    def test_no_width_uses_available(self):
        assert resolve_width({}, available=80) == 80

    def test_min_width_clamps_fill(self):
        assert resolve_width(
            {"width": "fill", "min_width": 30}, available=20,
        ) == 30

    def test_max_width_clamps_fill(self):
        assert resolve_width(
            {"width": "fill", "max_width": 60}, available=100,
        ) == 60

    def test_min_and_max_width(self):
        spec = {"width": "fill", "min_width": 30, "max_width": 60}
        assert resolve_width(spec, available=50) == 50
        assert resolve_width(spec, available=20) == 30
        assert resolve_width(spec, available=100) == 60

    def test_min_width_on_fixed(self):
        assert resolve_width({"width": 20, "min_width": 30}, available=80) == 30

    def test_max_width_on_fixed(self):
        assert resolve_width({"width": 80, "max_width": 60}, available=80) == 60

    def test_absolute_minimum_enforced(self):
        assert resolve_width({"width": 2}, available=80) == 4

    def test_absolute_minimum_with_fill(self):
        assert resolve_width({"width": "fill"}, available=2) == 4


class TestResolveHeight:
    """resolve_height: spec + content_lines + available → concrete height."""

    def test_content_default(self):
        assert resolve_height({}, content_lines=10) == 10

    def test_content_explicit(self):
        assert resolve_height({"height": "content"}, content_lines=5) == 5

    def test_fixed_integer(self):
        assert resolve_height({"height": 20}, content_lines=10) == 20

    def test_fill_uses_available(self):
        assert resolve_height(
            {"height": "fill"}, content_lines=10, available=24,
        ) == 24

    def test_fill_falls_back_to_content(self):
        assert resolve_height(
            {"height": "fill"}, content_lines=10, available=None,
        ) == 10

    def test_min_height(self):
        assert resolve_height(
            {"min_height": 5}, content_lines=3,
        ) == 5

    def test_max_height(self):
        assert resolve_height(
            {"max_height": 8}, content_lines=20,
        ) == 8

    def test_absolute_minimum_one_line(self):
        assert resolve_height({}, content_lines=0) == 1


class TestBoxSizingIntegration:
    """Box render type uses resolve_width when rendering."""

    @pytest.fixture(scope="class")
    def loader(self):
        from askee_ds import Loader
        return Loader()

    @pytest.fixture(scope="class")
    def theme(self, loader):
        from askee_ds import Theme
        return Theme(loader.load_tokens_dir(TOKENS_DIR))

    @pytest.fixture(scope="class")
    def renderer(self, theme):
        from askee_ds import Renderer
        return Renderer(theme)

    def test_fixed_width_box_unchanged(self, renderer, loader):
        """A box with width: 44 renders identically regardless of available."""
        comps = loader.load_components_dir(COMPONENTS_DIR)
        room = comps.get("room-card.default")
        if room is None:
            pytest.skip("room-card.default not found")
        props = {"title": "Cave", "body": "A dark cave."}
        out_80 = renderer.render(room, props, available_width=80)
        out_120 = renderer.render(room, props, available_width=120)
        assert out_80 == out_120

    def test_fill_width_adapts(self, renderer, theme):
        """A box with width: fill renders wider when available_width grows."""
        from askee_ds.loader import Component

        comp = Component(
            name="test.fill-box",
            category="core",
            status="approved",
            description="Test fill-width box",
            props={"title": {"type": "string"}},
            render={
                "type": "box",
                "width": "fill",
                "border": "single",
                "sections": [
                    {"type": "heading", "template": "{title}"},
                ],
            },
        )
        narrow = renderer.render(comp, {"title": "Hi"}, available_width=30)
        wide = renderer.render(comp, {"title": "Hi"}, available_width=60)

        narrow_width = max(len(line) for line in narrow.splitlines())
        wide_width = max(len(line) for line in wide.splitlines())

        assert narrow_width == 30
        assert wide_width == 60

    def test_fill_with_min_max(self, renderer, theme):
        """Min/max constraints are respected for fill-width boxes."""
        from askee_ds.loader import Component

        comp = Component(
            name="test.constrained-box",
            category="core",
            status="approved",
            description="Test constrained box",
            props={"title": {"type": "string"}},
            render={
                "type": "box",
                "width": "fill",
                "min_width": 30,
                "max_width": 50,
                "border": "single",
                "sections": [
                    {"type": "heading", "template": "{title}"},
                ],
            },
        )
        # Below min — clamps to 30
        too_small = renderer.render(comp, {"title": "Hi"}, available_width=20)
        small_width = max(len(line) for line in too_small.splitlines())
        assert small_width == 30

        # Within range — uses available
        mid = renderer.render(comp, {"title": "Hi"}, available_width=40)
        mid_width = max(len(line) for line in mid.splitlines())
        assert mid_width == 40

        # Above max — clamps to 50
        too_big = renderer.render(comp, {"title": "Hi"}, available_width=80)
        big_width = max(len(line) for line in too_big.splitlines())
        assert big_width == 50


class TestComposerSizingPassthrough:
    """Composer passes available_width through to child renders."""

    @pytest.fixture(scope="class")
    def loader(self):
        from askee_ds import Loader
        return Loader()

    @pytest.fixture(scope="class")
    def theme(self, loader):
        from askee_ds import Theme
        return Theme(loader.load_tokens_dir(TOKENS_DIR))

    @pytest.fixture(scope="class")
    def renderer(self, theme):
        from askee_ds import Renderer
        return Renderer(theme)

    @pytest.fixture(scope="class")
    def components(self, loader):
        return loader.load_components_dir(COMPONENTS_DIR)

    @pytest.fixture(scope="class")
    def composer(self, renderer, components):
        from askee_ds import Composer
        return Composer(renderer, components)

    def test_compose_accepts_available_width(self, composer, components):
        """Composer.compose() runs without error when given available_width."""
        stack_comp = components.get("layout.stack")
        if stack_comp is None:
            pytest.skip("layout.stack not found")
        result = composer.compose(
            "layout.stack",
            {"blocks": ["Block A", "Block B"]},
            available_width=60,
        )
        assert isinstance(result, str)
        assert len(result) > 0
