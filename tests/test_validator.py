"""Tests for the AskeeDS Validator."""


def test_validate_all_components(validator, components):
    errors = validator.validate_all(components)
    assert errors == [], "Validation errors:\n" + "\n".join(
        f"  {n}: {m}" for n, m in errors
    )


def test_validate_catches_bad_status(validator):
    from askee_ds.loader import Component
    bad = Component(
        name="test.bad", category="core/test",
        description="Bad", status="nonexistent",
        props={}, render={"type": "inline", "template": "hi"},
    )
    errors = validator.validate(bad)
    statuses = [msg for _, msg in errors if "status" in msg]
    assert len(statuses) >= 1


def test_validate_catches_bad_category(validator):
    from askee_ds.loader import Component
    bad = Component(
        name="test.bad", category="invalid/prefix",
        description="Bad", status="ideated",
        props={}, render={"type": "inline", "template": "hi"},
    )
    errors = validator.validate(bad)
    cats = [msg for _, msg in errors if "category" in msg]
    assert len(cats) >= 1


def test_validate_catches_bad_render_type(validator):
    from askee_ds.loader import Component
    bad = Component(
        name="test.bad", category="core/test",
        description="Bad", status="ideated",
        props={}, render={"type": "nonexistent"},
    )
    errors = validator.validate(bad)
    renders = [msg for _, msg in errors if "render type" in msg]
    assert len(renders) >= 1


def test_validate_catches_bad_section_type(validator):
    from askee_ds.loader import Component
    bad = Component(
        name="test.bad", category="core/test",
        description="Bad", status="ideated",
        props={}, render={
            "type": "box", "width": 40, "border": "single",
            "sections": [{"type": "nonexistent"}],
        },
    )
    errors = validator.validate(bad)
    sects = [msg for _, msg in errors if "section" in msg]
    assert len(sects) >= 1
