"""Package-level tests: load and validate default components, decorations, and maps via askee_ds."""

import unittest

from askee_ds import components, decorations, maps


class TestPackageComponents(unittest.TestCase):
    """Load and validate default component library via askee_ds.components."""

    def test_load_default_components(self) -> None:
        comps = components.load_default_components()
        self.assertIsInstance(comps, list)
        self.assertGreaterEqual(len(comps), 1, "Expected at least one component")
        for c in comps:
            self.assertIn("name", c)
            self.assertIn("meta", c)
            self.assertIn("art", c)
            self.assertIsInstance(c["meta"], dict)
            self.assertIsInstance(c["art"], str)

    def test_validate_default_components_no_errors(self) -> None:
        errors, warnings = components.validate_default_components()
        self.assertIsInstance(errors, list)
        self.assertIsInstance(warnings, list)
        self.assertEqual(len(errors), 0, f"Expected no critical component errors: {errors}")


class TestPackageDecorations(unittest.TestCase):
    """Load and validate default decoration catalog via askee_ds.decorations."""

    def test_load_default_decorations(self) -> None:
        decos = decorations.load_default_decorations()
        self.assertIsInstance(decos, list)
        self.assertGreaterEqual(len(decos), 1, "Expected at least one decoration")
        for d in decos:
            self.assertIn("id", d)
            self.assertIn("meta", d)
            self.assertIn("art", d)
            self.assertIsInstance(d["meta"], dict)
            self.assertIsInstance(d["art"], str)

    def test_validate_default_decorations_no_errors(self) -> None:
        errors, warnings = decorations.validate_default_decorations()
        self.assertIsInstance(errors, list)
        self.assertIsInstance(warnings, list)
        self.assertEqual(len(errors), 0, f"Expected no critical decoration errors: {errors}")


class TestPackageMaps(unittest.TestCase):
    """Load and validate default maps via askee_ds.maps."""

    def test_load_and_validate_default_maps_no_errors(self) -> None:
        errors, warnings, parsed_maps = maps.load_and_validate_default_maps()
        self.assertIsInstance(errors, list)
        self.assertIsInstance(warnings, list)
        self.assertIsInstance(parsed_maps, list)
        self.assertEqual(len(errors), 0, f"Expected no critical map errors: {errors}")


if __name__ == "__main__":
    unittest.main()
