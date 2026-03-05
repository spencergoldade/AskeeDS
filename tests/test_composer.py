"""Tests for the AskeeDS Composer."""

import pytest


def test_compose_stack_with_children(composer):
    output = composer.compose("layout.stack", {
        "blocks": [
            ("status-bar.default", {
                "hp_current": 10, "hp_max": 10,
                "location": "Test", "turn_count": 1,
            }),
            "plain string block",
        ],
    })
    assert "HP: 10/10" in output
    assert "plain string block" in output


def test_compose_columns_with_children(composer):
    output = composer.compose("layout.two-column", {
        "left_content": ("breadcrumb.inline", {
            "segments": [{"label": "A"}, {"label": "B"}],
        }),
        "right_content": "static text",
        "left_width": 15,
    })
    assert "A" in output
    assert "static text" in output


def test_compose_shell_with_children(composer):
    output = composer.compose("layout.app.shell", {
        "header": ("header.banner", {"title": "Test App"}),
        "sidebar": "Nav",
        "content": "Content",
        "sidebar_width": 10,
    })
    assert "Test App" in output
    assert "Nav" in output
    assert "Content" in output


def test_compose_unknown_component_raises(composer):
    with pytest.raises(ValueError):
        composer.compose("nonexistent.layout", {})


def test_compose_unknown_child_raises(composer):
    with pytest.raises(ValueError):
        composer.compose("layout.stack", {
            "blocks": [("nonexistent.child", {})],
        })
