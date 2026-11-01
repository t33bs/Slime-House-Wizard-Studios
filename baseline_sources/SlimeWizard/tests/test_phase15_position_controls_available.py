"""Position controls must remain editable after placing a saved pose."""
import ast
from pathlib import Path
import unittest


class PositionControlsContract(unittest.TestCase):
    def test_easy_mode_keeps_xy_editable(self):
        source = Path(__file__).resolve().parents[1].joinpath("friendly_animator.py").read_text(encoding="utf-8")
        ast.parse(source)
        self.assertIn('self.x.setEnabled(True);self.y.setEnabled(True)', source)
        self.assertNotIn('self.x.setEnabled(self.advanced)', source)
