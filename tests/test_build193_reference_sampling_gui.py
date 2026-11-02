"""Windows/Qt mouse integration: pick reference RGBA or 2x2 and stamp only on canvas."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
pytest.importorskip('PySide6')
from PIL import Image
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from studio.app import MainWindow
from studio.core import Layer


def _click_source_pixel(dock, x, y):
    image=dock.references[dock._selected_path]
    label=dock.preview_label
    pixmap=label.pixmap()
    sx=(label.width()-pixmap.width())//2 + (x*pixmap.width()//image.width) + 1
    sy=(label.height()-pixmap.height())//2 + (y*pixmap.height()//image.height) + 1
    QTest.mouseClick(label, Qt.MouseButton.LeftButton, pos=QPoint(sx,sy))


def test_reference_picker_uses_native_pixels_and_never_edits_artwork(tmp_path):
    app=QApplication.instance() or QApplication([])
    window=MainWindow()
    window.show()
    try:
        original=Image.new('RGBA',(6,6),(0,0,0,0))
        four=[(200,20,30,255),(0,0,0,0),(33,145,220,129),(255,222,10,255)]
        for (x,y),rgba in zip(((1,1),(2,1),(1,2),(2,2)),four):
            original.putpixel((x,y),rgba)
        image_bytes=original.tobytes()
        filename=tmp_path/'exact_rgba.png';original.save(filename)
        window.reference_button.click()
        app.processEvents()
        dock=window.reference_dock
        assert dock.add_references([filename])==1
        dock.zoom_slider.setValue(4)
        app.processEvents()
        assert dock.isVisible() and dock.preview_label.pixmap() is not None
        before=window.current_image().tobytes()
        dirty=window._dirty
        history_depth=len(window.history.undo_stack) if hasattr(window.history,'undo_stack') else None

        # Transparent reference pixel must not pick checkerboard color or exit eyedropper.
        window.tool.setCurrentText('Eyedropper')
        _click_source_pixel(dock,0,0)
        assert window.tool.currentText()=='Eyedropper'
        _click_source_pixel(dock,1,2)
        assert window.paint_color==(33,145,220,129)
        assert window.tool.currentText()=='Pencil'
        assert window.current_image().tobytes()==before and window._dirty==dirty

        # Chameleon samples 2x2 from reference without painting it or the canvas.
        window.tool.setCurrentText('Chameleon (2×2)')
        _click_source_pixel(dock,1,1)
        assert window.chameleon_sample is not None
        assert [window.chameleon_sample.getpixel((x,y)) for y in range(2) for x in range(2)]==four
        assert window.current_image().tobytes()==before
        # A second reference click changes the held sample (does not stamp the preview).
        _click_source_pixel(dock,0,0)
        assert window.chameleon_sample.getpixel((0,0))==(0,0,0,0)
        _click_source_pixel(dock,1,1)
        assert window.tool.currentText()=='Chameleon (2×2)'
        assert Image.open(filename).convert('RGBA').tobytes()==image_bytes
        if history_depth is not None:
            assert len(window.history.undo_stack)==history_depth

        # Stamping on SHS canvas does change only its selected artwork layer.
        window.add_layer(Layer('Paint target',Image.new('RGBA',window.size_px)))
        window.canvas.chameleon_at(5,7)
        painted=window.selected_layer().image
        assert [painted.getpixel((5+x,7+y)) for y in range(2) for x in range(2)]==four
        assert Image.open(filename).convert('RGBA').tobytes()==image_bytes
        window.tool.setCurrentText('Pencil')
        window.tool.setCurrentText('Chameleon (2×2)')
        assert window.chameleon_sample is None  # previous reset contract preserved
    finally:
        window._dirty=False
        window.close()
