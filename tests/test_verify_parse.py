"""Approved Track 01 tests for verify target parsing."""

import unittest

from src.sac_engine import _parse_line


def parse_verify(constraint: str) -> tuple[list[str], list[str]]:
    line = f"# SAC:REGR: WARNING - Subject: {constraint}"
    tag, warnings = _parse_line(line)
    if tag is None:
        raise AssertionError(f"fixture did not parse: {line}")
    return tag.verify, warnings


class VerifyParseTest(unittest.TestCase):
    def test_dotted_target_and_second_target_are_preserved(self) -> None:
        targets, warnings = parse_verify("MUST verify: Cache.key, Adapter")
        self.assertEqual(["Cache.key", "Adapter"], targets)
        self.assertEqual([], warnings)

    def test_terminal_period_preserves_existing_behavior(self) -> None:
        targets, warnings = parse_verify("MUST verify: CacheKey, Adapter.")
        self.assertEqual(["CacheKey", "Adapter"], targets)
        self.assertEqual([], warnings)

    def test_narrative_before_verify_preserves_existing_behavior(self) -> None:
        targets, warnings = parse_verify(
            "Se mudar X, entao Y. MUST verify: CacheKey"
        )
        self.assertEqual(["CacheKey"], targets)
        self.assertEqual([], warnings)

    def test_invalid_target_is_named_without_dropping_valid_target(self) -> None:
        targets, warnings = parse_verify("MUST verify: 9bad, Good")
        self.assertEqual(["Good"], targets)
        self.assertEqual(["invalid_verify_target target=9bad"], warnings)

    def test_semicolon_ends_verify_list(self) -> None:
        targets, warnings = parse_verify("MUST verify: A; texto depois")
        self.assertEqual(["A"], targets)
        self.assertEqual([], warnings)

    def test_narrative_after_verify_is_not_accepted_as_a_target(self) -> None:
        targets, warnings = parse_verify("MUST verify: Good, narrative words")
        self.assertEqual(["Good"], targets)
        self.assertEqual(
            ["invalid_verify_target target=narrative words"], warnings
        )


if __name__ == "__main__":
    unittest.main()
