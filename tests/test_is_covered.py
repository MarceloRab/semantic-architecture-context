"""Approved Track 04 tests for complete-set diff coverage."""

import os
import tempfile
import unittest

from src.sac_diff import diff_check


def added_file_patch(*paths: str) -> str:
    parts = []
    for path in paths:
        with open(path, "r", encoding="utf-8") as fixture:
            lines = fixture.read().splitlines()
        relative = path.split(os.sep + "fixture" + os.sep, 1)[-1]
        body = "\n".join(f"+{line}" for line in lines)
        parts.append(
            f"--- /dev/null\n+++ b/{relative}\n"
            f"@@ -0,0 +1,{len(lines)} @@\n{body}\n"
        )
    return "".join(parts)


class CompleteCoverageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = os.path.join(self.temporary.name, "fixture")
        os.makedirs(os.path.join(self.root, "lib"))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write(self, relative: str, content: str) -> str:
        path = os.path.join(self.root, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fixture:
            fixture.write(content)
        return path

    def source(self, target: str = "testChargeIdem") -> str:
        return self.write(
            "lib/pay.dart",
            "// SAC:REGR: on=payment_change - charge: MUST verify: "
            f"{target}\nvoid charge() {{}}\n",
        )

    def test_test_and_aaa_path_orders_have_identical_verdicts(self) -> None:
        verdicts = []
        for directory in ("test", "aaa"):
            source = self.source()
            target = self.write(
                f"{directory}/pay_test.dart", "void testChargeIdem() {}\n"
            )
            verdicts.append(diff_check(added_file_patch(source, target), self.root).exit_code)
        self.assertEqual([0, 0], verdicts)

    def test_untouched_verify_target_remains_a_violation(self) -> None:
        source = self.source("testNotChanged")
        result = diff_check(added_file_patch(source), self.root)
        self.assertEqual(1, result.exit_code)
        self.assertEqual(["testNotChanged"], result.violations[0].uncovered)

    def test_ack_releases_exactly_the_named_symbol(self) -> None:
        first = self.source("testNotChanged")
        second = self.write(
            "lib/refund.dart",
            "// SAC:REGR: on=refund_change - refund: MUST verify: testRefund\n"
            "void refund() {}\n",
        )
        result = diff_check(
            added_file_patch(first, second),
            self.root,
            pr_body="SAC-ACK: charge",
        )
        self.assertEqual(1, result.exit_code)
        self.assertEqual(["refund"], [violation.symbol for violation in result.violations])
        self.assertEqual(["charge"], result.acks)


if __name__ == "__main__":
    unittest.main()
