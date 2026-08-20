"""Approved Track 05 fixtures for lexical language symbol registration."""

import unittest

from src.sac_diff import _SYMBOL_REGISTRY


POSITIVE_FIXTURES = {
    ".py": [("class Ledger:", "Ledger"), ("async def settle(item):", "settle")],
    ".js": [("export class Ledger {}", "Ledger"), ("const settle = item => item;", "settle")],
    ".jsx": [("function LedgerView() {", "LedgerView"), ("export const Row = (item) => <li />;", "Row")],
    ".ts": [("export interface Ledger {}", "Ledger"), ("async function settle(item: Item) {", "settle")],
    ".tsx": [("export class LedgerView {}", "LedgerView"), ("const Row: Component = (item) => <li />;", "Row")],
    ".go": [("type Ledger struct {", "Ledger"), ("func (l *Ledger) Settle(item Item) error {", "Settle")],
}

NEGATIVE_FIXTURES = {
    ".py": ["settle(item)", "# def commented():", 'text = "def string():"', "from ledger import settle"],
    ".js": ["settle(item);", "// function commented() {}", 'const text = "function string() {}";', "import { settle } from './ledger.js';"],
    ".jsx": ["render(view);", "// const Commented = () => null;", 'const text = "class StringValue {}";', "import Row from './Row.jsx';"],
    ".ts": ["settle(item);", "// interface Commented {}", 'const text = "type StringValue = string";', "import type { Ledger } from './ledger';"],
    ".tsx": ["render(<Row />);", "// function Commented() {}", 'const text = "interface StringValue {}";', "import { Row } from './Row';"],
    ".go": ["Settle(item)", "// func Commented() {}", 'text := "func StringValue() {}"', 'import "example/ledger"'],
}


def recognized_symbol(extension: str, line: str) -> str | None:
    for pattern in _SYMBOL_REGISTRY[extension]:
        match = pattern.match(line)
        if match:
            return match.group("symbol")
    return None


class SymbolRegistryTest(unittest.TestCase):
    def test_positive_fixtures_recognize_every_declared_symbol(self) -> None:
        for extension, fixture in POSITIVE_FIXTURES.items():
            with self.subTest(extension=extension):
                self.assertEqual(
                    [expected for _, expected in fixture],
                    [recognized_symbol(extension, line) for line, _ in fixture],
                )

    def test_negative_fixtures_have_zero_false_positives(self) -> None:
        for extension, fixture in NEGATIVE_FIXTURES.items():
            with self.subTest(extension=extension):
                self.assertEqual([], [symbol for line in fixture if (symbol := recognized_symbol(extension, line))])

    def test_existing_dart_and_powershell_behavior(self) -> None:
        fixtures = {
            ".dart": [("abstract class Ledger {", "Ledger"), ("Future settle() {", "settle")],
            ".ps1": [("function Invoke-Ledger {", "Invoke"), ("$ledger = @{}", "ledger")],
        }
        for extension, fixture in fixtures.items():
            with self.subTest(extension=extension):
                self.assertEqual(
                    [expected for _, expected in fixture],
                    [recognized_symbol(extension, line) for line, _ in fixture],
                )


if __name__ == "__main__":
    unittest.main()
