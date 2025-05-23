import unittest
import subprocess
import os
import tempfile
import shutil
import re

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
COOL_WORDLIST_FILENAME = "password.list"
DICTIONARY_FILENAME = "dict.txt"

# This import is needed to access PRESETS directly for the special char test adjustment
# Ensure pwfilter is importable (e.g. after `uv pip install -e .` and venv active)
# or adjust sys.path if running tests in a more complex setup.
try:
    from pwfilter.presets import PRESETS
except ImportError:
    # Fallback for environments where direct import might fail during test discovery
    # This is a bit of a hack; ideally, the test environment ensures pwfilter is on PYTHONPATH
    import sys

    sys.path.insert(0, os.path.abspath(os.path.join(TEST_DIR, "..")))
    from pwfilter.presets import PRESETS


def load_test_passwords(filepath):
    """Loads passwords from a file, skipping comments and empty lines."""
    passwords = set()
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            stripped_line = line.strip()
            if stripped_line:
                passwords.add(stripped_line)
    return passwords


class TestPwFilter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()

        # Paths to the actual test data files
        cls.source_wordlist_path = os.path.join(TEST_DIR, COOL_WORDLIST_FILENAME)
        cls.source_dict_path = os.path.join(TEST_DIR, DICTIONARY_FILENAME)

        if not os.path.exists(cls.source_wordlist_path):
            raise FileNotFoundError(
                f"Test wordlist not found: {cls.source_wordlist_path}"
            )
        if not os.path.exists(cls.source_dict_path):
            raise FileNotFoundError(
                f"Test dictionary not found: {cls.source_dict_path}"
            )

        # We still copy them to a temp dir in case tests modify them (though unlikely here)
        # or if pwfilter expects a writable location for some reason (not the case here).
        # More importantly, it ensures a clean state if the source files were to be changed during a test run by mistake.
        cls.wordlist_path = os.path.join(cls.temp_dir, "test_wordlist.txt")
        shutil.copy(cls.source_wordlist_path, cls.wordlist_path)

        cls.dict_path = os.path.join(cls.temp_dir, "test_dict.txt")
        shutil.copy(cls.source_dict_path, cls.dict_path)

        cls.pwfilter_cmd = "pwfilter"  # Assumes installed

        cls.all_test_passwords = load_test_passwords(cls.wordlist_path)
        cls.test_dictionary_words = load_test_passwords(cls.dict_path)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir)

    def run_pwfilter(self, args):
        cmd = [self.pwfilter_cmd, self.wordlist_path] + args
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, encoding="utf-8"
            )
            return set(
                line.strip() for line in result.stdout.splitlines() if line.strip()
            )
        except subprocess.CalledProcessError as e:
            print(f"Error running pwfilter with args {args}:")
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            raise  # Re-raise to get full traceback for easier debugging

    def test_list_presets(self):
        try:
            result = subprocess.run(
                [self.pwfilter_cmd, "--list-presets"],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("Available presets", result.stdout)
            self.assertIn("ml8", result.stdout)
        except subprocess.CalledProcessError as e:
            self.fail(f"pwfilter --list-presets failed: {e.stderr}")

    # --- Single Preset Tests ---
    # The 'expected' sets now need to be derived by filtering cls.all_test_passwords

    def test_min_length_8(self):
        expected = {p for p in self.all_test_passwords if len(p) >= 8}
        self.assertEqual(self.run_pwfilter(["--presets", "ml8"]), expected)

    def test_has_uppercase(self):
        expected = {p for p in self.all_test_passwords if re.search(r"[A-Z]", p)}
        self.assertEqual(self.run_pwfilter(["--presets", "upper"]), expected)

    def test_has_lowercase(self):
        expected = {p for p in self.all_test_passwords if re.search(r"[a-z]", p)}
        self.assertEqual(self.run_pwfilter(["--presets", "lower"]), expected)

    def test_has_digit(self):
        expected = {p for p in self.all_test_passwords if re.search(r"[0-9]", p)}
        self.assertEqual(self.run_pwfilter(["--presets", "digit"]), expected)

    def test_has_special_char(self):
        special_regex = PRESETS["has_special_char"]["regex"]
        expected = {p for p in self.all_test_passwords if re.search(special_regex, p)}
        self.assertEqual(self.run_pwfilter(["--presets", "special"]), expected)

    def test_has_consecutive_repeated_chars(self):
        expected = {p for p in self.all_test_passwords if re.search(r"(.)\1", p)}
        self.assertEqual(self.run_pwfilter(["--presets", "consec"]), expected)

    def test_no_consecutive_repeated_chars(self):
        consecutive_passwords = {
            p for p in self.all_test_passwords if re.search(r"(.)\1", p)
        }
        expected = self.all_test_passwords - consecutive_passwords
        self.assertEqual(self.run_pwfilter(["--presets", "consec", "-v"]), expected)

    def test_contains_common_pattern_password(self):
        expected = {
            p for p in self.all_test_passwords if "password" in p
        }  # Case sensitive
        self.assertEqual(self.run_pwfilter(["--presets", "cmnpwd"]), expected)

    def test_contains_common_pattern_password_case_insensitive(self):
        expected = {p for p in self.all_test_passwords if "password" in p.lower()}
        self.assertEqual(self.run_pwfilter(["--presets", "cmnpwd", "-i"]), expected)

    def test_in_dictionary(self):
        expected = {
            p for p in self.all_test_passwords if p in self.test_dictionary_words
        }
        self.assertEqual(
            self.run_pwfilter(
                ["--presets", "dict", "--dictionary-file", self.dict_path]
            ),
            expected,
        )

    def test_in_dictionary_case_insensitive(self):
        # For case-insensitive dictionary check, dictionary words are lowercased for comparison in core
        lower_dict_words = {dw.lower() for dw in self.test_dictionary_words}
        expected = {p for p in self.all_test_passwords if p.lower() in lower_dict_words}
        self.assertEqual(
            self.run_pwfilter(
                ["--presets", "dict", "--dictionary-file", self.dict_path, "-i"]
            ),
            expected,
        )

    def test_in_dictionary_inverted(self):
        dict_matches = {
            p for p in self.all_test_passwords if p in self.test_dictionary_words
        }
        expected = self.all_test_passwords - dict_matches
        self.assertEqual(
            self.run_pwfilter(
                ["--presets", "dict", "--dictionary-file", self.dict_path, "-v"]
            ),
            expected,
        )

    def test_strong_8_plus_all_types(self):
        s8all_regex = PRESETS["strong_8_plus_all_types"]["regex"]  # NEW
        expected = {p for p in self.all_test_passwords if re.search(s8all_regex, p)}
        self.assertEqual(self.run_pwfilter(["--presets", "s8all"]), expected)

    # --- Combination Tests ---
    def test_combo_ml8_upper_digit(self):
        expected = {
            p
            for p in self.all_test_passwords
            if len(p) >= 8 and re.search(r"[A-Z]", p) and re.search(r"[0-9]", p)
        }
        self.assertEqual(
            self.run_pwfilter(["--presets", "ml8", "upper", "digit"]), expected
        )

    def test_combo_ml12_lower_special_inverted(self):
        special_regex_str = PRESETS["has_special_char"]["regex"]
        matches_criteria = {
            p
            for p in self.all_test_passwords
            if len(p) >= 12
            and re.search(r"[a-z]", p)
            and re.search(special_regex_str, p)
        }
        expected_inverted = self.all_test_passwords - matches_criteria
        self.assertEqual(
            self.run_pwfilter(["--presets", "ml12", "lower", "special", "-v"]),
            expected_inverted,
        )

    def test_combo_onlydig_nodig_is_empty(self):
        # This is an interesting one. The regex for "onlydig" is ^[0-9]+$
        # The regex for "nodig" is ^[^0-9]*$
        # Logically, no string can satisfy both.
        expected = set()
        # We can also define it by filtering self.all_test_passwords if we want strictness
        # expected = {
        #     p for p in self.all_test_passwords
        #     if re.match(r"^[0-9]+$", p) and re.match(r"^[^0-9]*$", p)
        # } # This will be empty
        self.assertEqual(self.run_pwfilter(["--presets", "onlydig", "nodig"]), expected)

    def test_custom_regex(self):
        custom_r = r"^(apple|banana)$"
        expected = {p for p in self.all_test_passwords if re.match(custom_r, p)}
        self.assertEqual(self.run_pwfilter(["--regex", custom_r]), expected)

    def test_custom_regex_ignore_case(self):
        custom_r = r"^password$"
        expected = {
            p for p in self.all_test_passwords if re.match(custom_r, p, re.IGNORECASE)
        }
        self.assertEqual(self.run_pwfilter(["--regex", custom_r, "-i"]), expected)

    def test_empty_wordlist_file(self):
        # Create a truly empty temporary file for this specific test
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, dir=self.temp_dir, suffix=".txt"
        ) as tmp_empty_file:
            empty_wordlist_path = tmp_empty_file.name

        try:
            cmd = [self.pwfilter_cmd, empty_wordlist_path, "--presets", "ml8"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, encoding="utf-8"
            )
            output_set = set(
                line.strip() for line in result.stdout.splitlines() if line.strip()
            )
            self.assertEqual(output_set, set())
            self.assertIn(
                "Processed 0 valid passwords from 0 total lines.", result.stderr
            )  # Check stderr message
        finally:
            os.remove(empty_wordlist_path)

    def test_dictionary_and_regex_combo(self):
        # Words in dict AND len >= 8
        expected = {
            p
            for p in self.all_test_passwords
            if (p in self.test_dictionary_words) and (len(p) >= 8)
        }
        self.assertEqual(
            self.run_pwfilter(
                ["--presets", "dict", "ml8", "--dictionary-file", self.dict_path]
            ),
            expected,
        )

    def test_no_filters_error(self):
        cmd = [self.pwfilter_cmd, self.wordlist_path]
        with self.assertRaises(subprocess.CalledProcessError) as cm:
            subprocess.run(
                cmd, capture_output=True, text=True, check=True, encoding="utf-8"
            )
        self.assertIn(
            "usage: pwfilter [-h] (--presets preset_id_or_name [preset_id_or_name ...]",
            cm.exception.stderr.lower(),
        )


if __name__ == "__main__":
    unittest.main()
