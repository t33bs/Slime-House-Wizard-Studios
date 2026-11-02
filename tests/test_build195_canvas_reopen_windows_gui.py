"""Windows Qt acceptance for opening a saved creature onto another-size canvas."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import pytest
from PIL import Image

pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
import shws_wizard.friendly_animator as wizard
from shws_wizard.studio.pet_suite_model import PetSuiteModel


@pytest.mark.parametrize('size', [(64, 64), (256, 128)])
def test_open_creature_restores_its_own_canvas_and_timeline(tmp_path, monkeypatch, size):
    app = QApplication.instance() or QApplication([])
    model = PetSuiteModel(size)
    im = Image.new('RGBA', (8, 8), (21, 41, 61, 255))
    model.import_part('Independent art', im)
    for n in range(7):
        model.parts[0]['x'] = 3 * n
        model.save_frame('Walk')
    model.current = 'Walk'
    saved = tmp_path / 'custom-size.rig.json'
    model.save_project(saved)
    monkeypatch.setattr(wizard.QFileDialog, 'getOpenFileName',
                        lambda *args, **kwargs: (str(saved), 'Editable creature project (*.rig.json)'))

    window = wizard.Suite()
    window.confirm_unsaved_projects = lambda *_a, **_k: True
    window.show(); app.processEvents()
    try:
        assert window.model.size != size
        before_count = len(window._projects)
        window.open_project()
        app.processEvents()
        assert len(window._projects) == before_count + 1
        assert window.model.size == size
        assert tuple(window.canvas._image_size) == size
        assert len(window.model.animations['Walk']) == 7
        assert window.timeline.count() == 7
        for index in (0, 3, 6):
            window.select_timeline_pose(index)
            assert window.model.render().tobytes() == model.render(model.animations['Walk'][index]).tobytes()
    finally:
        window.close()
