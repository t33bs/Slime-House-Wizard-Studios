"""Static guards run on Linux too; GUI behavior is tested with Qt on Windows."""
from pathlib import Path
import ast

ROOT=Path(__file__).resolve().parents[1]


def test_shs_close_dialog_choice_wiring():
    source=(ROOT/'studio/app.py').read_text(encoding='utf-8')
    tree=ast.parse(source)
    window=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='MainWindow')
    method=next(x for x in window.body if isinstance(x,ast.FunctionDef) and x.name=='closeEvent')
    body=ast.get_source_segment(source,method)
    assert 'StandardButton.Yes|QMessageBox.StandardButton.No|QMessageBox.StandardButton.Cancel' in body
    assert 'QMessageBox.StandardButton.Cancel)' in body
    assert 'choice==QMessageBox.StandardButton.No' in body
    assert 'choice==QMessageBox.StandardButton.Yes' in body
    assert 'self.recovery_path.unlink(missing_ok=True)' in body
    # The old bug wrote recovery *before asking*. Both choices are now
    # explicitly handled, so No never calls write_recovery.
    assert body.index('QMessageBox.question(')<body.index('self.write_recovery()')
    assert 'Choose No to stay' not in body


def test_wizard_still_has_save_discard_cancel():
    source=(ROOT/'shws_wizard/friendly_animator.py').read_text(encoding='utf-8')
    assert 'QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel' in source
    assert 'if answer==QMessageBox.StandardButton.Cancel' in source
