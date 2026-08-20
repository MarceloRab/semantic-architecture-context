import os
import sys
import tempfile
import unittest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sac_engine import _parse_line, scan


class CommentMarkerTests(unittest.TestCase):
    def test_supported_non_alphanumeric_markers(self):
        fixtures = {
            "--": "-- SAC:ARCH: on=ssot - SqlOwner: MUST own state",
            "%": "% SAC:ARCH: on=ssot - ErlangOwner: MUST own state",
            ";": "; SAC:ARCH: on=ssot - LispOwner: MUST own state",
            "<!--": "<!-- SAC:ARCH: on=ssot - HtmlOwner: MUST own state -->",
            "/*": "/* SAC:ARCH: on=ssot - BlockOwner: MUST own state */",
            '"""': '""" SAC:ARCH: on=ssot - DocOwner: MUST own state """',
        }
        for marker, line in fixtures.items():
            with self.subTest(marker=marker):
                tag, warnings = _parse_line(line)
                self.assertIsNotNone(tag)
                self.assertEqual([], warnings)
                self.assertNotRegex(tag.constraint, r'(?:-->|\*/|""")$')

    def test_existing_slash_and_hash_markers_remain_supported(self):
        for marker in ("// ", "# "):
            with self.subTest(marker=marker):
                tag, warnings = _parse_line(
                    f"{marker}SAC:ARCH: on=boundary - Existing: NEVER bypass"
                )
                self.assertEqual("Existing", tag.symbol)
                self.assertEqual([], warnings)

    def test_quoted_string_is_ignored_while_real_tag_is_scanned(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "fixture.txt")
            with open(path, "w", encoding="utf-8") as fixture:
                fixture.write(
                    '"SAC:ARCH: on=ssot - StringValue: MUST be ignored"\n'
                    "-- SAC:ARCH: on=ssot - RealTag: MUST be scanned\n"
                )
            warnings = []
            tags = scan(root, extra_exts=[".txt"], warnings=warnings)
        self.assertEqual(["RealTag"], [tag.symbol for tag in tags])
        self.assertEqual([], warnings)

    def test_html_closer_is_removed_before_verify_parsing(self):
        tag, warnings = _parse_line(
            "<!-- SAC:REGR: on=cache_change - Cache: DEVE verificar; "
            "MUST verify: A, B -->"
        )
        self.assertEqual(["A", "B"], tag.verify)
        self.assertNotIn("-->", tag.constraint)
        self.assertNotIn("-->", tag.symbol)
        self.assertEqual([], warnings)

    def test_portuguese_imperative_and_missing_imperative(self):
        portuguese, portuguese_warnings = _parse_line(
            "# SAC:ARCH: on=ownership - Dono: DEVE preservar o contrato"
        )
        missing, missing_warnings = _parse_line(
            "# SAC:ARCH: on=ownership - Dono: preserva o contrato"
        )
        self.assertIsNotNone(portuguese)
        self.assertNotIn("arch_imperative_required", portuguese_warnings)
        self.assertIsNotNone(missing)
        self.assertIn("arch_imperative_required", missing_warnings)

    def test_shape_rejects_alphanumeric_and_overlong_prefixes(self):
        for line in (
            "value SAC:ARCH: on=ssot - False: MUST ignore",
            "!!!!! SAC:ARCH: on=ssot - False: MUST ignore",
        ):
            with self.subTest(line=line):
                self.assertEqual((None, []), _parse_line(line))


if __name__ == "__main__":
    unittest.main()
