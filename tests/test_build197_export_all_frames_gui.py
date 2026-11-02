"""Windows/Qt click-path: custom frame name, cancel, correct status, no stray prefixes."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import json
from pathlib import Path

import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
import shws_wizard.friendly_animator as wizard


def test_export_all_frames_uses_custom_manifest_name(tmp_path, monkeypatch):
    app=QApplication.instance() or QApplication([])
    editor=wizard.Suite()
    editor.show(); app.processEvents()
    try:
        editor.model.import_part('old-project-name',Image.new('RGBA',(4,4),(42,53,64,255)))
        editor.model.save_frame('Idle / Breathing')
        filename=tmp_path/'MySwordcat_frames.json'
        calls=[]
        def save_dialog(*args):
            calls.append(args)
            return str(filename), 'Animation frame manifest (*.json)'
        monkeypatch.setattr(wizard.QFileDialog,'getSaveFileName',save_dialog)
        editor.export_all_frames()
        assert calls
        assert calls[0][2] == 'creature_frames.json'
        assert filename.exists()
        assert (tmp_path/'MySwordcat_frame_0001.png').exists()
        manifest=json.loads(filename.read_text())
        assert manifest['frames'][0]['file']=='MySwordcat_frame_0001.png'
        assert 'MySwordcat' in editor.status.text()
        assert not list(tmp_path.glob('friendly*'))
    finally:
        editor.close()


def test_export_all_frames_cancel_leaves_files_untouched(tmp_path, monkeypatch):
    app=QApplication.instance() or QApplication([])
    editor=wizard.Suite()
    try:
        monkeypatch.setattr(wizard.QFileDialog,'getSaveFileName',lambda *a: ('',''))
        editor.export_all_frames()
        assert not list(tmp_path.iterdir())
    finally:
        editor.close()
