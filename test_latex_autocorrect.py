import unittest
import re
from Fileshed import fix_latex_overescape

class TestLatexAutocorrect(unittest.TestCase):
    def test_basic_correction(self):
        text = "$\approx 20\\\\text{ms}$"
        corrected, count = fix_latex_overescape(text)
        self.assertEqual(corrected, "$\approx 20\\text{ms}$")
        self.assertEqual(count, 1)

    def test_whitelisted_commands(self):
        cases = [
            (r"\\frac{a}{b}", r"\frac{a}{b}"),
            (r"\\theta", r"\theta"),
            (r"\\cos x", r"\cos x"),
            (r"\\times", r"\times"),
        ]
        for input_text, expected in cases:
            with self.subTest(input_text=input_text):
                corrected, count = fix_latex_overescape(input_text)
                self.assertEqual(corrected, expected)
                self.assertEqual(count, 1)

    def test_brace_rule(self):
        # Not whitelisted, but followed by {
        text = r"\\mycmd{x}"
        corrected, count = fix_latex_overescape(text)
        self.assertEqual(corrected, r"\mycmd{x}")
        self.assertEqual(count, 1)

    def test_unchanged_cases(self):
        cases = [
            ("a\\\\b", "a\\\\b"), # b is not whitelisted, not followed by {
            ("pmatrix a & b \\\\ c & d \\\\ e & f", "pmatrix a & b \\\\ c & d \\\\ e & f"), # row breaks
            (r"\\ [2pt]", r"\\ [2pt]"), # row break with space
            (r"\\*", r"\\*"), # row break with *
            (r"\\\\\\hline", r"\\\\\\hline"), # 3 backslashes
            (r"\\\\\\\\text", r"\\\\\\\\text"), # 4 backslashes
            ("Line end\\\\", "Line end\\\\"), # end of line
        ]
        for input_text, expected in cases:
            with self.subTest(input_text=input_text):
                corrected, count = fix_latex_overescape(input_text)
                self.assertEqual(corrected, expected)
                self.assertEqual(count, 0)

    def test_code_blocks(self):
        text = "Prose \\\\text is fixed, but `\\\\text` in code is not. Also ```\n\\\\text in block\n``` is not."
        expected = "Prose \\text is fixed, but `\\\\text` in code is not. Also ```\n\\\\text in block\n``` is not."
        corrected, count = fix_latex_overescape(text)
        self.assertEqual(corrected, expected)
        self.assertEqual(count, 1)

    def test_currency_prose(self):
        text = "costs $5 and $10"
        corrected, count = fix_latex_overescape(text)
        self.assertEqual(corrected, text)
        self.assertEqual(count, 0)

    def test_idempotence(self):
        text = "$\approx 20\\\\text{ms}$"
        corrected1, count1 = fix_latex_overescape(text)
        corrected2, count2 = fix_latex_overescape(corrected1)
        self.assertEqual(corrected1, corrected2)
        self.assertEqual(count2, 0)

    def test_extra_commands(self):
        text = r"\\customcmd{x}"
        # Without extra
        c1, n1 = fix_latex_overescape(text)
        # With extra (brace rule still applies, so let's use one without brace)
        text2 = r"\\customcmd"
        c2, n2 = fix_latex_overescape(text2)
        self.assertEqual(n2, 0)
        
        c3, n3 = fix_latex_overescape(text2, extra_commands={"customcmd"})
        self.assertEqual(c3, r"\customcmd")
        self.assertEqual(n3, 1)

    def test_extra_commands_types(self):
        # This simulates the logic used in shed_patch_text/shed_lockedit_overwrite
        def get_extra(val):
            if isinstance(val, str):
                return set(filter(None, val.split(','))) if val else None
            elif isinstance(val, (list, tuple, set)):
                return set(filter(None, val)) if val else None
            return None

        cases = [
            ("cmd1,cmd2", {"cmd1", "cmd2"}),
            ("", None),
            (None, None),
            (("cmd1", "cmd2"), {"cmd1", "cmd2"}),
            (["cmd1", "cmd2"], {"cmd1", "cmd2"}),
            (123, None),
        ]
        for input_val, expected in cases:
            with self.subTest(input_val=input_val):
                self.assertEqual(get_extra(input_val), expected)

        # Ensure fix_latex_overescape works with the resulting sets
        text = r"\\customcmd"
        c, n = fix_latex_overescape(text, {"customcmd"})
        self.assertEqual(c, r"\customcmd")
        self.assertEqual(n, 1)

if __name__ == "__main__":
    unittest.main()
