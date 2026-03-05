"""Tests for the AskeeDS CLI."""

import json


def test_validate_succeeds():
    from askee_ds.cli import main
    assert main(["validate"]) == 0


def test_validate_bad_path():
    from askee_ds.cli import main
    assert main(["validate", "--components", "/nonexistent/path"]) == 1


def test_list_all():
    from askee_ds.cli import main
    assert main(["list"]) == 0


def test_list_by_status(capsys):
    from askee_ds.cli import main
    main(["list", "--status", "approved"])
    captured = capsys.readouterr()
    assert "approved" in captured.out
    assert "ideated" not in captured.out


def test_list_by_prefix(capsys):
    from askee_ds.cli import main
    main(["list", "--prefix", "room-card"])
    captured = capsys.readouterr()
    assert "room-card.default" in captured.out


def test_preview_known_component(capsys):
    from askee_ds.cli import main
    props = json.dumps({
        "title": "Test", "description_text": "A test.",
        "items": [], "npcs": [],
        "exits": [{"id": "n", "label": "north"}],
    })
    result = main(["preview", "room-card.default", "--props", props])
    assert result == 0
    captured = capsys.readouterr()
    assert "Test" in captured.out
    assert "north" in captured.out


def test_preview_unknown_component():
    from askee_ds.cli import main
    assert main(["preview", "nonexistent.component"]) == 1


def test_preview_bad_json():
    from askee_ds.cli import main
    assert main(["preview", "room-card.default", "--props", "{bad json}"]) == 1


def test_no_command_shows_help(capsys):
    from askee_ds.cli import main
    result = main([])
    assert result == 0
