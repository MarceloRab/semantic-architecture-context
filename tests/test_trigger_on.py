"""Approved Track 02 tests for the on=<condition> field and legacy parsing."""

import os
import tempfile
import unittest

from src.sac_engine import _ALLOWED_TRIGGERS, _parse_line, scan


ARCH_ALLOWED = ("ssot", "boundary", "ordering", "state", "exclusive", "ownership")


class TriggerOnTest(unittest.TestCase):
    def parse(self, line: str):
        tag, warnings = _parse_line(line)
        self.assertIsNotNone(tag, line)
        return tag, warnings

    def test_complete_legacy_matrix(self) -> None:
        fixtures = (
            ("ARCH", "RULE", "MUST remain canonical", [], None),
            ("ARCH", "CONSTRAINT", "MUST remain canonical", [], None),
            ("REGR", "WARNING", "MUST verify: Cache.key, Adapter", ["Cache.key", "Adapter"], None),
            ("REGR", "CRITICAL", "MUST verify: Cache.key, Adapter", ["Cache.key", "Adapter"], None),
            ("DEPRECATED", "WARNING", "MUST NOT be used; replacement: NewApi", [], "NewApi"),
            ("DEPRECATED", "CRITICAL", "MUST NOT be used; replacement: NewApi", [], "NewApi"),
        )
        for tag_type, old_trigger, constraint, verify, replacement in fixtures:
            with self.subTest(tag_type=tag_type, old_trigger=old_trigger):
                tag, warnings = self.parse(
                    f"# SAC:{tag_type}: {old_trigger} - Sym: {constraint}"
                )
                self.assertEqual("", tag.trigger)
                self.assertEqual("Sym", tag.symbol)
                self.assertEqual(constraint, tag.constraint)
                self.assertEqual(verify, tag.verify)
                self.assertEqual(replacement, tag.replacement)
                self.assertEqual(["legacy_trigger"], warnings)

    def test_legacy_deprecated_still_requires_replacement(self) -> None:
        tag, warnings = self.parse(
            "# SAC:DEPRECATED: WARNING - Sym: MUST NOT be used"
        )
        self.assertEqual("", tag.trigger)
        self.assertIsNone(tag.replacement)
        self.assertEqual(
            ["legacy_trigger", "deprecated_replacement_required"], warnings
        )

    def test_legacy_regr_if_modifying_form_remains_visible(self) -> None:
        tag, warnings = self.parse(
            "# SAC:REGR: WARNING - If modifying Sym, you MUST verify: Target"
        )
        self.assertEqual(("Sym", "", ["Target"]), (tag.symbol, tag.trigger, tag.verify))
        self.assertEqual(["legacy_trigger"], warnings)

    def test_legacy_and_new_tags_coexist_without_loss(self) -> None:
        source = "\n".join(
            (
                "# SAC:ARCH: RULE - Legacy: MUST remain visible",
                "# SAC:ARCH: on=ssot - Current: MUST remain visible",
            )
        )
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "mixed.py")
            with open(path, "w", encoding="utf-8") as fixture:
                fixture.write(source)
            warnings: list[str] = []
            tags = scan(root, warnings=warnings)
        self.assertEqual(["Legacy", "Current"], [tag.symbol for tag in tags])
        self.assertEqual(["", "ssot"], [tag.trigger for tag in tags])
        self.assertEqual(1, sum("legacy_trigger" in warning for warning in warnings))

    def test_arch_ssot_is_accepted(self) -> None:
        tag, warnings = self.parse("# SAC:ARCH: on=ssot - Sym: MUST remain unique")
        self.assertEqual("ssot", tag.trigger)
        self.assertEqual([], warnings)

    def test_invalid_arch_condition_lists_exact_closed_vocabulary(self) -> None:
        tag, warnings = self.parse(
            "# SAC:ARCH: on=qualquer_outra_coisa - Sym: MUST remain visible"
        )
        self.assertEqual("qualquer_outra_coisa", tag.trigger)
        self.assertEqual(ARCH_ALLOWED, _ALLOWED_TRIGGERS["ARCH"])
        self.assertEqual(
            [
                "invalid_trigger tag=ARCH trigger=qualquer_outra_coisa "
                "allowed=ssot|boundary|ordering|state|exclusive|ownership"
            ],
            warnings,
        )

    def test_regr_snake_case_condition_is_accepted(self) -> None:
        tag, warnings = self.parse(
            "# SAC:REGR: on=normalization_order - Sym: MUST verify: Target"
        )
        self.assertEqual("normalization_order", tag.trigger)
        self.assertEqual([], warnings)

    def test_invalid_regr_condition_keeps_tag(self) -> None:
        tag, warnings = self.parse("# SAC:REGR: on=X - Sym: MUST verify: Target")
        self.assertEqual(("Sym", "X", ["Target"]), (tag.symbol, tag.trigger, tag.verify))
        self.assertEqual(
            ["invalid_trigger tag=REGR trigger=X allowed=[a-z][a-z0-9_]{2,47}"],
            warnings,
        )

    def test_new_line_is_not_longer_than_legacy_equivalent(self) -> None:
        constraint = "Sym: MUST preserve behavior"
        legacy = f"# SAC:ARCH: CONSTRAINT - {constraint}"
        current = f"# SAC:ARCH: on=ssot - {constraint}"
        self.assertLessEqual(len(current), len(legacy))


if __name__ == "__main__":
    unittest.main()
