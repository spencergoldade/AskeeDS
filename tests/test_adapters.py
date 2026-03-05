"""Tests for AskeeDS Rich and Textual adapters."""


class TestRichAdapter:

    def test_colorize_returns_rich_text(self, renderer, components, theme):
        from askee_ds.adapters.rich import RichAdapter
        from rich.text import Text

        adapter = RichAdapter(theme)
        output = renderer.render(components["button.text"], {"label": "Click"})
        result = adapter.colorize(output, "neutral")
        assert isinstance(result, Text)
        assert "Click" in result.plain

    def test_colorize_with_different_roles(self, theme):
        from askee_ds.adapters.rich import RichAdapter

        adapter = RichAdapter(theme)
        output = "+---+\n| A |\n+---+"
        for role in ("neutral", "danger", "dungeon", "arcane"):
            result = adapter.colorize(output, role)
            assert result.plain == output

    def test_render_component_shortcut(self, renderer, components, theme):
        from askee_ds.adapters.rich import RichAdapter
        from rich.text import Text

        adapter = RichAdapter(theme)
        comp = components["status-bar.default"]
        result = adapter.render_component(renderer, comp, {
            "hp_current": 5, "hp_max": 10,
            "location": "Test", "turn_count": 1,
        })
        assert isinstance(result, Text)
        assert "HP:" in result.plain

    def test_colorize_preserves_all_characters(self, theme):
        from askee_ds.adapters.rich import RichAdapter

        adapter = RichAdapter(theme)
        original = "+-|\n| x |\n+-+"
        result = adapter.colorize(original, "neutral")
        assert result.plain == original


class TestTextualAdapter:

    def test_from_component_creates_widget(self, renderer, components, theme):
        from askee_ds.adapters.textual import AskeeWidget

        widget = AskeeWidget.from_component(
            renderer, components["status-bar.default"],
            props={"hp_current": 5, "hp_max": 10,
                   "location": "Test", "turn_count": 1},
            theme=theme, color_role="neutral",
        )
        assert isinstance(widget, AskeeWidget)

    def test_from_text_creates_widget(self, theme):
        from askee_ds.adapters.textual import AskeeWidget

        widget = AskeeWidget.from_text(
            "+---+\n| A |\n+---+", theme, "danger",
        )
        assert isinstance(widget, AskeeWidget)
