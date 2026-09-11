import os
import sys
import unittest

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

class TestOutputDirConfiguration(unittest.TestCase):
    def test_output_dir_env_var(self):
        test_dir = os.path.join(PROJECT_ROOT, "tmp_test_output")
        os.environ["OUTPUT_DIR"] = test_dir
        try:
            self.assertEqual(os.environ.get("OUTPUT_DIR"), test_dir)
        finally:
            if "OUTPUT_DIR" in os.environ:
                del os.environ["OUTPUT_DIR"]

    def test_cli_output_dir_argument(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("-o", "--output-dir")
        args = parser.parse_args(["-o", r"C:\Users\gdemon\daily-work\ast"])
        self.assertEqual(args.output_dir, r"C:\Users\gdemon\daily-work\ast")

if __name__ == "__main__":
    unittest.main()
