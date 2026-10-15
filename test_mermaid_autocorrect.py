import unittest
from Fileshed import fix_mermaid_overescape

class TestMermaidAutocorrect(unittest.TestCase):
    def test_basic_correction(self):
        text = r'```mermaid\ngraph TD\n    subgraph \"Driver Layer\"\n        SDR[RTL-SDR V5]\n    end\n```'
        expected = r'```mermaid\ngraph TD\n    subgraph "Driver Layer"\n        SDR[RTL-SDR V5]\n    end\n```'
        corrected, count = fix_mermaid_overescape(text)
        self.assertEqual(corrected, expected)
        self.assertEqual(count, 1)

    def test_no_correction_outside_block(self):
        text = r'This is an escaped quote \" and it should stay.'
        corrected, count = fix_mermaid_overescape(text)
        self.assertEqual(corrected, text)
        self.assertEqual(count, 0)

    def test_case_insensitivity(self):
        text = r'```Mermaid\nnode \"A\"\n```'
        expected = r'```Mermaid\nnode "A"\n```'
        corrected, count = fix_mermaid_overescape(text)
        self.assertEqual(corrected, expected)
        self.assertEqual(count, 1)

    def test_multiple_blocks(self):
        text = r'```mermaid\nnode \"A\"\n```\nProse\n```mermaid\nnode \"B\"\n```'
        expected = r'```mermaid\nnode "A"\n```\nProse\n```mermaid\nnode "B"\n```'
        corrected, count = fix_mermaid_overescape(text)
        self.assertEqual(corrected, expected)
        self.assertEqual(count, 2)

    def test_backslash_runs(self):
        cases = [
            (r'```mermaid\n"quote"', r'```mermaid\n"quote"'), # no backslash
            (r'```mermaid\n\"quote"', r'```mermaid\n"quote"'), # exactly one: match
            (r'```mermaid\n\\"quote"', r'```mermaid\n\\"quote"'), # two: no match
            (r'```mermaid\n\\\"quote"', r'```mermaid\n\\\"quote"'), # three: no match
            (r'```mermaid\n\\\\\"quote"', r'```mermaid\n\\\\\"quote"'), # four: no match
        ]
        for input_text, expected in cases:
            with self.subTest(input_text=input_text):
                corrected, count = fix_mermaid_overescape(input_text)
                self.assertEqual(corrected, expected)
                if corrected != input_text:
                    self.assertEqual(count, 1)
                else:
                    self.assertEqual(count, 0)

    def test_non_greedy_blocks(self):
        text = r'```mermaid\nblock 1 \"A\"\n```\nProse\n```mermaid\nblock 2 \"B\"\n```'
        corrected, count = fix_mermaid_overescape(text)
        self.assertEqual(count, 2)
        self.assertIn('block 1 "A"', corrected)
        self.assertIn('block 2 "B"', corrected)

    def test_idempotence(self):
        text = r'```mermaid\nnode \"A\"\n```'
        corrected1, count1 = fix_mermaid_overescape(text)
        corrected2, count2 = fix_mermaid_overescape(corrected1)
        self.assertEqual(corrected1, corrected2)
        self.assertEqual(count2, 0)

if __name__ == "__main__":
    unittest.main()
