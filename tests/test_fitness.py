import os
import sys
import tempfile
import textwrap
import unittest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sac_engine import assess_domain_capillarity


def test_guard(source):
    """Physical verification target named by the baseline fixture's REGR."""
    return "MUST verify: test_guard" in source


class FitnessTest(unittest.TestCase):
    def test_physical_guard_target(self):
        """Keep the baseline fixture's physical REGR verification target covered."""
        self.assertTrue(test_guard(self.BASE_SOURCE))

    def assess(self, source, anchors, claims):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, ".sac"))
            os.makedirs(os.path.join(root, "src"))
            with open(os.path.join(root, "src", "domain.py"), "w", encoding="utf-8") as f:
                f.write(textwrap.dedent(source).lstrip())
            claim_lines = "\n".join(f"  - {claim}" for claim in claims)
            manifest = f"""# SAC Domain Index

## fixture
- intent: Fitness fixture
- onboarded: 2026-08-20
- drawer_file:
- drawer_refs:
- anchor_symbols: {', '.join(anchors)}
- files:
  - src/domain.py
- context_scenarios: SUMMARY, EXTEND, REGRESSION
- coverage_claims:
{claim_lines}
- on_edit: sac-execution-overlay
- known_gaps:
"""
            with open(os.path.join(root, ".sac", "domains.md"), "w", encoding="utf-8") as f:
                f.write(manifest)
            return assess_domain_capillarity(root, "fixture")

    BASE_SOURCE = """
        # SAC:ARCH: on=ssot - Core: MUST remain authoritative
        class Core: pass
        # SAC:REGR: on=core_regression - Guard: MUST remain covered; MUST verify: test_guard
        class Guard: pass
    """
    BASE_CLAIMS = [
        "SUMMARY_CORE | SUMMARY | ARCH | Core | src/domain.py",
        "EXTEND_CORE | EXTEND | ARCH | Core | src/domain.py",
        "REGRESSION_GUARD | REGRESSION | REGR | Guard | src/domain.py",
    ]

    def test_policy_selected_regr_without_claim_keeps_fit(self):
        payload = self.assess(
            self.BASE_SOURCE
            + "\n# SAC:REGR: on=extra_regression - Extra: MUST remain covered; MUST verify: test_extra\nclass Extra: pass\n",
            ["Core"],
            self.BASE_CLAIMS,
        )
        self.assertEqual("FIT", payload["fitness_status"])
        self.assertEqual(0, payload["uncontracted_context_tag_count"])

    def test_unclaimed_arch_selected_by_anchor_remains_over_select(self):
        payload = self.assess(
            self.BASE_SOURCE
            + "\n# SAC:ARCH: on=boundary - ExtraArch: MUST remain bounded\nclass ExtraArch: pass\n",
            ["Core", "ExtraArch"],
            self.BASE_CLAIMS,
        )
        self.assertEqual("OVER_SELECT", payload["fitness_status"])
        self.assertEqual(1, payload["uncontracted_context_tag_count"])

    def test_missing_regression_role_claim_remains_too_thin(self):
        claims = self.BASE_CLAIMS[:2] + [
            "REGRESSION_WRONG_ROLE | REGRESSION | ARCH | Core | src/domain.py"
        ]
        payload = self.assess(self.BASE_SOURCE, ["Core"], claims)
        self.assertEqual("TOO_THIN", payload["fitness_status"])
        self.assertIn("REGRESSION:REGR", payload["missing_roles"])

    def test_arch_claim_whose_symbol_is_not_anchor_remains_unfit(self):
        payload = self.assess(self.BASE_SOURCE, [], self.BASE_CLAIMS)
        self.assertEqual("UNFIT", payload["fitness_status"])
        self.assertEqual(2, len(payload["context_unfit_claims"]))

    def test_assess_reports_exact_arch_anchor_floor_and_excess(self):
        payload = self.assess(self.BASE_SOURCE, ["Core", "Surplus"], self.BASE_CLAIMS)
        self.assertEqual(["Core"], payload["anchor_floor_symbols"])
        self.assertEqual(["Surplus"], payload["anchor_excess_symbols"])


if __name__ == "__main__":
    unittest.main()
