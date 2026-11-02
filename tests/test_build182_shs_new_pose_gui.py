"""Windows Qt smoke: visible SHS sidebar button creates a new Wizard pose."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
pytest.importorskip('PySide6')
from PIL import Image
from PySide6.QtWidgets import QApplication
from main import SlimeHouseWizardStudios


def test_shs_sidebar_send_as_new_pose_click_roundtrip():
    app=QApplication.instance() or QApplication([])
    host=SlimeHouseWizardStudios()
    host.wizard.confirm_unsaved_projects=lambda *_args,**_kw: True
    try:
        host.show()
        app.processEvents()
        button=host.studio.send_new_pose_button
        assert button.text()=='Send to Slime Wizard as New Pose'
        assert button.isVisible()
        assert button.parentWidget() is host.studio.external_save_button.parentWidget()
        animation=host.wizard.anim.currentText()
        original_count=len(host.wizard.model.animations.get(animation,[]))
        # The SHS canvas is deliberately the same size as the active creature.
        sprite=Image.new('RGBA',tuple(host.wizard.model.size),(0,0,0,0))
        sprite.putpixel((8,8),(10,20,30,255))
        host.studio.current_image=lambda:sprite
        button.click()
        app.processEvents()
        assert host.tabs.currentWidget() is host.wizard
        assert len(host.wizard.model.animations.get(animation,[]))==original_count+1
        assert host.wizard.model.render(host.wizard.model.animations[animation][host.wizard.frame]).tobytes()==sprite.tobytes()
        assert host.studio.external_png_path is None
    finally:
        host.studio._dirty=False
        host.wizard.confirm_unsaved_projects=lambda *_args,**_kw: True
        host.close()
