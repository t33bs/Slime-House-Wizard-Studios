"""Read-only PNG reference dock for Slime House Studios (not Slime Wizard).

Reference pixels may be sampled by Eyedropper or Chameleon; the references
themselves remain immutable and never become layers or exported artwork.
"""
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QDockWidget, QFileDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QScrollArea, QSlider, QVBoxLayout, QWidget,
)


MAX_IMAGE_PIXELS = 16_000_000
MAX_PREVIEW_SIDE = 4096


def read_reference_png(path):
    """Load a standalone, detached RGBA copy; reject unsupported/huge images."""
    path = Path(path)
    try:
        with Image.open(path) as source:
            if source.format != 'PNG':
                raise ValueError('Reference images must be PNG files.')
            if source.width < 1 or source.height < 1 or source.width * source.height > MAX_IMAGE_PIXELS:
                raise ValueError('Reference PNG is too large (maximum 16 million pixels).')
            source.load()
            return source.convert('RGBA').copy()
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError(f'Could not open the reference PNG: {path.name}') from exc


def make_checkerboard(image):
    """Prepare a visual-only RGBA preview; never modify the source reference."""
    from PIL import ImageDraw
    background = Image.new('RGBA', image.size, (51, 60, 73, 255))
    squares = ImageDraw.Draw(background)
    step = 8
    for y in range(0, image.height, step):
        for x in range(0, image.width, step):
            if (x // step + y // step) % 2:
                squares.rectangle((x, y, min(x + step - 1, image.width - 1),
                                         min(y + step - 1, image.height - 1)),
                                  fill=(73, 84, 100, 255))
    background.alpha_composite(image.convert('RGBA'))
    return background


def reference_pixel_from_preview(click_x, click_y, label_size, preview_size, source_size):
    """Map a label click to an exact native reference pixel, including letterboxing.

    QLabel centers a pixmap when the dock's minimum preview label is larger than
    the displayed image. Use the *actual* preview pixmap dimensions, not the
    requested slider zoom (which can be capped for large references).
    """
    lw, lh = map(int, label_size)
    pw, ph = map(int, preview_size)
    sw, sh = map(int, source_size)
    if min(lw, lh, pw, ph, sw, sh) <= 0:
        return None
    left = (lw - pw) // 2
    top = (lh - ph) // 2
    rx = int(click_x) - left
    ry = int(click_y) - top
    if not (0 <= rx < pw and 0 <= ry < ph):
        return None
    return min(sw - 1, rx * sw // pw), min(sh - 1, ry * sh // ph)


class ReferencePreview(QLabel):
    """Translate clicks to source pixels; never paint on reference data."""

    def __init__(self, dock):
        super().__init__('Add a PNG to preview it here.')
        self.dock = dock

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dock.handle_preview_click(event.position().x(), event.position().y())
            event.accept()
            return
        super().mousePressEvent(event)


class ReferenceDock(QDockWidget):
    """Resizable, closable right dock with a PNG reference list and crisp preview."""

    def __init__(self, parent=None):
        super().__init__('PNG References — Read-only Sampling', parent)
        self.setObjectName('SHSPNGReferenceDock')
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable |
                         QDockWidget.DockWidgetFeature.DockWidgetMovable |
                         QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.setMinimumWidth(280)
        self.references = {}  # File paths -> detached RGBA PIL images, in memory only
        self._selected_path = None
        self._preview_source = None

        body = QWidget(self)
        layout = QVBoxLayout(body)
        self.info_label = QLabel('Read-only references. Select Eyedropper (I) to pick a color or Chameleon (2×2) to pick a pattern; then paint or stamp on the SHS canvas.')
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        actions = QHBoxLayout()
        self.add_button = QPushButton('＋ Add PNG References')
        self.add_button.setToolTip('Choose PNG references; with Eyedropper or Chameleon selected, click the preview to sample without editing it.')
        self.add_button.clicked.connect(self.choose_references)
        actions.addWidget(self.add_button)
        self.remove_button = QPushButton('Remove Selected')
        self.remove_button.clicked.connect(self.remove_selected)
        actions.addWidget(self.remove_button)
        layout.addLayout(actions)
        self.reference_list = QListWidget()
        self.reference_list.setObjectName('SHSPNGReferenceList')
        self.reference_list.setMaximumHeight(140)
        self.reference_list.currentItemChanged.connect(self.on_reference_selected)
        layout.addWidget(self.reference_list)
        zoom_row = QHBoxLayout()
        zoom_row.addWidget(QLabel('Reference zoom'))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(1, 8)
        self.zoom_slider.setValue(2)
        self.zoom_slider.valueChanged.connect(self.refresh_preview)
        zoom_row.addWidget(self.zoom_slider)
        self.zoom_label = QLabel('2×')
        zoom_row.addWidget(self.zoom_label)
        layout.addLayout(zoom_row)
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setObjectName('SHSPNGReferencePreviewScroll')
        self.preview_scroll.setWidgetResizable(False)
        self.preview_label = ReferencePreview(self)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(240, 220)
        self.preview_scroll.setWidget(self.preview_label)
        layout.addWidget(self.preview_scroll, 1)
        self.setWidget(body)

    def choose_references(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, 'Choose reference PNG images', '', 'PNG images (*.png)')
        if paths:
            self.add_references(paths)

    def add_references(self, paths):
        """Add multiple PNGs. Failed files report an error without disturbing art."""
        errors = []
        last_added = None
        for filename in paths:
            path = str(Path(filename).expanduser().resolve())
            if path in self.references:
                last_added = path
                continue
            try:
                image = read_reference_png(path)
            except (ValueError, OSError) as exc:
                errors.append(f'{Path(path).name}: {exc}')
                continue
            self.references[path] = image
            item = QListWidgetItem(Path(path).name)
            item.setData(Qt.ItemDataRole.UserRole, path)
            item.setToolTip(path)
            self.reference_list.addItem(item)
            last_added = path
        if last_added is not None:
            for i in range(self.reference_list.count()):
                if self.reference_list.item(i).data(Qt.ItemDataRole.UserRole) == last_added:
                    self.reference_list.setCurrentRow(i)
                    break
        if errors:
            QMessageBox.warning(self, 'Some references could not be opened', '\n'.join(errors[:5]))
        return len(self.references)

    def on_reference_selected(self, current, previous=None):
        self._selected_path = current.data(Qt.ItemDataRole.UserRole) if current else None
        image = self.references.get(self._selected_path)
        self._preview_source = make_checkerboard(image) if image is not None else None
        self.refresh_preview()

    def refresh_preview(self, value=None):
        if self._preview_source is None:
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText('Add a PNG to preview it here.')
            self.preview_label.resize(260, 220)
            self.zoom_label.setText(f'{self.zoom_slider.value()}×')
            return
        image = self._preview_source
        # Avoid unbounded allocations for very large user-supplied references.
        requested = self.zoom_slider.value()
        zoom = min(requested, MAX_PREVIEW_SIDE / max(image.size))
        width = max(1, int(round(image.width * zoom)))
        height = max(1, int(round(image.height * zoom)))
        rendered = image.resize((width, height), Image.Resampling.NEAREST)
        image_bytes = rendered.tobytes()
        qimage = QImage(image_bytes, rendered.width, rendered.height,
                        QImage.Format.Format_RGBA8888).copy()
        self.preview_label.setText('')
        self.preview_label.setPixmap(QPixmap.fromImage(qimage))
        self.preview_label.resize(width, height)
        self.zoom_label.setText(f'{requested}×' if zoom == requested else f'{zoom:.2g}× max')

    def handle_preview_click(self, click_x, click_y):
        """Sample the unmodified RGBA source, never the checkerboard preview."""
        image = self.references.get(self._selected_path)
        editor = self.parentWidget()
        if image is None or editor is None:
            return False
        tool = editor.tool.currentText()
        if tool not in ('Eyedropper', 'Chameleon (2×2)'):
            editor.statusBar().showMessage('Select Eyedropper (I) or Chameleon (2×2) to sample this reference.', 4000)
            return False
        pixmap = self.preview_label.pixmap()
        if pixmap is None or pixmap.isNull():
            return False
        point = reference_pixel_from_preview(
            click_x, click_y,
            (self.preview_label.width(), self.preview_label.height()),
            (pixmap.width(), pixmap.height()), image.size,
        )
        if point is None:
            return False  # ignored: click on label padding or outside image
        return editor.sample_reference_at(image, *point)

    def remove_selected(self):
        row = self.reference_list.currentRow()
        if row < 0:
            return
        item = self.reference_list.takeItem(row)
        self.references.pop(item.data(Qt.ItemDataRole.UserRole), None)
        self._selected_path = None
        self._preview_source = None
        if self.reference_list.count():
            self.reference_list.setCurrentRow(min(row, self.reference_list.count() - 1))
        else:
            self.refresh_preview()
