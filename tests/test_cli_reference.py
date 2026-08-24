from pathlib import Path
import subprocess
import sys
from unittest import TestCase


PROJECT_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_DIR / "docs"))

from generate_cli_reference import ANSI_ESCAPE_PATTERN


class CommandReferenceTests(TestCase):
    def test_committed_reference_matches_cli_help(self):
        subprocess.run(
            [sys.executable, "docs/generate_cli_reference.py", "--check"],
            check=True,
            cwd=PROJECT_DIR,
        )

    def test_ansi_escape_sequences_are_removed_from_help(self):
        self.assertEqual(
            ANSI_ESCAPE_PATTERN.sub("", "\x1b[1;34musage:\x1b[0m mastodown"),
            "usage: mastodown",
        )
