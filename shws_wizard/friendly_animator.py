"""Slime House Friendly Animator v0.43.0: independent creature animation workshop."""
import sys
from copy import deepcopy
import math
import subprocess
import tempfile
import logging
from pathlib import Path
from PIL import Image, ImageSequence
from PySide6.QtCore import Qt, QTimer, Signal, QSettings, QThread, QStandardPaths
from PySide6.QtGui import QImage, QPixmap, QIcon, QPainter, QPen, QColor, QCursor
from pathlib import Path
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QSplitter,QLabel,
 QPushButton,QToolButton,QListWidget,QComboBox,QSpinBox,QFormLayout,QFileDialog,QMessageBox,QScrollArea,QCheckBox, QSlider, QTabBar, QMenu, QInputDialog, QColorDialog, QAbstractItemView, QFrame)
from shws_wizard.studio.release_config import APP_VERSION, UPDATE_MANIFEST_URL, UPDATE_PUBLIC_KEY_B64
from shws_wizard.studio.update_manager import check_update, download_verified_installer
from shws_wizard.studio.resource_checks import bundled_resource_report
from shws_wizard.studio.canvas_navigation import geometry as canvas_geometry, zoom_at
from shws_wizard.studio.viewport_handles import visible_handle_position
from shws_wizard.studio.asset_hit_test import choose_drag_layer
from shws_wizard.studio.timeline_tools import timeline_summary, onion_composite
from shws_wizard.studio.pet_suite_model import PetSuiteModel
from shws_wizard.studio.edit_history import EditHistory
from shws_wizard.studio.slimer_tool import SlimerSelection, composite_selection_layers
from shws_wizard.studio.animation_registry import available_animation_names, preferred_animation
from shws_wizard.studio.signal_guard import blocked_signals
from shws_wizard.studio.preview_timing import frame_at_time
from shws_wizard.studio.playback_clock import PlaybackClock
from shws_wizard.studio.playback_resume import resume_position
from shws_wizard.studio.timeline_retime import retime_elapsed
from shws_wizard.studio.technical_checks import check_animation
from shws_wizard.studio.workspace_identity import animation_key
from shws_wizard.studio.recovery import (recovery_path, read_recovery, discard_recovery,
    list_project_recoveries, write_project_recovery, discard_project_recovery)

def wizard_slime_app_icon():
    """Reuse the launcher artwork for the running application's window icon."""
    candidates = []
    bundle = getattr(sys, '_MEIPASS', None)
    if bundle:
        candidates.append(Path(bundle) / 'shws_wizard' / 'studio' / 'assets' / 'wizard_slime.ico')
        candidates.append(Path(bundle) / 'shws_wizard' / 'studio' / 'assets' / 'wizard_slime_icon.png')
    assets = Path(__file__).resolve().parent / 'studio' / 'assets'
    candidates.extend((assets / 'wizard_slime.ico', assets / 'wizard_slime_icon.png'))
    for path in candidates:
        if path.is_file():
            icon = QIcon(str(path))
            if not icon.isNull():
                return icon
    return QIcon()

def pixmap(img,size=260):
    rgba=img.convert('RGBA');data=rgba.tobytes('raw','RGBA')
    q=QImage(data,rgba.width,rgba.height,rgba.width*4,QImage.Format.Format_RGBA8888).copy()
    return QPixmap.fromImage(q).scaled(size,size,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.FastTransformation)

class SlimerColorTabs(QTabBar):
    """Named selection tabs with the small compatibility API of the old picker."""
    currentTextChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setExpanding(False)
        self.setUsesScrollButtons(True)
        self.currentChanged.connect(self._emit_current_text)

    def _emit_current_text(self, index):
        if index >= 0:
            self.currentTextChanged.emit(self.tabText(index))

    def addItem(self, name):
        return self.addTab(name)

    def addItems(self, names):
        for name in names:
            self.addItem(name)

    def currentText(self):
        index = self.currentIndex()
        return self.tabText(index) if index >= 0 else ''

    def setCurrentText(self, name):
        for index in range(self.count()):
            if self.tabText(index) == name:
                self.setCurrentIndex(index)
                return
        raise ValueError(f'Unknown Slimer selection tab: {name}')


class PoseTimelineList(QListWidget):
    """Keep Qt drag-time selection changes from loading the wrong pose.

    During an InternalMove Qt updates the *visual* row order first and may
    emit currentRowChanged before the rowsMoved callback reconciles the saved
    model. Loading that premature index can commit the old live artwork into
    the wrong saved pose. After drop, the owner reorders the model by identity
    and explicitly loads the moved snapshot.
    """

    def dropEvent(self, event):
        # In SHWS the Suite is embedded in a host QMainWindow; QWidget.window()
        # would return the outer host instead of the owning Wizard editor.
        owner = self.parentWidget()
        while owner is not None and not isinstance(owner, Suite):
            owner = owner.parentWidget()
        if owner is not None and getattr(owner, '_slimer_pending_layer', None) is not None:
            owner.status.setText('Apply Move or Cancel the unconfirmed Slimer layer before reordering poses.')
            event.ignore()
            return
        was_blocked = self.blockSignals(True)
        try:
            super().dropEvent(event)
        finally:
            self.blockSignals(was_blocked)


class DragCanvas(QLabel):
    """Pixel-space hit testing with movable parts and bottom-right resize handles."""
    moved=Signal(int,int)
    resized=Signal(int,int)
    picked=Signal(int)
    anchor_chosen=Signal(int,int)
    angle_chosen=Signal(float)
    view_changed=Signal()
    cleaner_stroke=Signal(int,int)
    cleaner_stroke_start=Signal()
    slimer_stroke=Signal(int,int,bool)
    slimer_stroke_start=Signal()
    slimer_drag=Signal(int,int,str)
    slimer_drag_start=Signal()
    slimer_drag_end=Signal()
    def __init__(self):
        super().__init__();self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMouseTracking(True);self._last=None;self._image_size=(128,128)
        self.parts=[];self.selected=-1;self._action=None;self.anchor_mode=False;self.anchors={};self.angles={}
        self.zoom=1.0;self.pan_x=0.0;self.pan_y=0.0;self._pan_last=None;self._art=None;self.asset_controls_enabled=False;self.slimer_active=False;self.cleaner_active=False;self._cleaner_painting=False;self._slimer_painting=False;self.slimer_transform_mode=False;self._slimer_last=None;self.slimer_bounds=None;self._slimer_handle=None
        # The canvas, not the left sidebar, owns this compact overlay.
        # Its choices do not affect project pixels or exported artwork.
        self.asset_handle_mode = 'move_x'
        self._asset_picker_names = ()
        self._create_canvas_handle_menu()

    def _create_canvas_handle_menu(self):
        self.handle_panel = QFrame(self)
        self.handle_panel.setObjectName('canvasHandlePanel')
        self.handle_panel.setStyleSheet("""
            QFrame#canvasHandlePanel { background: #20332e; border: 1px solid #6c947b;
                                       border-radius: 7px; }
            QFrame#canvasHandlePanel QLabel { color: #e5f5e4; border: none; }
            QFrame#canvasHandlePanel QPushButton { text-align: left; padding: 5px;
                                                    background: #314d3d; color: #f3f9ed; }
            QFrame#canvasHandlePanel QComboBox { background: #324b42; color: white;
                                                 border: 1px solid #759783; padding: 4px; }
        """)
        self.handle_panel.setFixedWidth(194)
        layout = QVBoxLayout(self.handle_panel)
        layout.setContentsMargins(6, 5, 6, 5)
        layout.setSpacing(4)
        self.handle_menu_button = QPushButton('▸ Transform handles · X')
        self.handle_menu_button.setCheckable(True)
        self.handle_menu_button.setToolTip('Show or hide the canvas transform menu. Edit Selection enables or disables handles.')
        layout.addWidget(self.handle_menu_button)
        self.handle_menu_details = QWidget(self.handle_panel)
        details = QVBoxLayout(self.handle_menu_details)
        details.setContentsMargins(0, 2, 0, 0)
        details.setSpacing(4)
        details.addWidget(QLabel('Active Asset Library layer'))
        self.handle_layer_picker = QComboBox(self.handle_menu_details)
        self.handle_layer_picker.setToolTip('Choose which layer to edit. Apply Move or Cancel before changing a staged Slimer layer.')
        details.addWidget(self.handle_layer_picker)
        details.addWidget(QLabel('Visible handle'))
        self.handle_mode_picker = QComboBox(self.handle_menu_details)
        self.handle_mode_picker.addItem('X — Move horizontally', 'move_x')
        self.handle_mode_picker.addItem('Y — Move vertically', 'move_y')
        self.handle_mode_picker.addItem('R — Rotate in degrees', 'rotate')
        self.handle_mode_picker.addItem('S — Resize artwork', 'resize')
        self.handle_mode_picker.setToolTip('Only the selected handle is shown on the canvas. Resize scales artwork, not its transparent padding.')
        details.addWidget(self.handle_mode_picker)
        self.handle_status = QLabel('Use Edit Selection to enable handles')
        self.handle_status.setWordWrap(True)
        details.addWidget(self.handle_status)
        layout.addWidget(self.handle_menu_details)
        self.handle_menu_details.hide()  # Collapsed by default.
        self.handle_menu_button.toggled.connect(self._toggle_canvas_handle_menu)
        self.handle_mode_picker.currentIndexChanged.connect(self._canvas_handle_mode_changed)
        self.handle_panel.setVisible(True)
        self._position_canvas_handle_menu()

    def _position_canvas_handle_menu(self):
        if not hasattr(self, 'handle_panel'):
            return
        self.handle_panel.adjustSize()
        self.handle_panel.move(max(3, self.width() - self.handle_panel.width() - 8), 8)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_canvas_handle_menu()

    def _toggle_canvas_handle_menu(self, expanded):
        self.handle_menu_details.setVisible(bool(expanded))
        self._refresh_canvas_handle_header()
        self._position_canvas_handle_menu()

    def _refresh_canvas_handle_header(self):
        mode = {'move_x': 'X', 'move_y': 'Y', 'rotate': 'R', 'resize': 'S'}[self.asset_handle_mode]
        prefix = '▾' if self.handle_menu_button.isChecked() else '▸'
        self.handle_menu_button.setText(f'{prefix} Transform handles · {mode}')

    def _canvas_handle_mode_changed(self, index):
        mode = self.handle_mode_picker.itemData(index)
        if mode in ('move_x', 'move_y', 'rotate', 'resize'):
            self.asset_handle_mode = mode
            self._refresh_canvas_handle_header()
            self.sync_canvas_handle_layers(self.parts, self.selected,
                                           getattr(self, 'slimer_staged_part', None) is not None)
            self.update()

    def set_canvas_handle_mode(self, mode):
        if mode not in ('move_x', 'move_y', 'rotate', 'resize'):
            raise ValueError('Unknown canvas handle mode')
        self.handle_mode_picker.setCurrentIndex(('move_x','move_y','rotate','resize').index(mode))
        self.asset_handle_mode = mode
        self._refresh_canvas_handle_header()
        self.update()

    def sync_canvas_handle_layers(self, parts, selected, pending=False):
        names = tuple(f'{i + 1}. {p.get("name", f"Layer {i + 1}")}' for i, p in enumerate(parts))
        if names != self._asset_picker_names or self.handle_layer_picker.count() != len(names):
            self._asset_picker_names = names
            was_blocked = self.handle_layer_picker.blockSignals(True)
            try:
                self.handle_layer_picker.clear()
                self.handle_layer_picker.addItems(names)
            finally:
                self.handle_layer_picker.blockSignals(was_blocked)
        if self.handle_layer_picker.currentIndex() != selected:
            was_blocked = self.handle_layer_picker.blockSignals(True)
            try:
                self.handle_layer_picker.setCurrentIndex(selected)
            finally:
                self.handle_layer_picker.blockSignals(was_blocked)
        self.handle_layer_picker.setEnabled(not pending)
        self.handle_status.setText(
            ('Handles ON • ' + {'move_x': 'X', 'move_y': 'Y', 'rotate': 'R', 'resize': 'S'}[self.asset_handle_mode]
             if self.asset_controls_enabled else 'Handles OFF • click Edit Selection')
            + (' • Apply/Cancel before changing layer' if pending else ''))

    def _geometry(self):
        return canvas_geometry(self.width(),self.height(),*self._image_size,self.zoom,self.pan_x,self.pan_y)
    def _pixel(self,pos):
        scale,ox,oy=self._geometry()
        return ((pos.x()-ox)/scale,(pos.y()-oy)/scale)
    def set_art(self,pixmap):
        self._art=pixmap
        self.update()
    def paintEvent(self,event):
        if self._art is None:return
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform,False)
        scale,ox,oy=self._geometry()
        painter.drawPixmap(round(ox),round(oy),max(1,round(self._image_size[0]*scale)),max(1,round(self._image_size[1]*scale)),self._art)
        if self.slimer_active and self.slimer_transform_mode and self.slimer_bounds is not None:
            x0,y0,x1,y1=self.slimer_bounds
            left=ox+x0*scale;top=oy+y0*scale
            width=max(1,(x1-x0)*scale);height=max(1,(y1-y0)*scale)
            painter.setPen(QPen(QColor('#b5ff8d'),2,Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(round(left),round(top),round(width),round(height))
            if self.slimer_transform_mode:
                # Square resize handle and round rotation handle stay visible at any zoom.
                painter.setPen(QPen(QColor('#172d24'),2))
                painter.setBrush(QColor('#aaff80'))
                painter.drawRect(round(left+width-5),round(top+height-5),10,10)
                painter.setBrush(QColor('#75c9ff'))
                painter.drawEllipse(round(left+width/2-5),round(top-25),10,10)
                painter.setPen(QPen(QColor('#75c9ff'),2))
                painter.drawLine(round(left+width/2),round(top-15),round(left+width/2),round(top))
        # Editable Asset Library layers use four mutually exclusive visible handles.
        # Draw in widget coordinates, not in the exported image or pose pixels.
        if (self.asset_controls_enabled and not self.slimer_active and
                0 <= self.selected < len(self.parts) and
                self.parts[self.selected].get('visible', True)):
            corners, handles, pivot = self._asset_transform_geometry(self.selected)
            def screen(point):
                return (round(ox + point[0] * scale), round(oy + point[1] * scale))
            points = [screen(p) for p in corners]
            painter.setPen(QPen(QColor('#a7cc91'), 1, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for a, b in zip(points, points[1:] + points[:1]):
                painter.drawLine(*a, *b)
            colors = {'move_x': '#f5c35b', 'move_y': '#9eea86', 'rotate': '#75c9ff', 'resize': '#f3c77a'}
            labels = {'move_x': 'X', 'move_y': 'Y', 'rotate': 'R', 'resize': 'S'}
            action = self.asset_handle_mode
            screen_handle = self._asset_handle_screen(action)
            if screen_handle is not None:
                cx, cy = map(round, screen_handle)
                if action == 'rotate':
                    px, py = screen(pivot)
                    # Do not draw an enormous line across a zoomed-in canvas
                    # when the real pivot lies outside the visible widget.
                    if 0 <= px < self.width() and 0 <= py < self.height():
                        painter.setPen(QPen(QColor('#75c9ff'), 1))
                        painter.drawLine(px, py, cx, cy)
                painter.setPen(QPen(QColor('#142b29'), 2))
                painter.setBrush(QColor(colors[action]))
                painter.drawEllipse(cx - 10, cy - 10, 20, 20)
                painter.setPen(QPen(QColor('#152b29'), 2))
                painter.drawText(cx - 9, cy - 9, 18, 18,
                                 Qt.AlignmentFlag.AlignCenter, labels[action])
        painter.end()
    def _asset_transform_geometry(self, index):
        """Canvas-space X, Y, rotation handles for the selected artwork only.

        Visual positions rotate with the asset, but X and Y dragging remain
        constrained to the canvas axes. Handle sizes stay constant on screen.
        """
        pivot, rotation_handle, bounds = self._selected_rotation_geometry(index)
        left, top, right, bottom = bounds
        cx, cy = (left + right) / 2, (top + bottom) / 2
        scale = max(self._geometry()[0], 0.01)
        offset = 17 / scale
        theta = math.radians(self.angles.get(index, 0))
        ct, st = math.cos(theta), math.sin(theta)
        def rotate(point):
            dx, dy = point[0] - pivot[0], point[1] - pivot[1]
            return (pivot[0] + dx * ct - dy * st,
                    pivot[1] + dx * st + dy * ct)
        corners = [rotate(p) for p in ((left, top), (right, top),
                                       (right, bottom), (left, bottom))]
        handles = {
            'move_x': rotate((right + offset, cy)),
            'move_y': rotate((cx, bottom + offset)),
            'rotate': rotation_handle,
            'resize': rotate((right + offset, bottom + offset)),
        }
        return corners, handles, pivot

    def _asset_handle_screen(self, action=None):
        """Reachable widget-space handle, even when zoom crops its true edge.

        The selection's content geometry remains in canvas coordinates, but
        editing affordances live in screen pixels. Use the same position for
        both drawing and hit testing; otherwise a visible handle may be dead.
        """
        if not 0 <= self.selected < len(self.parts):
            return None
        corners, handles, _ = self._asset_transform_geometry(self.selected)
        mode = action or self.asset_handle_mode
        scale, ox, oy = self._geometry()
        points = [(ox + x * scale, oy + y * scale) for x, y in corners]
        actual_x, actual_y = handles[mode]
        desired = (ox + actual_x * scale, oy + actual_y * scale)
        blocked = None
        if self.handle_panel.isVisible():
            panel = self.handle_panel.geometry()
            blocked = (panel.left(), panel.top(), panel.right() + 1, panel.bottom() + 1)
        return visible_handle_position(desired, points, self.width(), self.height(),
                                       blocked=blocked)

    def _asset_transform_hit(self, pos):
        """Hit-test the *visible* X/Y/R/S handle, including at high zoom."""
        if (not self.asset_controls_enabled or self.slimer_active or
                not 0 <= self.selected < len(self.parts) or
                not self.parts[self.selected].get('visible', True)):
            return None
        action = self.asset_handle_mode
        screen_pos = self._asset_handle_screen(action)
        if screen_pos is None:
            return None
        distance = math.hypot(pos.x() - screen_pos[0], pos.y() - screen_pos[1])
        return action if distance <= 13 else None

    def _selected_rotation_geometry(self, index):
        """Pivot, handle and occupied bounds for the selected asset.

        Slimer layers are full-canvas PNGs containing a small selected region.
        Their rotation affordance must be next to the actual artwork rather
        than a full canvas-width away (and potentially off screen).
        """
        part = self.parts[index]
        w, h = part['image'].size
        # Geometry follows actual opaque/translucent artwork, not padded PNG.
        occupied = part['image'].getchannel('A').getbbox() or (0, 0, w, h)
        left, top, right, bottom = occupied
        ax, ay = self.anchors.get(index, [w // 2, h // 2])
        pivot = (part['x'] + ax, part['y'] + ay)
        theta = math.radians(self.angles.get(index, 0))
        radius = max(14, round(max(right - left, bottom - top) * 0.65))
        handle = (pivot[0] + radius * math.cos(theta - math.pi / 2),
                  pivot[1] + radius * math.sin(theta - math.pi / 2))
        return pivot, handle, (part['x'] + left, part['y'] + top,
                               part['x'] + right, part['y'] + bottom)

    def _slimer_hit_handle(self,pos):
        if not self.slimer_bounds:return None
        scale,ox,oy=self._geometry()
        x0,y0,x1,y1=self.slimer_bounds
        x=pos.x();y=pos.y();right=ox+x1*scale;bottom=oy+y1*scale
        mid=ox+(x0+x1)*scale/2;top=oy+y0*scale
        if abs(x-mid)<=12 and abs(y-(top-20))<=12:return 'rotate'
        if abs(x-right)<=12 and abs(y-bottom)<=12:return 'scale'
        return None
    def wheelEvent(self,event):
        # Zoom around the pointer so the artwork beneath it stays in place.
        steps=event.angleDelta().y()/120
        if not steps:return
        self.zoom,self.pan_x,self.pan_y=zoom_at(self.width(),self.height(),*self._image_size,self.zoom,self.pan_x,self.pan_y,event.position().x(),event.position().y(),steps)
        self.update();self.view_changed.emit();event.accept()
    def reset_view(self):
        self.zoom=1.0;self.pan_x=0.0;self.pan_y=0.0
        self.update();self.view_changed.emit()
    def _part_pixel_hit(self, index, x, y):
        """Hit the exact alpha rendered for this asset, not its padded PNG bounds.

        The owning Suite supplies a model-backed evaluator, including joint
        rotation and parent attachments. The self-contained fallback keeps
        DragCanvas usable by lightweight standalone Qt tests.
        """
        target=getattr(self, 'model_pixel_hit', None)
        if target is not None:
            return bool(target(index, x, y))
        part=self.parts[index]
        image=part['image'].convert('RGBA')
        canvas=Image.new('RGBA', self._image_size)
        px,py=int(part['x']),int(part['y'])
        canvas.paste(image,(px,py))
        angle=float(self.angles.get(index,0))
        if angle % 360:
            ax,ay=self.anchors.get(index,[image.width//2,image.height//2])
            canvas=canvas.rotate(angle,Image.Resampling.NEAREST,
                                 center=(px+ax,py+ay),expand=False)
        xi,yi=int(x),int(y)
        return (0 <= xi < canvas.width and 0 <= yi < canvas.height and
                canvas.getpixel((xi,yi))[3] > 0)

    def mousePressEvent(self,event):
        if self.cleaner_active and event.button()==Qt.MouseButton.LeftButton and not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            x,y=self._pixel(event.position())
            self._cleaner_painting=True
            self.cleaner_stroke_start.emit()
            self.cleaner_stroke.emit(int(x),int(y))
            event.accept();return
        if self.slimer_active and event.button() in (Qt.MouseButton.LeftButton,Qt.MouseButton.RightButton) and not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            x,y=self._pixel(event.position())
            if self.slimer_transform_mode and event.button()==Qt.MouseButton.LeftButton:
                self._slimer_last=(x,y);self._slimer_handle=self._slimer_hit_handle(event.position());self.slimer_drag_start.emit();event.accept();return
            self._slimer_painting=True;self._slimer_erase=event.button()==Qt.MouseButton.RightButton
            self.slimer_stroke_start.emit()
            self.slimer_stroke.emit(int(x),int(y),self._slimer_erase);event.accept();return
        if event.button()==Qt.MouseButton.MiddleButton or (event.button()==Qt.MouseButton.LeftButton and event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self._pan_last=event.position();event.accept();return
        if event.button()==Qt.MouseButton.LeftButton:
            x,y=self._pixel(event.position());self._last=(x,y);self._action=None
            handle=self._asset_transform_hit(event.position())
            if handle is not None:
                self._action=handle
                event.accept()
                return
            # A staged layer with handles hidden is not being edited.
            # It must not accidentally move while waiting for Apply/Cancel.
            if (getattr(self, 'slimer_staged_part', None) is not None
                    and not self.asset_controls_enabled):
                self._last=None
                event.accept()
                return
            if self.anchor_mode and 0<=self.selected<len(self.parts):
                p=self.parts[self.selected]
                self.anchor_chosen.emit(round(x-p["x"]),round(y-p["y"]))
                self._last=None
                return
            if 0<=self.selected<len(self.parts):
                p=self.parts[self.selected]
                pivot, handle, occupied = self._selected_rotation_geometry(self.selected)
                # The dedicated R handle above takes precedence. An invisible
                # old blue handle must not remain clickable after Edit is off.
                # Alt+drag is a rotation gesture on the staged layer itself.
                # The blue handle also works without holding a key.
                if (self.asset_controls_enabled
                        and getattr(self, 'slimer_staged_part', None) is p
                        and event.modifiers() & Qt.KeyboardModifier.AltModifier
                        and occupied[0] <= x < occupied[2]
                        and occupied[1] <= y < occupied[3]):
                    self._action='rotate';return
                right=p['x']+p['image'].width;bottom=p['y']+p['image'].height
                if abs(x-right)<=4 and abs(y-bottom)<=4:self._action='resize'
            if not self._action:
                # Slimer layers have full-canvas transparent PNGs; their image
                # rectangle must NOT claim clicks on transparent pixels. Give
                # the asset explicitly selected in the library priority if its
                # rendered artwork is under this click, even beneath later
                # Slimer layers. A staged move remains the sole editable layer.
                hit = choose_drag_layer(
                    self.parts, self.selected, x, y, self._part_pixel_hit,
                    staged=getattr(self, 'slimer_staged_part', None))
                if hit is not None:
                    self.picked.emit(hit)
                    self._action='move'
            if not self._action:self._last=None
        super().mousePressEvent(event)
    def mouseMoveEvent(self,event):
        if self._cleaner_painting:
            x,y=self._pixel(event.position())
            self.cleaner_stroke.emit(int(x),int(y))
            event.accept();return
        if self.slimer_active and self._slimer_last is not None:
            x,y=self._pixel(event.position());dx=round(x-self._slimer_last[0]);dy=round(y-self._slimer_last[1])
            if dx or dy:
                mode=self._slimer_handle or ('rotate' if event.modifiers() & Qt.KeyboardModifier.AltModifier else ('scale' if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else 'move'))
                self.slimer_drag.emit(dx,dy,mode)
                self._slimer_last=(self._slimer_last[0]+dx,self._slimer_last[1]+dy)
            event.accept();return
        if self._slimer_painting:
            x,y=self._pixel(event.position());self.slimer_stroke.emit(int(x),int(y),self._slimer_erase);event.accept();return
        if self._pan_last is not None:
            delta=event.position()-self._pan_last
            self.pan_x+=delta.x();self.pan_y+=delta.y();self._pan_last=event.position()
            self.update();self.view_changed.emit();event.accept();return
        if self._last is not None and self._action:
            x,y=self._pixel(event.position());dx=round(x-self._last[0]);dy=round(y-self._last[1])
            if self._action=='rotate':
                p=self.parts[self.selected]
                ax,ay=self.anchors.get(self.selected,[p['image'].width//2,p['image'].height//2])
                angle=math.degrees(math.atan2(y-(p['y']+ay),x-(p['x']+ax)))+90
                self.angle_chosen.emit(round(angle)%360)
                return
            if dx or dy:
                if self._action=='resize':self.resized.emit(dx,dy)
                elif self._action=='move_x':self.moved.emit(dx,0)
                elif self._action=='move_y':self.moved.emit(0,dy)
                else:self.moved.emit(dx,dy)
                self._last=(self._last[0]+dx,self._last[1]+dy)
        super().mouseMoveEvent(event)
    def mouseReleaseEvent(self,event):
        self._last=None;self._action=None;self._pan_last=None;self._slimer_painting=False;self._cleaner_painting=False;self._slimer_last=None;self._slimer_handle=None;self.slimer_drag_end.emit();super().mouseReleaseEvent(event)

class UpdateCheckWorker(QThread):
    result = Signal(object, str)
    def run(self):
        try:
            payload = check_update(APP_VERSION, UPDATE_MANIFEST_URL, UPDATE_PUBLIC_KEY_B64)
            self.result.emit(payload, '')
        except Exception as exc:
            self.result.emit(None, str(exc))

class UpdateDownloadWorker(QThread):
    result = Signal(object, str)
    def __init__(self, payload, destination, parent=None):
        super().__init__(parent)
        self.payload, self.destination = payload, destination
    def run(self):
        try:
            self.result.emit(str(download_verified_installer(self.payload, self.destination)), '')
        except Exception as exc:
            self.result.emit(None, str(exc))

class Suite(QMainWindow):
    def __init__(self):
        super().__init__();self.setWindowTitle(f'Slime Wizard — v{APP_VERSION}');self.setWindowIcon(wizard_slime_app_icon());self.resize(1380,850)
        self._shs_edit=None;self.model=PetSuiteModel();self.selected=-1;self.frame=0;self.playframe=0;self.history=EditHistory();self._project_histories={0:self.history};self.advanced=False;self._loading_pose=False;self._pose_draft_key=None;self._pose_live_id=None;self._pose_draft_dirty=False;self._next_pose_capture_pending=False;self._workspace_frames={};self._workspace_tab_keys=[];self._switching_tab=False;self._active_workspace=None;self._project_name="Untitled Creature";self.settings=QSettings("SlimeHouse", "FriendlyAnimator");self._projects={};self._project_id=0;self._active_project_id=0;self._project_paths={};self._projects[0]=self.model;self._project_labels={0:self._project_name};self._project_frames={0:{}};self._project_views={0:(1.0,0.0,0.0)};self._project_selected={0:-1};self._project_animation={0:preferred_animation(self.model)};self._dirty_projects=set();self._saved_fingerprints={0:self.model.content_fingerprint()}
        geometry=self.settings.value("window_geometry",None)
        if geometry:self.restoreGeometry(geometry)
        QTimer.singleShot(0,self.ensure_window_visible)
        from shws_wizard.studio.ui_pixel_theme import PIXEL_THEME_QSS
        self.setStyleSheet(PIXEL_THEME_QSS)
        base=QWidget();self.setCentralWidget(base);outer=QVBoxLayout(base)
        outer.setContentsMargins(6,5,6,6);outer.setSpacing(4)
        # Phase 99: purely decorative title strip, no actions or shortcuts.
        pixel_header=QWidget();pixel_header.setObjectName('pixelAppHeader')
        header_layout=QHBoxLayout(pixel_header)
        header_layout.setContentsMargins(12,3,14,3);header_layout.setSpacing(11)
        header_portrait=QLabel();header_portrait.setObjectName('pixelAppPortrait')
        header_portrait.setFixedSize(44,44)
        portrait_file=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent.parent))/'shws_wizard'/'studio'/'assets'/'slime_buddy_blue_portrait.png'
        if portrait_file.is_file():
            header_portrait.setPixmap(QPixmap(str(portrait_file)).scaled(
                44,44,Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation))
        header_layout.addWidget(header_portrait)
        header_title=QLabel('Slime Wizard');header_title.setObjectName('pixelAppTitle')
        header_layout.addWidget(header_title)
        header_subtitle=QLabel('✦ Pixel Art  •  Animation  •  Creature Builder ✦')
        header_subtitle.setObjectName('pixelAppSubtitle')
        header_layout.addWidget(header_subtitle)
        header_layout.addStretch(1)
        outer.addWidget(pixel_header)
        top_container=QWidget();top=QHBoxLayout(top_container);top.setContentsMargins(0,0,0,0)
        top_scroll=QScrollArea();top_scroll.setWidget(top_container);top_scroll.setWidgetResizable(True);top_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded);top_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);top_scroll.setFixedHeight(42);outer.addWidget(top_scroll)
        for title,callback in [('Import PNG assets',self.import_assets),('Open creature',self.open_project),('New creature',self.new_project),('Save creature',self.save_project),('Save creature as…',self.save_project_as),('Export Sprite Sheet',self.export),('Export GIF / APNG',self.export_animated),('Export Frame PNG',self.export_current_frame),('Export All Frames',self.export_all_frames),('Edit Frame in SHS',self.edit_frame_in_shs),('Set SHS Location',self.choose_shs_location),('Reload SHS Edit',self.reload_shs_edit),('Replace Frame PNG',self.replace_current_frame_png)]:
            b=QPushButton(title)
            b.setProperty('uiRole', 'primary' if title in ('New creature','Open creature','Save creature') else 'success' if title.startswith('Export') else 'toolbar')
            b.clicked.connect(callback);top.addWidget(b)
        update_button=QPushButton('Check for updates');update_button.clicked.connect(self.check_for_updates);top.addWidget(update_button)
        self.status=QLabel('Welcome! Import PNG parts, pick an animation, and create your first pose.');self.status.setObjectName('pixelStatusBar');outer.addWidget(self.status)
        mode_container=QWidget();modebar=QHBoxLayout(mode_container);modebar.setContentsMargins(0,0,0,0)
        mode_scroll=QScrollArea();mode_scroll.setWidget(mode_container);mode_scroll.setWidgetResizable(True);mode_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded);mode_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);mode_scroll.setFixedHeight(42);outer.addWidget(mode_scroll)
        self.mode=QPushButton('Easy Mode 🌱  •  Switch to Advanced');self.mode.clicked.connect(self.toggle_mode);modebar.addWidget(self.mode)
        undo=QPushButton('↶ Undo');undo.setProperty('uiRole','toolbar');undo.clicked.connect(self.undo);modebar.addWidget(undo)
        redo=QPushButton('↷ Redo');redo.setProperty('uiRole','toolbar');redo.clicked.connect(self.redo);modebar.addWidget(redo)
        # Keep the only main Slime Buddy switch in the high-level toolbar,
        # freeing the canvas from the obsolete station chooser and readiness row.
        self.buddy_toggle=QCheckBox('🌱 Slime Buddy ON / OFF')
        self.buddy_toggle.setObjectName('topSlimeBuddyToggle')
        self.buddy_toggle.setChecked(self.settings.value('slime_buddy_enabled',True,type=bool))
        self.buddy_toggle.setToolTip('Optional technical guidance. Preference is saved. All editing tools work while OFF.')
        from PySide6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence('Ctrl+Z'),self,activated=self.undo)
        QShortcut(QKeySequence('Ctrl+Shift+Z'),self,activated=self.redo)
        QShortcut(QKeySequence('Ctrl+Y'),self,activated=self.redo)
        # App-wide brush sizing follows whichever painting tool is active.
        # ApplicationShortcut also works while focus is in the canvas or side panels.
        for key, delta in (('+', 1), ('=', 1), ('-', -1)):
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
            shortcut.activated.connect(lambda step=delta: self.adjust_active_brush_size(step))
        self.onion=QCheckBox('Ghost nearby poses');self.onion.setChecked(False);self.onion.setToolTip('Show faint neighboring poses to help you judge movement. Guides are never exported.');# Ghost controls are now located at the top of the left tool panel.
        self.onion_next=QCheckBox('Also show next');self.onion_next.setToolTip('Show the following pose as another faint guide.');self.onion_next.toggled.connect(self.refresh)
        self.onion.stateChanged.connect(self.refresh)
        modebar.addStretch(1)
        modebar.addWidget(self.buddy_toggle)
        splitter=QSplitter(Qt.Orientation.Horizontal);outer.addWidget(splitter,1)
        left=QWidget();left.setObjectName('pixelToolRegion');ll=QVBoxLayout(left);ll.setContentsMargins(6,5,6,5)
        tool_title=QLabel('✦ TOOLS & ASSETS');tool_title.setObjectName('pixelLeftToolsHeading');tool_title.setProperty('uiRole','sectionTitle');ll.addWidget(tool_title)
        ghost_row=QHBoxLayout();ghost_row.addWidget(self.onion);ghost_row.addWidget(self.onion_next);ll.addLayout(ghost_row)
        asset_header=QHBoxLayout();ll.addLayout(asset_header)
        asset_title=QLabel('▣ ASSET LIBRARY');asset_title.setObjectName('pixelAssetsHeading');asset_title.setProperty('uiRole','sectionTitle');asset_header.addWidget(asset_title)
        self.show_hidden_assets=QCheckBox('Show inactive');self.show_hidden_assets.setObjectName('pixelInactiveAssetToggle')
        self.show_hidden_assets.setToolTip('Show layers inherited from other poses that are hidden here. Showing these rows does not make their artwork visible or change earlier poses.')
        self.show_hidden_assets.setChecked(False)
        self.show_hidden_assets.toggled.connect(self.sync_slimer_asset_labels)
        asset_header.addWidget(self.show_hidden_assets)
        self.assets=QListWidget();self.assets.setObjectName('pixelAssetLibraryList');self.assets.currentRowChanged.connect(self.select_asset);ll.addWidget(self.assets,1)
        # Asset Library I/O stays beside the assets themselves, rather than
        # hiding behind the project-level Import PNG button.
        asset_io=QHBoxLayout();ll.addLayout(asset_io)
        self.library_import=QPushButton('Import Asset');self.library_import.setProperty('uiRole','success')
        self.library_import.setToolTip('Import one or more transparent PNGs as independently editable Asset Library layers.')
        self.library_import.clicked.connect(self.import_assets)
        asset_io.addWidget(self.library_import)
        self.library_export_shs=QPushButton('Export for SHS');self.library_export_shs.setProperty('uiRole','toolbar')
        self.library_export_shs.setToolTip('Save a valid PNG of the selected layer for opening in Slime House Studios. Does not launch SHS.')
        self.library_export_shs.clicked.connect(self.export_asset_for_shs)
        asset_io.addWidget(self.library_export_shs)
        self.pose_asset_remove=QPushButton('Remove asset from this pose');self.pose_asset_remove.setProperty('uiRole','danger')
        self.pose_asset_remove.setToolTip('Hide the selected asset only in the current pose; other poses keep their artwork. Undo is available.')
        self.pose_asset_remove.clicked.connect(self.remove_asset_from_current_pose);ll.addWidget(self.pose_asset_remove)
        self.pose_asset_restore=QPushButton('Restore asset in this pose')
        self.pose_asset_restore.clicked.connect(self.restore_asset_in_current_pose);ll.addWidget(self.pose_asset_restore)
        self.pose_asset_state=QLabel('Select a saved pose and asset to manage visibility.');self.pose_asset_state.setObjectName('pixelAssetVisibilityHint')
        self.pose_asset_state.setWordWrap(True)
        ll.addWidget(self.pose_asset_state)
        order=QHBoxLayout();ll.addLayout(order)
        for label,offset in [('Move layer up',1),('Move layer down',-1)]:
            b=QPushButton(label);b.clicked.connect(lambda checked=False,d=offset:self.move_layer(d));order.addWidget(b)
        self.active_asset_label=QLabel('Selected layer: None • Handles OFF');self.active_asset_label.setObjectName('pixelActiveAssetLabel')
        self.active_asset_label.setWordWrap(True)
        # Phase 100: visual color lives in the central theme instead of an inline override.
        self.active_asset_label.setToolTip('The selected layer and handle state. Choose a handle from the collapsible menu on the canvas.')
        ll.addWidget(self.active_asset_label)
        form=QFormLayout();ll.addLayout(form)
        self.x=QSpinBox();self.y=QSpinBox();self.w=QSpinBox();self.h=QSpinBox()
        for spin in (self.x,self.y,self.w,self.h):spin.setRange(-2048 if spin in (self.x,self.y) else 1,2048);spin.valueChanged.connect(self.update_asset)
        for label,spin in [('X',self.x),('Y',self.y),('Width (px)',self.w),('Height (px)',self.h)]:form.addRow(label,spin)
        self.lock=QCheckBox('Lock aspect ratio');self.lock.setObjectName('pixelLockAspectToggle');self.lock.setChecked(True);ll.addWidget(self.lock)
        self.angle=QSpinBox();self.angle.setRange(-360,360);self.angle.setSuffix('°');self.angle.setToolTip('Rotate the selected asset in degrees around its joint dot. For a Slimer layer, the joint starts at the center of the highlighted artwork.');form.addRow('Turn part (degrees)',self.angle);self.angle.valueChanged.connect(self.turn_part)
        self.turn_tip=QLabel('🌱 Tip: place a yellow joint dot, then turn an arm, leg or tail around it.');self.turn_tip.setWordWrap(True);ll.addWidget(self.turn_tip)
        ll.addWidget(QLabel('Connect body parts • optional'))
        self.parent_picker=QComboBox();ll.addWidget(self.parent_picker)
        attach_buttons=QHBoxLayout();ll.addLayout(attach_buttons)
        connect=QPushButton('🔗 Connect selected part');connect.setToolTip('Keep this part attached when its parent moves.');connect.clicked.connect(self.connect_part);attach_buttons.addWidget(connect)
        disconnect=QPushButton('Unlink');disconnect.clicked.connect(self.disconnect_part);attach_buttons.addWidget(disconnect)
        self.anchor_button=QPushButton('📍 Place a joint dot')
        self.anchor_button.setCheckable(True)
        self.anchor_button.setToolTip('Select a part, click here, then click where it bends or connects on the canvas. Click again to exit.')
        self.anchor_button.toggled.connect(self.toggle_anchor_mode)
        ll.addWidget(self.anchor_button)
        self.joint_tip=QLabel('Joint dots help you see where parts connect. Optional!')
        self.joint_tip.setWordWrap(True);ll.addWidget(self.joint_tip)
        ll.addWidget(QLabel('QUICK FIXES • selected part'))
        quick=QHBoxLayout();ll.addLayout(quick)
        for label,axis in [('↔ Flip left/right','horizontal'),('↕ Flip up/down','vertical')]:
            b=QPushButton(label);b.setToolTip('Mirror the selected part. Undo restores it.');b.clicked.connect(lambda checked=False,a=axis:self.flip_selected(a));quick.addWidget(b)
        alignment=QHBoxLayout();ll.addLayout(alignment)
        for label,axis in [('Center ↔','horizontal'),('Center ↕','vertical'),('Center both','both')]:
            b=QPushButton(label);b.setToolTip('Move the selected part to the middle of the canvas on this axis.');b.clicked.connect(lambda checked=False,a=axis:self.center_selected(a));alignment.addWidget(b)
        self.reset=QPushButton('↺ Restore original size');self.reset.setToolTip('Restore the PNG’s imported width and height in one undoable step.');self.reset.clicked.connect(self.reset_size);ll.addWidget(self.reset)
        self.advanced_label=QLabel('Advanced tools: exact X/Y coordinates and frame editing')
        ll.addWidget(self.advanced_label)
        slimer_title=QLabel('✦ SLIMER TOOL  •  select pixels, then place');slimer_title.setObjectName('pixelSlimerHeading');slimer_title.setProperty('uiRole','sectionTitle');ll.addWidget(slimer_title)
        self.slimer_toggle=QPushButton('Activate Slimer Tool');self.slimer_toggle.setProperty('uiRole','tool');self.slimer_toggle.setCheckable(True);self.slimer_toggle.toggled.connect(self.slimer_toggle_mode);ll.addWidget(self.slimer_toggle)
        self.slimer_drag_toggle=QPushButton('Drag selected pixels (Shift=resize, Alt=rotate)')
        self.slimer_drag_toggle.setCheckable(True)
        self.slimer_drag_toggle.setToolTip('Legacy floating selection transform; the visible Edit Selection button now creates a directly draggable Asset Library layer.')
        self.slimer_drag_toggle.toggled.connect(self.slimer_drag_mode)
        # The old floating-selection toggle remains for legacy project/tests,
        # but must not be another step in the beginner-facing Slimer workflow.
        self.slimer_drag_toggle.hide()
        self.slimer_edit_asset=QPushButton('Edit Selection • Create / Show Handles')
        self.slimer_edit_asset.setToolTip('One button: highlighted pixels become an editable layer; afterward toggle the chosen handle from the collapsible menu on the canvas.')
        # This is a command button, not a checkable toggle: a failed Edit
        # Selection must never visually turn editing ON.  The real canvas
        # handle mode owns the indicator via _show_asset_transform_controls().
        self.slimer_edit_asset.setProperty('editingActive', False)
        self.slimer_edit_asset.clicked.connect(self.slimer_create_editable_layer)
        ll.addWidget(self.slimer_edit_asset)
        self.asset_handle_tip=QLabel('Choose X, Y, Rotate or Resize from the on-canvas Transform handles menu. Edit Selection shows/hides the chosen handle.')
        self.asset_handle_tip.setWordWrap(True)
        # The picker and mode options live on the canvas, so do not duplicate
        # guidance or controls in the crowded left sidebar.
        self.asset_handle_tip.hide()
        self.slimer_cancel_asset=QPushButton('Cancel Unconfirmed Layer');self.slimer_cancel_asset.setProperty('uiRole','danger')
        self.slimer_cancel_asset.setToolTip('Discard the staged Slimer layer without erasing any original pixels. Stay on this canvas.')
        self.slimer_cancel_asset.clicked.connect(self.slimer_cancel_editable_layer)
        ll.addWidget(self.slimer_cancel_asset)
        self._slimer_pending_layer=None
        self._slimer_pending_part=None
        self._slimer_pending_source=None
        self._slimer_pending_mask=None
        self._slimer_pending_move_original=None
        self._slimer_previous_selected_part=None
        # Finish Selecting is retired: Edit Selection stages the real asset.
        self.slimer_selection_undo=[];self.slimer_selection_redo=[];self._slimer_numeric_replaying=False
        selection_actions=QHBoxLayout();ll.addLayout(selection_actions)
        for label,callback in [('Slimer Undo',self.slimer_undo_selection),('Slimer Redo',self.slimer_redo_selection)]:
            b=QPushButton(label);b.clicked.connect(callback);selection_actions.addWidget(b)
        cleaner_title=QLabel('✦ SLIME CLEANER  •  erase to transparency');cleaner_title.setObjectName('pixelCleanerHeading');cleaner_title.setProperty('uiRole','sectionTitle');ll.addWidget(cleaner_title)
        self.cleaner_toggle=QPushButton('Activate Slime Cleaner');self.cleaner_toggle.setProperty('uiRole','tool')
        self.cleaner_toggle.setCheckable(True)
        self.cleaner_toggle.setToolTip('Independent eraser. Left-drag to clear pixels on the current pose. Undo restores a stroke.')
        self.cleaner_toggle.toggled.connect(self.cleaner_toggle_mode)
        ll.addWidget(self.cleaner_toggle)
        self.cleaner_brush=QSpinBox();self.cleaner_brush.setRange(1,32);self.cleaner_brush.setValue(1)
        self.cleaner_brush.setToolTip('While Slime Cleaner is active, press + or = to increase size and - to decrease it.');form.addRow('Cleaner brush size (+ / -)',self.cleaner_brush)
        self.slimer_brush=QSpinBox();self.slimer_brush.setRange(1,32);self.slimer_brush.setValue(1);self.slimer_brush.setToolTip('While Slimer is active, press + or = to increase highlight size and - to decrease it.');form.addRow('Slimer brush size (+ / -)',self.slimer_brush)
        self.slimer_dx=QSpinBox();self.slimer_dy=QSpinBox();self.slimer_turn=QSpinBox();self.slimer_scale=QSpinBox()
        for spin in (self.slimer_dx,self.slimer_dy):spin.setRange(-2048,2048)
        self.slimer_turn.setRange(-360,360);self.slimer_turn.setToolTip('While editing a Slimer layer, rotate that layer in degrees. Changes are confirmed on Apply Move.');self.slimer_scale.setRange(10,800);self.slimer_scale.setValue(100)
        for label,spin in [('Slime move X',self.slimer_dx),('Slime move Y',self.slimer_dy),('Slime rotate °',self.slimer_turn),('Slime size %',self.slimer_scale)]:form.addRow(label,spin)
        for spin in (self.slimer_dx,self.slimer_dy,self.slimer_turn,self.slimer_scale):
            spin.valueChanged.connect(lambda value, control=spin: self.slimer_numeric_changed(control, value))
            if spin is self.slimer_scale:
                spin.setToolTip('After Edit Selection, resize the selected layer in percent. Slimer layers scale visible artwork around their pivot, not the transparent canvas.')
            elif spin is not self.slimer_turn:
                spin.setToolTip('Adjust a highlighted selection before creating its layer; use Asset Library controls after Edit Selection.')
        self.slimer_move_original=QCheckBox('Move Original Pixels (uncheck to Copy Pixels)')
        self.slimer_move_original.setChecked(True)
        self.slimer_move_original.setToolTip('Checked: clear selected pixels from the active pose when placing. Unchecked: copy them and keep the originals. Existing saved poses stay unchanged.')
        ll.addWidget(self.slimer_move_original)
        self.slimer_preview_label=QLabel('Activate Slimer to preview the canvas without editing guides')
        self.slimer_preview_label.setMinimumHeight(142)
        self.slimer_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slimer_preview_label.setObjectName('pixelSlimerCleanPreview')
        self.slimer_preview_label.setToolTip('Clean live canvas preview, including the editable Slimer layer. No selection tint, outlines, X/Y/R/S handles, onion ghosts, or joint dots.')
        slimer_actions=QHBoxLayout();ll.addLayout(slimer_actions)
        for label,callback in [('Place as Layer',self.slimer_place_layer),('Place Frame',self.slimer_place_frame),('Clear Selection',self.slimer_clear)]:
            button=QPushButton(label);button.clicked.connect(callback);slimer_actions.addWidget(button)
            if label == 'Place Frame':
                self.slimer_place_frame_button = button
                button.setProperty('uiRole','primary')
                button.setToolTip('Capture the CURRENT canvas as the NEXT new pose without changing the previous saved pose. Move the legs, Apply Move, then Place Frame. To overwrite a saved pose intentionally, choose Save Current Pose.')
        self.slimer_apply_move=QPushButton('✓ Apply Move • Continue Selecting');self.slimer_apply_move.setProperty('uiRole','success')
        self.slimer_apply_move.setToolTip('Confirm the staged editable layer and its source-pixel policy on this canvas. No new pose is created. Then highlight another region.')
        self.slimer_apply_move.clicked.connect(self.slimer_apply_move_to_pose)
        ll.addWidget(self.slimer_apply_move)
        self.slimer_confirm_all=QPushButton('✓ Confirm All Placements')
        self.slimer_confirm_all.setToolTip('Place all color-tab selections together as one undoable layer. Each tab keeps its own movement, rotation and size. For one tab, use Place as Layer or Place Frame.')
        self.slimer_confirm_all.clicked.connect(self.slimer_confirm_all_placements)
        self.slimer_confirm_all.hide()  # Retained for legacy regression tests only.
        # Independent, color-coded selection masks for animation phases.
        # The color is a canvas overlay only; exports never include it.
        self.slimer_phase_colors={'Start':'#54e88a','Middle':'#58b9ff','End':'#d38bff'}
        self.slimer_phase_masks={}
        self.slimer_phase_transforms={}  # Each highlight phase owns its own move/rotate/scale.
        self.slimer_phase_histories={}  # Undo/Redo stays with its color tab.
        self.slimer_phase_picker=SlimerColorTabs()
        self.slimer_phase_picker.addItems(self.slimer_phase_colors)
        self.slimer_phase_picker.setToolTip('Click a color tab to edit its independent pixel selection and transform. Tabs scroll when many colors are used.')
        self.slimer_phase_picker.currentTextChanged.connect(self.slimer_switch_phase)
        self.slimer_phase_picker.hide()  # One sequential selection; no phase tabs in the UI.
        phase_buttons=QHBoxLayout();ll.addLayout(phase_buttons)
        self.slimer_color_button=QPushButton('Change highlight color')
        color_button=self.slimer_color_button
        color_button.clicked.connect(self.slimer_choose_color)
        phase_buttons.addWidget(color_button)
        add_phase=QPushButton('+ New phase')
        add_phase.clicked.connect(self.slimer_add_phase)
        add_phase.hide()  # No new selection tabs.
        self.slimer_selection=None
        self._update_slimer_color_button()

        self.left_tool_scroll=self.scroll_panel(left)
        self.left_tool_scroll.setObjectName('pixelLeftToolsScroll')
        self.left_tool_scroll.verticalScrollBar().setMinimumWidth(19)
        splitter.addWidget(self.left_tool_scroll)
        middle=QWidget();middle.setObjectName('pixelCanvasRegion')
        middle_layout=QVBoxLayout(middle)
        middle_layout.setContentsMargins(6,4,6,4)
        middle_layout.setSpacing(4)
        # Vertical handle splits the *view*, not the actual sprite dimensions.
        # Both regions can be resized independently without editing pose pixels.
        self.canvas_timeline_splitter=QSplitter(Qt.Orientation.Vertical,middle)
        self.canvas_timeline_splitter.setObjectName('pixelCanvasTimelineSplitter')
        self.canvas_timeline_splitter.setHandleWidth(13)
        self.canvas_timeline_splitter.setChildrenCollapsible(False)
        self.canvas_timeline_splitter.setToolTip('Drag this bar up to see more poses, or down to enlarge the editing canvas.')
        middle_layout.addWidget(self.canvas_timeline_splitter,1)
        canvas_region=QWidget()
        canvas_region.setObjectName('pixelCanvasTopArea')
        ml=QVBoxLayout(canvas_region)
        ml.setContentsMargins(0,0,0,0)
        ml.setSpacing(4)
        # Keep the animation state selector internally for legacy project loading,
        # saved-pose navigation and export. Do not display recipe/preset choices.
        # It must not be added to the layout: the canvas should have no giant
        # Choose Animation button or dropdown above the timeline.
        self.anim=QComboBox(middle)
        self.anim.addItems(available_animation_names(self.model))
        self.anim.currentTextChanged.connect(self.change_anim)
        self.anim.hide()
        # No station dropdown or readiness button above the canvas.
        # Slime Buddy now provides optional, context-sensitive help in its
        # existing speech bubble in the comparison dock, and its toggle lives
        # beside Easy Mode / Undo / Redo near the top of the window.
        self.buddy_toggle.toggled.connect(self.refresh_buddy)
        self.buddy_toggle.toggled.connect(lambda enabled:self.settings.setValue('slime_buddy_enabled',enabled))
        self.refresh_buddy()
        canvas_title=QLabel('✦ BUILD YOUR POSE  •  Drag parts on the canvas');canvas_title.setObjectName('pixelCanvasHeading');canvas_title.setProperty('uiRole','sectionTitle');ml.addWidget(canvas_title)
        self.canvas=DragCanvas();self.canvas.model_pixel_hit=self._canvas_model_pixel_hit;self.canvas.handle_layer_picker.currentIndexChanged.connect(self.assets.setCurrentRow);self.canvas.handle_mode_picker.currentIndexChanged.connect(lambda _index: self._refresh_active_layer_label());self.canvas.cleaner_stroke.connect(self.cleaner_paint);self.canvas.cleaner_stroke_start.connect(self.cleaner_start_stroke);self.canvas.slimer_stroke.connect(self.slimer_paint);self.canvas.slimer_stroke_start.connect(self.slimer_start_stroke);self.canvas.slimer_drag.connect(self.slimer_drag_transform);self.canvas.slimer_drag_start.connect(self.slimer_start_transform);self.canvas.slimer_drag_end.connect(self.slimer_end_transform);self.canvas.moved.connect(self.drag_part);self.canvas.resized.connect(self.resize_drag);self.canvas.picked.connect(self.assets.setCurrentRow);self.canvas.anchor_chosen.connect(self.place_anchor);self.canvas.angle_chosen.connect(self.turn_part);self.canvas.setMinimumHeight(205);self.canvas.setObjectName('pixelMainCanvas');self.canvas.setStyleSheet('background:#161c38;border:2px solid #6986c7;border-radius:5px;');ml.addWidget(self.canvas,1);self.canvas.setToolTip('Expand Transform handles on the canvas to select a layer and one X, Y, Rotation, or Resize handle. Edit Selection enables or disables the chosen handle.')
        nav=QHBoxLayout();ml.addLayout(nav)
        canvas_nav_title=QLabel('Canvas view:');canvas_nav_title.setObjectName('pixelCanvasNavLabel');nav.addWidget(canvas_nav_title)
        fit=QPushButton('Fit to Canvas');fit.setObjectName('pixelCanvasFitButton');fit.setToolTip('Show the whole creature again (does not resize your artwork).');fit.clicked.connect(self.canvas.reset_view);nav.addWidget(fit)
        self.zoom_label=QLabel('100%');self.zoom_label.setObjectName('pixelZoomReadout');nav.addWidget(self.zoom_label)
        canvas_nav_tip=QLabel('Wheel: zoom  •  Middle-drag or Ctrl+drag: move view');canvas_nav_tip.setObjectName('pixelCanvasNavTip');nav.addWidget(canvas_nav_tip)
        nav.addStretch(1)
        self.canvas.view_changed.connect(self.canvas_view_changed)
        # Workspace tabs sit immediately below the main canvas, aligned to the left.
        tabline=QHBoxLayout();tabline.setContentsMargins(0,0,0,0);ml.addLayout(tabline)
        self.workspace_tabs=QTabBar();self.workspace_tabs.setObjectName('pixelWorkspaceTabs');self.workspace_tabs.setMovable(True);self.workspace_tabs.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu);self.workspace_tabs.customContextMenuRequested.connect(self.workspace_tab_context_menu)
        self.workspace_tabs.setExpanding(False);self.workspace_tabs.setUsesScrollButtons(True)
        self.workspace_tabs.setToolTip('Switch between open creature projects. Animations and poses are edited with their own controls.')
        self.workspace_tabs.currentChanged.connect(self.switch_workspace_tab)
        self.workspace_tabs.tabMoved.connect(self.workspace_tab_moved)
        tabline.addWidget(self.workspace_tabs,1)
        self.add_workspace=QPushButton('+');self.add_workspace.setObjectName('pixelWorkspaceAddButton');self.add_workspace.setFixedWidth(36)
        self.add_workspace.setToolTip('Open or create a creature project')
        self.add_workspace.clicked.connect(self.workspace_menu);tabline.addWidget(self.add_workspace)
        self.canvas_timeline_splitter.addWidget(canvas_region)
        timeline_content=QWidget()
        tl=QVBoxLayout(timeline_content)
        tl.setContentsMargins(0,0,4,0)
        tl.setSpacing(4)
        ml=tl
        timeline_title=QLabel('▣ POSE TIMELINE  •  Click a frame to edit');timeline_title.setObjectName('pixelTimelineHeading');timeline_title.setProperty('uiRole','sectionTitle');ml.addWidget(timeline_title)
        self.timeline=PoseTimelineList();self.timeline.setObjectName('pixelPoseTimeline');self.timeline.setFlow(QListWidget.Flow.LeftToRight);self.timeline.setMinimumHeight(124);self.timeline.setMaximumHeight(420);self.timeline.setIconSize(__import__('PySide6.QtCore',fromlist=['QSize']).QSize(82,82));self.timeline.setSpacing(5);self.timeline.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.timeline.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.timeline.setDragDropOverwriteMode(False)
        self.timeline.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.timeline.setDragEnabled(True)
        self.timeline.setAcceptDrops(True)
        self.timeline.model().rowsMoved.connect(self._timeline_rows_moved)
        self.timeline.currentRowChanged.connect(self.load_frame);ml.addWidget(self.timeline,1)
        timing=QHBoxLayout();ml.addLayout(timing)
        timing_caption=QLabel('How long should this pose last?');timing_caption.setObjectName('pixelTimelineTimingCaption');timing.addWidget(timing_caption)
        self.duration=QSpinBox();self.duration.setObjectName('pixelTimelineDuration');self.duration.setRange(40,2000);self.duration.setSingleStep(25);self.duration.setSuffix(' ms');self.duration.setValue(125)
        self.duration.setToolTip('Shorter means faster movement. Try 125 ms to start!')
        self.duration.valueChanged.connect(self.change_duration);timing.addWidget(self.duration);timing.addStretch(1)
        actions=QHBoxLayout();ml.addLayout(actions)
        for label,callback in [('Save Current Pose',self.save_frame),('Restore Previous Pose',self.restore_previous_timeline_pose),('Duplicate last frame',self.duplicate_frame),('Previous frame',self.prev_frame),('Next frame',self.next_frame)]:
            b=QPushButton(label)
            if label == 'Save Current Pose':b.setObjectName('pixelTimelineSavePose')
            elif label == 'Restore Previous Pose':b.setObjectName('pixelTimelineRestorePose')
            elif label == 'Duplicate last frame':b.setObjectName('pixelTimelineDuplicatePose')
            elif label == 'Previous frame':b.setObjectName('pixelTimelinePreviousPose')
            elif label == 'Next frame':b.setObjectName('pixelTimelineNextPose')
            b.clicked.connect(callback);actions.addWidget(b)
            if label == 'Save Current Pose':
                b.setToolTip('INTENTIONALLY replace this selected saved pose with the current canvas. To keep this pose unchanged and record your new leg movements as the NEXT frame, use Place Frame instead.')
        timeline_tools=QHBoxLayout();ml.addLayout(timeline_tools)
        for label,callback in [('➕ Insert pose after selected',self.insert_pose),('📋 Copy pose',self.copy_pose),('🗑 Remove pose',self.remove_pose),('← Shift pose',lambda:self.shift_pose(-1)),('Shift pose →',lambda:self.shift_pose(1))]:
            button=QPushButton(label)
            if label.startswith('➕ Insert'):button.setObjectName('pixelTimelineInsertPose')
            elif label.startswith('📋 Copy'):button.setObjectName('pixelTimelineCopyPose')
            elif label.startswith('🗑 Remove'):button.setObjectName('pixelTimelineRemovePose')
            elif label.startswith('← Shift'):button.setObjectName('pixelTimelineShiftLeft')
            elif label.startswith('Shift pose'):button.setObjectName('pixelTimelineShiftRight')
            button.setToolTip('Edit the saved poses in this animation. You can undo this change.');button.clicked.connect(callback);timeline_tools.addWidget(button)
        # One compact import control: clicking imports an exact independent PNG;
        # its dropdown arrow offers intentional compositing over the prior pose.
        self.pose_png_import_button=QToolButton()
        self.pose_png_import_button.setText('📥 Import Pose PNG');self.pose_png_import_button.setObjectName('pixelTimelineImportPose');self.pose_png_import_button.setProperty('uiRole','toolbar')
        self.pose_png_import_button.setToolTip('Click for an exact independent RGBA pose. Use the arrow for Build on Previous Pose, which keeps underlying artwork visible through transparency.')
        self.pose_png_import_button.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.pose_png_import_button.clicked.connect(lambda checked=False: self.import_pose_png())
        import_menu=QMenu(self.pose_png_import_button)
        import_menu.addAction('Import exact PNG as new pose',lambda checked=False: self.import_pose_png())
        import_menu.addAction('Build new pose over previous artwork',lambda checked=False: self.import_pose_png_overlay())
        self.pose_png_import_button.setMenu(import_menu)
        timeline_tools.insertWidget(1,self.pose_png_import_button)
        # The timeline scrolls its button rows independently when made compact.
        self.timeline_scroll=self.scroll_panel(timeline_content)
        self.timeline_scroll.setObjectName('pixelTimelineToolsScroll')
        self.timeline_scroll.setMinimumHeight(135)
        self.canvas_timeline_splitter.addWidget(self.timeline_scroll)
        self.canvas_timeline_splitter.setStretchFactor(0,3)
        self.canvas_timeline_splitter.setStretchFactor(1,2)
        stored_layout=self.settings.value('canvas_timeline_splitter_sizes',None)
        if isinstance(stored_layout,(list,tuple)) and len(stored_layout)==2:
            try:
                initial_layout=[max(210,int(stored_layout[0])),max(135,int(stored_layout[1]))]
            except (ValueError,TypeError):
                initial_layout=[425,285]
        else:
            initial_layout=[425,285]
        self.canvas_timeline_splitter.setSizes(initial_layout)
        splitter.addWidget(middle)
        # Phase 97 UI: the human's editor and Buddy's independent production
        # engine have separate workspaces. The two exchange assets only after
        # explicit approval; no generation engine is connected in this phase.
        right=QWidget();right.setObjectName('pixelRightRegion');right_layout=QVBoxLayout(right)
        right_layout.setContentsMargins(6,6,6,6);right_layout.setSpacing(6)
        self.right_splitter=QSplitter(Qt.Orientation.Vertical)
        self.right_splitter.setObjectName('buddyPreviewVerticalSplitter')
        self.right_splitter.setHandleWidth(7)
        self.right_splitter.setChildrenCollapsible(False)
        right_layout.addWidget(self.right_splitter,1)

        self.buddy_workspace_panel=QFrame()
        self.buddy_workspace_panel.setObjectName('slimeBuddyProductionWorkspace')
        bl=QVBoxLayout(self.buddy_workspace_panel);bl.setContentsMargins(11,10,11,10);bl.setSpacing(7)
        buddy_header=QHBoxLayout();bl.addLayout(buddy_header)
        buddy_header_label=QLabel('✦ SLIME BUDDY  •  PRODUCTION ASSISTANT')
        buddy_header_label.setObjectName('pixelBuddyWorkspaceHeading')
        buddy_header.addWidget(buddy_header_label,1)
        # Phase 101: one Buddy ON/OFF checkbox in the main toolbar only.
        buddy_line=QHBoxLayout();bl.addLayout(buddy_line)
        self.buddy_mascot=QLabel();self.buddy_mascot.setObjectName('pixelBuddyMascot');self.buddy_mascot.setFixedSize(86,86)
        mascot_dir=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent.parent))/'shws_wizard'/'studio'/'assets'
        mascot=mascot_dir/'slime_buddy_blue_portrait.png'
        if not mascot.is_file():mascot=mascot_dir/'slime_buddy_16bit.png'
        self.buddy_mascot.setPixmap(QPixmap(str(mascot)).scaled(86,86,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.FastTransformation))
        buddy_line.addWidget(self.buddy_mascot)
        self.buddy_bubble=QLabel('Hi! I am Slime Buddy!')
        self.buddy_bubble.setObjectName('pixelBuddySpeechBubble')
        self.buddy_bubble.setWordWrap(True)
        buddy_line.addWidget(self.buddy_bubble,1)

        production_label=QLabel('PRODUCTION WORKSPACE  •  FUTURE INTEGRATION')
        production_label.setObjectName('pixelBuddyProductionHeading')
        bl.addWidget(production_label)
        production_explainer=QLabel(
            'Buddy will produce pixel art, editable layers, and animations using HIS OWN system. '
            'Your canvas and manual Slime Wizard tools stay yours. Generated results will '
            'be reviewed before you import them.')
        production_explainer.setWordWrap(True)
        production_explainer.setObjectName('pixelBuddyProductionExplainer')
        bl.addWidget(production_explainer)
        self.buddy_production_status=QLabel('● Production engine not connected in this build')
        self.buddy_production_status.setObjectName('buddyProductionStatus')
        self.buddy_production_status.setWordWrap(True)
        bl.addWidget(self.buddy_production_status)
        self.buddy_handoff_status=QLabel('Planned handoff: request → independent generation → review → import approved assets')
        self.buddy_handoff_status.setWordWrap(True)
        self.buddy_handoff_status.setObjectName('pixelBuddyHandoffLabel')
        bl.addWidget(self.buddy_handoff_status)
        bl.addStretch(1)
        self.right_splitter.addWidget(self.buddy_workspace_panel)

        self.animation_preview_section=QFrame()
        self.animation_preview_section.setObjectName('collapsibleAnimationPreview')
        pv=QVBoxLayout(self.animation_preview_section)
        pv.setContentsMargins(10,9,10,9);pv.setSpacing(6)
        preview_header=QHBoxLayout();pv.addLayout(preview_header)
        preview_header_title=QLabel('▣ ANIMATION PREVIEW')
        preview_header_title.setObjectName('pixelAnimationPreviewHeading')
        preview_header.addWidget(preview_header_title,1)
        self.animation_preview_toggle=QPushButton('▾ Collapse');self.animation_preview_toggle.setProperty('uiRole','preview')
        self.animation_preview_toggle.setObjectName('animationPreviewCollapseButton')
        self.animation_preview_toggle.setToolTip('Collapse only Animation Preview to give Slime Buddy more space. Click again to restore every preview control.')
        self.animation_preview_toggle.clicked.connect(self.toggle_animation_preview)
        preview_header.addWidget(self.animation_preview_toggle)
        self.animation_preview_body=QWidget()
        self.animation_preview_body.setObjectName('animationPreviewBody')
        pv.addWidget(self.animation_preview_body,1)
        preview_body_layout=QVBoxLayout(self.animation_preview_body)
        preview_body_layout.setContentsMargins(0,0,0,0);preview_body_layout.setSpacing(4)
        # Only previews of the creature being edited belong here.
        clean_preview_title=QLabel('SLIMER PREVIEW • clean canvas, no tool overlays')
        clean_preview_title.setObjectName('pixelSlimerPreviewHeading')
        preview_body_layout.addWidget(clean_preview_title)
        preview_body_layout.addWidget(self.slimer_preview_label)
        creature_preview_title=QLabel('Your creature • frame preview')
        creature_preview_title.setObjectName('pixelCreaturePreviewHeading')
        preview_body_layout.addWidget(creature_preview_title)
        preview_zoom_row=QHBoxLayout();preview_body_layout.addLayout(preview_zoom_row)
        self.preview_zoom=150
        for label, action in [('−',-50),('+',50),('Fit',0)]:
            b=QPushButton(label);b.setObjectName({'−':'pixelPreviewZoomOut','+':'pixelPreviewZoomIn','Fit':'pixelPreviewZoomFit'}[label]);b.clicked.connect(lambda checked=False,step=action:self.change_preview_zoom(step));preview_zoom_row.addWidget(b)
        self.preview=QLabel();self.preview.setObjectName('pixelFramePreviewImage');self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter);self.preview.setMinimumSize(150,150)
        self.preview_scroll=QScrollArea();self.preview_scroll.setObjectName('pixelFramePreviewScroll');self.preview_scroll.setWidget(self.preview);self.preview_scroll.setWidgetResizable(False)
        self.preview_scroll.setMinimumHeight(145);preview_body_layout.addWidget(self.preview_scroll)
        self.play=QPushButton('▶ Play your animation');self.play.setObjectName('pixelPreviewPlayButton');self.play.setProperty('uiRole','success');self.play.setCheckable(True);preview_body_layout.addWidget(self.play)
        self.play.toggled.connect(self.play_toggled)
        speed_row=QHBoxLayout();preview_body_layout.addLayout(speed_row);speed_title=QLabel('Playback speed');speed_title.setObjectName('pixelPreviewSpeedHeading');speed_row.addWidget(speed_title)
        self.speed=QComboBox();self.speed.setObjectName('pixelPreviewSpeedSelect');self.speed.addItem('Slow • ½×',0.5);self.speed.addItem('Normal • 1×',1.0);self.speed.addItem('Fast • 2×',2.0);self.speed.setCurrentIndex(1);speed_row.addWidget(self.speed)
        self.loop=QCheckBox('Repeat animation');self.loop.setObjectName('pixelPreviewLoopCheck');self.loop.setChecked(True);preview_body_layout.addWidget(self.loop)
        self.loop.toggled.connect(self.restart_playback)
        self.speed.currentIndexChanged.connect(self.restart_playback)
        self.right_splitter.addWidget(self.animation_preview_section)
        saved_right_sizes=self.settings.value('buddy_preview_splitter_sizes',None)
        if isinstance(saved_right_sizes,list) and len(saved_right_sizes)==2:
            try:initial_right_sizes=[max(150,int(saved_right_sizes[0])),max(165,int(saved_right_sizes[1]))]
            except (ValueError,TypeError):initial_right_sizes=[300,380]
        else:initial_right_sizes=[300,380]
        self._expanded_right_sizes=list(initial_right_sizes)
        self.right_splitter.setSizes(initial_right_sizes)
        self._animation_preview_collapsed=False
        # Saved preference is applied after building every preview control.
        self.set_animation_preview_collapsed(self.settings.value('animation_preview_collapsed',False,type=bool),announce=False)
        splitter.addWidget(self.scroll_panel(right))
        # Apply the saved Buddy toggle after mascot + bubble exist.
        self.refresh_buddy()
        self.main_splitter=splitter
        self.comparison_panel=splitter.widget(2)
        self.comparison_toggle=QPushButton('👁 Hide previews')
        self.comparison_toggle.setToolTip('Hide the entire right dock for more canvas space. For Buddy-only expansion use the Animation Preview Collapse button instead.')
        self.comparison_toggle.clicked.connect(self.toggle_comparison)
        modebar.addWidget(self.comparison_toggle)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(7)
        saved=self.settings.value('splitter_sizes',None)
        if isinstance(saved,list) and len(saved)==3:
            try:splitter.setSizes([max(180,int(saved[0])), max(350,int(saved[1])), max(235,int(saved[2]))])
            except (ValueError,TypeError):splitter.setSizes([250,850,235])
        else:splitter.setSizes([250,850,235])
        self._comparison_sizes=[250,850,235]
        # Phase 15 recovery: always expose the preview dock on startup.
        # Earlier saved layouts could hide both Slimer and animation previews.
        # Users may still hide it manually using the comparison toggle.
        self.comparison_panel.show()
        # Persisted narrow docks can technically be visible while both previews
        # are clipped. Reserve enough width for the preview controls on restore.
        self.comparison_panel.setMinimumWidth(235)
        self.comparison_toggle.setText('👁 Hide previews')
        self.elapsed_ms=0
        self.playback_clock=PlaybackClock()
        self.timer=QTimer(self);self.timer.timeout.connect(self.tick);self.timer.start(25)
        self.recovery_timer=QTimer(self);self.recovery_timer.timeout.connect(self.autosave_recovery);self.recovery_timer.start(60000)
        self.change_anim(self.anim.currentText());self.toggle_mode(initial=True);self.add_workspace_tab("project",f"0::{self._project_name}");self.select_workspace_key(("project",f"0::{self._project_name}"))
        QTimer.singleShot(0,self.offer_recovery)
    @staticmethod
    def scroll_panel(content):
        """Keep controls accessible when a window is restored to a small display."""
        panel=QScrollArea()
        panel.setWidgetResizable(True)
        panel.setWidget(content)
        panel.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        panel.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        panel.setMinimumSize(0,0)
        return panel

    def ensure_window_visible(self):
        """Recover an off-screen saved window after monitor/resolution changes."""
        from shws_wizard.studio.window_geometry import fit_window_rect
        from PySide6.QtCore import QRect
        screens=QApplication.screens()
        if not screens:return
        available=[screen.availableGeometry() for screen in screens]
        r=self.frameGeometry()
        x,y,w,h=fit_window_rect((r.x(),r.y(),r.width(),r.height()),
            [(g.x(),g.y(),g.width(),g.height()) for g in available])
        if self.isMaximized():return
        if (x,y,w,h)!=(r.x(),r.y(),r.width(),r.height()):
            self.setGeometry(QRect(x,y,w,h))

    def check_for_updates(self):
        if not UPDATE_MANIFEST_URL or not UPDATE_PUBLIC_KEY_B64:
            QMessageBox.information(self, 'Updates not configured',
                'Secure updates will be enabled after the official release signing key and update feed are configured.\n'
                'You can still install official releases manually.')
            return
        if getattr(self, '_update_worker', None) and self._update_worker.isRunning():
            return
        self.status.setText('Checking for a signed update…')
        self._update_worker = UpdateCheckWorker(self)
        self._update_worker.result.connect(self.update_check_result)
        self._update_worker.start()

    def update_check_result(self, payload, error):
        if error:
            QMessageBox.warning(self, 'Update check failed', error)
        elif not payload:
            QMessageBox.information(self, 'Updates', 'You are running the latest available version.')
        else:
            answer = QMessageBox.question(self, 'Update available',
                f"Version {payload['version']} is available. Download its verified installer?\n"
                'Your open creature projects will not be closed or changed.',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if answer == QMessageBox.StandardButton.Yes:
                folder = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)) / 'updates'
                filename = f"SlimeHouseFriendlyAnimator-Setup-{payload['version']}.exe"
                self._update_download_worker = UpdateDownloadWorker(payload, folder / filename, self)
                self._update_download_worker.result.connect(self.update_download_result)
                self.status.setText('Downloading and verifying signed update…')
                self._update_download_worker.start()
                return
        self.status.setText('Update check finished.')

    def update_download_result(self, installer, error):
        if error:
            QMessageBox.warning(self, 'Update download failed', error)
            self.status.setText('Update download failed; current installation unchanged.')
            return
        answer = QMessageBox.question(self, 'Verified installer ready',
            'The update installer was downloaded and verified.\n'
            'Save any changes and close Friendly Animator to run the installer now?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            self.status.setText(f'Verified installer saved: {installer}')
            return
        if not self.confirm_unsaved_projects(list(self._projects)):
            self.status.setText('Update postponed; your projects remain open.')
            return
        # Windows cannot replace a running application. Launch the installer
        # independently and close the GUI; the installer handles file replacement.
        import subprocess
        try:
            if sys.platform != 'win32':
                raise RuntimeError('Installer handoff is supported on Windows only')
            subprocess.Popen([str(installer)], close_fds=True)
        except Exception as exc:
            QMessageBox.warning(self, 'Could not start installer', str(exc))
            return
        self.close()

    def show_technical_checks(self):
        """User-invoked technical checks; no automatic pop-ups or artistic judgments."""
        issues=check_animation(self.model,self.anim.currentText())
        if not issues:
            QMessageBox.information(self,'Animation check','No technical problems found in the saved poses.\nYour artistic choices are always yours!')
            return
        details='\n\n'.join(f'• {issue.message}\n  Try: {issue.action}' for issue in issues)
        QMessageBox.information(self,'Animation check',details)

    def refresh_buddy(self,*_):
        """Optional, nonjudgmental tool help without a redundant station menu."""
        enabled=self.buddy_toggle.isChecked()
        if hasattr(self,'buddy_mascot'):self.buddy_mascot.setVisible(enabled)
        if hasattr(self,'buddy_bubble'):self.buddy_bubble.setVisible(enabled)
        if enabled and hasattr(self,'buddy_bubble'):
            if self.slimer_toggle.isChecked():
                tip=('Highlight pixels → Edit Selection creates the editable layer. '
                     'Choose X, Y, Rotate or Resize in Transform handles on the canvas, '
                     'then Apply Move. Place Frame records this canvas as the NEXT pose; the previous saved pose stays unchanged.')
            elif not self.model.parts:
                tip=('Use Import PNG assets at the top to add your artwork. '
                     'You decide its appearance and how to assemble it.')
            else:
                tip=('Choose a part or pose to edit. Save Current Pose when ready, '
                     'then use Preview to check your animation. Your design is your choice.')
            self.buddy_bubble.setText(tip)

    def toggle_animation_preview(self):
        """Collapse only the preview, never the user's canvas or Buddy workspace."""
        self.set_animation_preview_collapsed(not self._animation_preview_collapsed)

    def set_animation_preview_collapsed(self, collapsed, *, announce=True):
        """Keep playback state, frame controls and rendered images intact when hidden."""
        collapsed=bool(collapsed)
        if collapsed == self._animation_preview_collapsed and not announce:
            return
        if collapsed and not self._animation_preview_collapsed:
            # Before the first show(), Qt splitters may report [0, 0].
            # Keep the user's last real expanded sizes rather than persisting
            # an uninitialized layout when restoring the collapsed preference.
            current=self.right_splitter.sizes()
            if len(current)==2 and all(value>0 for value in current):
                self._expanded_right_sizes=current
        self._animation_preview_collapsed=collapsed
        self.animation_preview_body.setVisible(not collapsed)
        self.animation_preview_toggle.setText('▸ Expand' if collapsed else '▾ Collapse')
        self.animation_preview_toggle.setToolTip(
            'Expand preview and playback controls.' if collapsed else
            'Collapse preview controls to enlarge the Slime Buddy production workspace.')
        if collapsed:
            self.right_splitter.setSizes([900,46])
        elif len(self._expanded_right_sizes)==2 and all(self._expanded_right_sizes):
            self.right_splitter.setSizes(self._expanded_right_sizes)
        else:
            self.right_splitter.setSizes([300,380])
        self.settings.setValue('animation_preview_collapsed',collapsed)
        if announce:
            self.status.setText('Animation Preview collapsed — more room for Slime Buddy.' if collapsed
                else 'Animation Preview expanded — your playback controls are back.')

    def toggle_comparison(self):
        if self.comparison_panel.isVisible():
            self._comparison_sizes=self.main_splitter.sizes()
            self.comparison_panel.hide()
            self.comparison_toggle.setText('👁 Show previews')
            self.status.setText('Previews hidden — enjoy the extra canvas room!')
        else:
            self.comparison_panel.show()
            sizes=self._comparison_sizes
            if len(sizes)==3 and sizes[2]>0:self.main_splitter.setSizes(sizes)
            self.comparison_toggle.setText('👁 Hide previews')
            self.status.setText('Animation previews restored. Drag the divider to adjust their width.')

    def workspace_tab_context_menu(self,pos):
        index=self.workspace_tabs.tabAt(pos)
        if index<0:return
        menu=QMenu(self)
        close=menu.addAction('✕ Close this tab')
        close.setEnabled(len(self._workspace_tab_keys)>1)
        action=menu.exec(self.workspace_tabs.mapToGlobal(pos))
        if action==close:self.close_workspace_tab(index)

    def close_workspace_tab(self,index):
        """Close only a creature project; timeline and pose controls are unaffected."""
        if not (0 <= index < len(self._workspace_tab_keys)):
            return
        kind, name = self._workspace_tab_keys[index]
        if kind != 'project':
            return
        project_id = int(name.split('::', 1)[0])
        self.close_creature_project(project_id)

    def autosave_recovery(self):
        self.preserve_pose_draft()
        # Keep an unplaced next pose in recovery without adding a timeline frame.
        # The model's live `parts` already contain the editable working canvas.
        if getattr(self, '_next_pose_capture_pending', False):
            self._remember_unplaced_next_pose()
        else:
            self.model.unplaced_next_pose = None
        # Every open creature has its own snapshot; switching tabs cannot overwrite it.
        self._projects[self._active_project_id]=self.model
        failures=[]
        for project_id, model in list(self._projects.items()):
            if not model.parts or not self.project_is_dirty(project_id):continue
            try:write_project_recovery(model,project_id)
            except Exception as exc:failures.append(str(exc))
        if failures:self.status.setText('Autosave incomplete: '+failures[0])

    def offer_recovery(self):
        paths=list_project_recoveries()
        legacy=recovery_path()
        if legacy.exists():paths.insert(0,legacy)
        if not paths:return
        answer=QMessageBox.question(self,'Recover creatures?',
            f'Found {len(paths)} creature recovery snapshot(s). Restore them as separate tabs?\n'
            'Choose No to discard the recovery copies.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if answer==QMessageBox.StandardButton.No:
            for path in paths:discard_recovery(path)
            return
        restored=0
        for path in paths:
            try:
                model=read_recovery(path)
                self.add_project(model,f'Recovered Creature {restored+1}')
                restored+=1
            except Exception as exc:
                QMessageBox.warning(self,'Recovery unavailable',f'{path.name}: {exc}')
        if restored:self.status.setText(f'Restored {restored} creature(s). Save each project to keep it permanently.')

    def closeEvent(self,event):
        self.preserve_pose_draft()
        if not self.confirm_unsaved_projects(list(self._projects)):
            event.ignore()
            return
        sizes=self.main_splitter.sizes() if self.comparison_panel.isVisible() else self._comparison_sizes
        self.settings.setValue('splitter_sizes',sizes)
        self.settings.setValue('canvas_timeline_splitter_sizes',self.canvas_timeline_splitter.sizes())
        self.settings.setValue('comparison_hidden',not self.comparison_panel.isVisible())
        self.settings.setValue('animation_preview_collapsed',self._animation_preview_collapsed)
        self.settings.setValue('buddy_preview_splitter_sizes',self._expanded_right_sizes if self._animation_preview_collapsed else self.right_splitter.sizes())
        for project_id in list(self._projects):discard_project_recovery(project_id)
        self.settings.setValue("window_geometry",self.saveGeometry())
        super().closeEvent(event)

    def workspace_tab_moved(self,from_index,to_index):
        key=self._workspace_tab_keys.pop(from_index)
        self._workspace_tab_keys.insert(to_index,key)

    def add_workspace_tab(self,kind,name):
        if kind != 'project':
            raise ValueError('Only open creature projects belong in the canvas tab strip')
        key = (kind, name)
        if key in self._workspace_tab_keys:
            return self._workspace_tab_keys.index(key)
        self._workspace_tab_keys.append(key)
        label = '🐾 ' + (name.split('::', 1)[1] if '::' in name else name)
        was_blocked = self.workspace_tabs.blockSignals(True)
        try:
            index = self.workspace_tabs.addTab(label)
        finally:
            self.workspace_tabs.blockSignals(was_blocked)
        return index

    def select_workspace_key(self,key):
        if key[0] != 'project':
            raise ValueError('Only creature projects can be selected in the canvas tab strip')
        index=self.add_workspace_tab(*key)
        self.workspace_tabs.setCurrentIndex(index)
        self.switch_workspace_tab(index)

    def switch_workspace_tab(self,index):
        if self._switching_tab or not (0 <= index < len(self._workspace_tab_keys)):
            return
        kind, name = self._workspace_tab_keys[index]
        if kind != 'project':
            return
        self._switching_tab = True
        try:
            self._active_workspace = (kind, name)
            project_id = int(name.split('::', 1)[0]) if '::' in name else 0
            self.activate_project(project_id)
            self.status.setText(f'Creature project: {self._project_name}')
        finally:
            self._switching_tab = False

    def workspace_menu(self):
        menu=QMenu(self)
        menu.addAction('🐾 New creature project',self.new_project)
        menu.addAction('📂 Open another creature',self.open_project)
        menu.addAction('✏ Rename current creature',self.rename_project)
        menu.exec(self.add_workspace.mapToGlobal(self.add_workspace.rect().bottomLeft()))

    def turn_part(self, angle):
        if not 0 <= self.selected < len(self.model.parts):return
        pending=getattr(self, '_slimer_pending_part', None)
        if pending is not None and self.model.parts[self.selected] is not pending:
            self.select_asset(self.selected)
            self.status.setText('Apply Move or cancel the staged Slimer layer before rotating another asset.')
            return
        if self.model.angles.get(self.selected, 0) == angle % 360:return
        self.remember()
        self.model.rotate_part(self.selected, angle)
        if hasattr(self,'angle'):
            with blocked_signals(self.angle):
                self.angle.setValue(round(angle)%360)
        # Both existing degree controls refer to the same editable Slimer asset
        # while it is staged; the old selection preview must not rotate instead.
        if (getattr(self, '_slimer_pending_part', None) is self.model.parts[self.selected]
                and hasattr(self, 'slimer_turn')):
            with blocked_signals(self.slimer_turn):
                self.slimer_turn.setValue(round(angle)%360)
            self._slimer_sync_numeric_values()
        self.refresh()

    def toggle_anchor_mode(self, enabled):
        self.canvas.anchor_mode=enabled
        self.anchor_button.setText('✓ Click your part to place the joint • Done' if enabled else '📍 Place a joint dot')
        self.status.setText('Click your selected part where it connects or bends.' if enabled else 'Joint placement finished.')
        # Joint dots are UI-only guides. Switching the placement tool must
        # show/hide them immediately without changing stored rotation pivots.
        if hasattr(self, 'canvas'):
            self.refresh()

    def place_anchor(self,x,y):
        if self.selected<0:return
        if not self._slimer_protect_staged_source('changing the joint on'):return
        self.remember()
        self.model.set_anchor(self.selected,x,y)
        self.anchor_button.setChecked(False)
        self.status.setText('Joint dot placed! Connected parts now follow parent turns.')
        self.refresh()

    def toggle_mode(self,initial=False):
        if not initial:self.advanced=not self.advanced
        self.mode.setText('Advanced Mode ⚙  •  Switch to Easy' if self.advanced else 'Easy Mode 🌱  •  Switch to Advanced')
        self.advanced_label.setVisible(self.advanced)
        # Position editing is a core pose tool, not an advanced-only feature.
        # Keep X/Y editable after placing or restoring a saved pose.
        self.x.setEnabled(True);self.y.setEnabled(True)
    def drag_part(self,dx,dy):
        if not 0<=self.selected<len(self.model.parts):return
        if not self._slimer_protect_staged_source('dragging'):return
        p=self.model.parts[self.selected]
        self.remember()
        self.model.move_with_children(self.selected,dx,dy)
        self.select_asset(self.selected);self.refresh()
    def resize_drag(self,dx,dy):
        if (self.canvas.asset_controls_enabled and self.canvas.asset_handle_mode == 'resize'
                and not self.canvas.slimer_active):
            self.slimer_scale.setValue(max(10, min(800, self.slimer_scale.value() + dx + dy)))
            return
        if not 0<=self.selected<len(self.model.parts):return
        if not self._slimer_protect_staged_source('resizing'):return
        p=self.model.parts[self.selected];self.remember()
        width=max(1,p['image'].width+dx);height=max(1,p['image'].height+dy)
        if self.lock.isChecked():
            ow,oh=self.model.originals[self.selected].size
            height=max(1,round(width*oh/ow))
        self.model.resize_part(self.selected,width,height)
        self.select_asset(self.selected);self.refresh()
    @staticmethod
    def _slimer_cursor():
        """Small pixel-art slime pointer with a precise top-left hotspot."""
        from PySide6.QtCore import QPoint
        art=QPixmap(24,24);art.fill(Qt.GlobalColor.transparent)
        painter=QPainter(art)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor('#183d31'));painter.drawRect(2,2,12,12)
        painter.setBrush(QColor('#8ee66c'));painter.drawRect(4,4,8,8)
        painter.setBrush(QColor('#e8fff0'));painter.drawRect(5,6,2,2);painter.drawRect(9,6,2,2)
        painter.setBrush(QColor('#183d31'));painter.drawRect(6,10,4,1)
        painter.setPen(QPen(QColor('#f5fff0'),1));painter.drawLine(0,0,0,3);painter.drawLine(0,0,3,0)
        painter.end()
        return QCursor(art,0,0)

    def slimer_switch_phase(self, name):
        if self.slimer_selection is None:
            return
        previous=getattr(self,'_slimer_current_phase',None)
        if previous:
            self.slimer_phase_masks[previous]=self.slimer_selection.mask.copy()
            self.slimer_phase_transforms[previous]=(self.slimer_dx.value(), self.slimer_dy.value(), self.slimer_turn.value(), self.slimer_scale.value())
            self.slimer_phase_histories[previous]=(self.slimer_selection_undo, self.slimer_selection_redo)
        self._slimer_current_phase=name
        # Transform handles belong to the previous color tab. Keep tab masks
        # and numeric values, but do not carry an active drag into another tab.
        if hasattr(self, 'canvas'):
            self.canvas.slimer_transform_mode=False
            self.canvas.slimer_bounds=None
            self.canvas._slimer_handle=None
            self.canvas._slimer_painting=False
            self.canvas._slimer_last=None
        self._slimer_mouse_transforming=False
        if hasattr(self, 'slimer_drag_toggle'):
            with blocked_signals(self.slimer_drag_toggle):
                self.slimer_drag_toggle.setChecked(False)
            self.slimer_drag_toggle.setText('Drag selected pixels (Shift=resize, Alt=rotate)')
        self.slimer_selection.mask=self.slimer_phase_masks.get(name,Image.new('L',self.model.size,0)).copy()
        values=self.slimer_phase_transforms.get(name,(0,0,0,100))
        for spin,value in zip((self.slimer_dx,self.slimer_dy,self.slimer_turn,self.slimer_scale),values):
            with blocked_signals(spin):
                spin.setValue(value)
        self.slimer_selection_undo, self.slimer_selection_redo = self.slimer_phase_histories.get(name, ([], []))
        self._slimer_sync_numeric_values()
        self._update_slimer_color_button()
        self.refresh()

    def _update_slimer_color_button(self):
        color=self.slimer_phase_colors.get(self.slimer_phase_picker.currentText(),'#54e88a')
        self.slimer_color_button.setStyleSheet(f'QPushButton {{ border: 2px solid {color}; }}')
        self.slimer_color_button.setToolTip(f'Current Slimer highlight color: {color}. Selection tint is editor-only.')

    def slimer_choose_color(self):
        name=self.slimer_phase_picker.currentText()
        color=QColorDialog.getColor(QColor(self.slimer_phase_colors[name]),self,'Slimer highlight color')
        if color.isValid():
            self.slimer_phase_colors[name]=color.name()
            self._update_slimer_color_button()
            self.refresh()

    def slimer_add_phase(self):
        name,ok=QInputDialog.getText(self,'New animation phase','Phase name:')
        name=name.strip()
        if not ok or not name or name in self.slimer_phase_colors:return
        self.slimer_phase_colors[name]='#ffd166'
        self.slimer_phase_picker.addItem(name)
        self.slimer_phase_picker.setCurrentText(name)

    def cleaner_toggle_mode(self,enabled):
        self.canvas.cleaner_active=enabled
        if enabled and self.slimer_toggle.isChecked():
            self.slimer_toggle.setChecked(False)
        self.canvas.setCursor(Qt.CursorShape.CrossCursor if enabled else Qt.CursorShape.ArrowCursor)
        self.status.setText('Slime Cleaner: left-drag to erase pixels; Undo restores a stroke.' if enabled else 'Slime Cleaner off.')
        self.refresh()

    def cleaner_start_stroke(self):
        self.remember()  # One undo snapshot for the complete brush stroke.

    def cleaner_paint(self,x,y):
        from shws_wizard.studio.slime_cleaner import erase_visible_pixels
        modified=set()
        changed=erase_visible_pixels(
            self.model.parts,x,y,self.cleaner_brush.value(),
            states=self._cleaner_resolved_states(),canvas_size=self.model.size,
            modified_indices=modified)
        if changed:
            # Only changed sources are rewritten. The inactive source layers
            # of other poses retain their exact RGBA snapshots.
            for index in modified:
                self.model.originals[index]=self.model.parts[index]['image'].copy()
            self.mark_pose_draft()
            if self.model.animations.get(self.anim.currentText()):
                self._next_pose_capture_pending=True
        self.refresh()

    def _cleaner_resolved_states(self):
        """Keep Slime Cleaner aligned with renderer rotation/parent attachments."""
        states=self.model.resolved_pose()
        for i, state in enumerate(states):
            if i < len(self.model.parts):
                image=self.model.parts[i]['image']
                state['_cleaner_anchor']=tuple(self.model.anchors.get(
                    i, [image.width // 2, image.height // 2]))
        return states

    def adjust_active_brush_size(self,delta):
        """Route +/- to the currently active brush without changing the other tool."""
        if self.cleaner_toggle.isChecked():
            brush = self.cleaner_brush
            label = 'Slime Cleaner'
        elif self.slimer_toggle.isChecked():
            brush = self.slimer_brush
            label = 'Slimer highlight'
        else:
            return
        target = max(brush.minimum(), min(brush.maximum(), brush.value() + delta))
        brush.setValue(target)
        self.status.setText(f'{label} brush size: {target} px (+ / -)')

    def adjust_slimer_brush_size(self,delta):
        """Change highlight size from the keyboard only when Slimer is active."""
        if not self.slimer_toggle.isChecked():
            return
        current=self.slimer_brush.value()
        target=max(self.slimer_brush.minimum(),min(self.slimer_brush.maximum(),current+delta))
        self.slimer_brush.setValue(target)
        self.status.setText(f'Slimer highlight brush size: {target} px (+ / -)')

    def slimer_toggle_mode(self,enabled):
        if enabled and getattr(self,'_slimer_pending_part',None) is None:
            self._show_asset_transform_controls(False)
        if enabled and self.cleaner_toggle.isChecked():
            self.cleaner_toggle.setChecked(False)
        self.canvas.slimer_active=enabled
        self.canvas.setCursor(self._slimer_cursor() if enabled else Qt.CursorShape.ArrowCursor)
        self.canvas.anchor_mode=False if enabled else self.canvas.anchor_mode
        self.slimer_drag_toggle.setEnabled(enabled)
        self.slimer_drag_toggle.setChecked(False)
        self.slimer_drag_toggle.setText('Drag selected pixels (legacy)')
        self.slimer_selection_undo.clear();self.slimer_selection_redo.clear()
        self._slimer_mouse_transforming=False
        self._slimer_sync_numeric_values()
        if enabled:
            self.slimer_selection=SlimerSelection.empty(self.model.render())
            self.slimer_phase_masks={}
            self.slimer_phase_transforms={}
            self.slimer_phase_histories={}
            self._slimer_current_phase=self.slimer_phase_picker.currentText()
        else:
            self.slimer_selection=None
        self.refresh_buddy()
        self.status.setText('Slimer: left-drag to highlight, right-drag to erase highlights. Click Edit Selection to create an editable layer when ready.' if enabled else 'Slimer brush disabled.')
        self.refresh()

    def slimer_finish_selecting(self):
        """Turn highlighted pixels into a movable, uncommitted Slimer selection.

        The floating selection is deliberately not an Asset Library layer until
        Place as Layer is pressed; this keeps cancel/edit safe and undoable.
        """
        if not self.slimer_toggle.isChecked():
            self.status.setText('Activate Slimer, then highlight the pixels you want to move.')
            return
        if self.slimer_selection is None or self.slimer_selection.mask.getbbox() is None:
            self.status.setText('No pixels highlighted. Highlight artwork, then click Edit Selection.')
            return
        self.slimer_drag_toggle.setChecked(True)
        self.refresh()
        self.status.setText('Legacy selection preview ready. Use Edit Selection to create an editable layer.')

    def slimer_drag_mode(self,enabled):
        self.canvas.slimer_transform_mode=enabled
        self.canvas.update()
        self.slimer_drag_toggle.setText('← Highlight Selection (edit)' if enabled else '✓ Move Selection (finish highlighting)')
        self.refresh()
        self.status.setText('Drag to move; hold Shift while dragging to resize, or Alt to rotate.' if enabled else 'Paint with left mouse; erase highlight with right mouse.')

    def _slimer_snapshot(self):
        return (self.slimer_selection.mask.copy(), self.slimer_dx.value(),
                self.slimer_dy.value(), self.slimer_scale.value(), self.slimer_turn.value())

    def _slimer_restore(self, snapshot):
        mask, dx, dy, scale, turn = snapshot
        self.slimer_selection.mask = mask.copy()
        for widget, value in ((self.slimer_dx,dx),(self.slimer_dy,dy),
                              (self.slimer_scale,scale),(self.slimer_turn,turn)):
            was_blocked = widget.blockSignals(True)
            try:
                widget.setValue(value)
            finally:
                widget.blockSignals(was_blocked)
        self._slimer_sync_numeric_values()
        self.refresh()

    def slimer_numeric_changed(self, control, value):
        """Record the previous numeric state before a manual spinner adjustment.

        Mouse-driven transforms already record one snapshot at drag start; avoid
        generating duplicate history entries for their intermediate updates.
        """
        # Once Edit Selection has created a real asset, degree edits must
        # rotate that asset, not an obsolete floating-selection preview.
        if (control is self.slimer_scale and self.canvas.asset_controls_enabled
                and not self.canvas.slimer_active):
            self._resize_active_asset_percent(value)
            self._slimer_numeric_values[control] = self.slimer_scale.value()
            return
        if control is self.slimer_turn and getattr(self, '_slimer_pending_part', None) is not None:
            pending = self._slimer_pending_part
            if 0 <= self.selected < len(self.model.parts) and self.model.parts[self.selected] is pending:
                self.turn_part(value)
                self._slimer_numeric_values[control] = value
            return
        if (self.slimer_selection is not None and not self._slimer_numeric_replaying
                and not getattr(self, '_slimer_mouse_transforming', False)):
            snapshot = list(self._slimer_snapshot())
            slot = {self.slimer_dx: 1, self.slimer_dy: 2,
                    self.slimer_scale: 3, self.slimer_turn: 4}[control]
            # QSpinBox.valueChanged runs after its value has changed. Capture
            # the previous value tracked from the last completed adjustment.
            previous = getattr(self, '_slimer_numeric_values', {}).get(control, value)
            if previous != value:
                snapshot[slot] = previous
                self.slimer_selection_undo.append(tuple(snapshot))
                self.slimer_selection_redo.clear()
        if not hasattr(self, '_slimer_numeric_values'):
            self._slimer_numeric_values = {}
        self._slimer_numeric_values[control] = value
        self.refresh()

    def _slimer_sync_numeric_values(self):
        self._slimer_numeric_values = {spin: spin.value() for spin in
            (self.slimer_dx, self.slimer_dy, self.slimer_scale, self.slimer_turn)}

    def slimer_end_transform(self):
        self._slimer_mouse_transforming=False
        self._slimer_sync_numeric_values()

    def slimer_start_stroke(self):
        if self.slimer_selection is None:return
        # Rebase only an EMPTY highlight. The previous Apply Move, an imported
        # layer, or a regular asset edit may have changed the live artwork.
        # A nonempty selection is deliberately never rebased: doing so would
        # erase the evidence needed for stale-source protection.
        if (getattr(self, '_slimer_pending_part', None) is None
                and self.slimer_selection.mask.getbbox() is None):
            current=self.model.render()
            if (self.slimer_selection.source.size != current.size
                    or self.slimer_selection.source.tobytes() != current.tobytes()):
                self.slimer_selection=SlimerSelection.empty(current)
                self.slimer_selection_undo.clear()
                self.slimer_selection_redo.clear()
        self.slimer_selection_undo.append(self._slimer_snapshot())
        self.slimer_selection_redo.clear()

    def slimer_start_transform(self):
        if self.slimer_selection is None or self.slimer_selection.mask.getbbox() is None:return
        # One mouse gesture is one history entry, even with many move events.
        self.slimer_selection_undo.append(self._slimer_snapshot())
        self.slimer_selection_redo.clear()
        self._slimer_mouse_transforming=True

    def slimer_undo_selection(self):
        if self.slimer_selection is None or not self.slimer_selection_undo:return
        self.slimer_selection_redo.append(self._slimer_snapshot())
        self._slimer_restore(self.slimer_selection_undo.pop())

    def slimer_redo_selection(self):
        if self.slimer_selection is None or not self.slimer_selection_redo:return
        self.slimer_selection_undo.append(self._slimer_snapshot())
        self._slimer_restore(self.slimer_selection_redo.pop())

    def slimer_drag_transform(self,dx,dy,mode):
        if self.slimer_selection is None or self.slimer_selection.mask.getbbox() is None:return
        if mode=='rotate':self.slimer_turn.setValue(self.slimer_turn.value()+dx+dy)
        elif mode=='scale':self.slimer_scale.setValue(self.slimer_scale.value()+dx+dy)
        else:
            self.slimer_dx.setValue(self.slimer_dx.value()+dx)
            self.slimer_dy.setValue(self.slimer_dy.value()+dy)

    def slimer_paint(self,x,y,erase):
        # A staged asset owns the highlighted pixels until Apply Move or Cancel.
        # Painting another highlight before confirmation must not modify the
        # source mask or silently create a second competing selection.
        if getattr(self, '_slimer_pending_part', None) is not None:
            self.status.setText('Apply Move or Cancel Unconfirmed Layer before highlighting another part.')
            return
        if self.slimer_selection is None:return
        if 0<=x<self.model.size[0] and 0<=y<self.model.size[1]:
            self.slimer_selection.paint(x,y,(self.slimer_brush.value()-1)//2,erase)
            self.refresh()

    def slimer_preview(self):
        if self.slimer_selection is None:return Image.new('RGBA',self.model.size)
        bounds=self.slimer_selection.mask.getbbox()
        if bounds is None:return Image.new('RGBA',self.model.size)
        scale=self.slimer_scale.value()/100
        return self.slimer_selection.transform(self.slimer_dx.value(),self.slimer_dy.value(),
            max(1,round((bounds[2]-bounds[0])*scale)),max(1,round((bounds[3]-bounds[1])*scale)),self.slimer_turn.value())

    def slimer_confirm_all_placements(self):
        """Place all nonempty color tabs together as one independent layer.

        Preserve each tab's transform and original-pixel mask. A single
        placement uses one history snapshot, rather than committing tabs in
        sequence and accidentally resampling already-edited artwork.
        """
        from PIL import ImageChops
        if self.slimer_selection is None:
            self.status.setText('Activate Slimer and highlight pixels first.')
            return
        active = self.slimer_phase_picker.currentText()
        self.slimer_phase_masks[active] = self.slimer_selection.mask.copy()
        self.slimer_phase_transforms[active] = (self.slimer_dx.value(), self.slimer_dy.value(),
                                                self.slimer_turn.value(), self.slimer_scale.value())
        layers = []
        union = Image.new('L', self.model.size, 0)
        # Use the current unmodified source for every phase, not the result
        # of an earlier phase's placement.
        source = self.model.render().copy()
        for name in self.slimer_phase_colors:
            mask = self.slimer_phase_masks.get(name)
            if mask is None or mask.getbbox() is None:
                continue
            dx, dy, turn, scale = self.slimer_phase_transforms.get(name, (0, 0, 0, 100))
            selection = SlimerSelection(source.copy(), mask.copy())
            bounds = mask.getbbox()
            transformed = selection.transform(dx, dy,
                max(1, round((bounds[2]-bounds[0]) * scale / 100)),
                max(1, round((bounds[3]-bounds[1]) * scale / 100)), turn)
            layers.append(transformed)
            union = ImageChops.lighter(union, mask)
        if not layers:
            self.status.setText('Highlight pixels in at least one color tab first.')
            return
        if self.slimer_move_original.isChecked() and not self._slimer_original_erase_safe(union):
            self.status.setText('Move Original is unavailable for rotated or resized layers. Use Copy Pixels instead.')
            return
        self.remember()
        if self.slimer_move_original.isChecked():
            self._slimer_erase_original_layers(union)
        # Preserve actual RGBA alpha when combining color tabs. Binary-mask
        # paste would turn translucent selected pixels fully opaque.
        combined = composite_selection_layers(layers, self.model.size)
        existing = {part.get('name', '') for part in self.model.parts}
        number = 1
        while f'Slimer Layer {number:03d}' in existing:
            number += 1
        self.model.import_part(f'Slimer Layer {number:03d}', combined)
        self.assets.addItem(self.model.parts[-1]['name'])
        self.assets.setCurrentRow(len(self.model.parts)-1)
        self.sync_slimer_asset_labels()
        self.slimer_clear()
        self.status.setText(f'Confirmed {len(layers)} color selections as one layer. Undo reverses the whole placement.')
        self.refresh()

    def slimer_clear(self):
        if getattr(self, '_slimer_pending_layer', None) is not None:
            self.status.setText('Apply Move before clearing the staged editable layer.')
            return
        if hasattr(self, '_show_asset_transform_controls'):
            self._show_asset_transform_controls(False)
        # Clearing a finished selection must also discard its floating handles.
        # Otherwise a later highlight can inherit stale transform-mode UI.
        self.canvas.slimer_transform_mode = False
        self.canvas.slimer_bounds = None
        self.canvas._slimer_handle = None
        self.canvas._slimer_painting = False
        self.canvas._slimer_last = None
        # A completed drag must not leave a stale mouse gesture or staged
        # destination bound to the canvas after returning to highlighting.
        self.canvas._action = None
        self.canvas._last = None
        self.canvas.slimer_staged_part = getattr(self, '_slimer_pending_part', None)
        with blocked_signals(self.slimer_drag_toggle):
            self.slimer_drag_toggle.setChecked(False)
        if self.slimer_selection is not None:self.slimer_selection=SlimerSelection.empty(self.model.render())
        self.slimer_phase_masks={}
        self.slimer_phase_transforms={}
        self.slimer_phase_histories={}
        self._slimer_current_phase=self.slimer_phase_picker.currentText()
        self.slimer_selection_undo.clear();self.slimer_selection_redo.clear()
        for spin,value in ((self.slimer_dx,0),(self.slimer_dy,0),(self.slimer_turn,0),(self.slimer_scale,100)):
            with blocked_signals(spin):
                spin.setValue(value)
        self._slimer_sync_numeric_values()
        # Return to highlighting after Apply Move, Cancel, or Clear Selection.
        # This is automatic; there is no second mode-switch button to click.
        if hasattr(self, 'slimer_toggle'):
            self.canvas.slimer_active=self.slimer_toggle.isChecked()
            if hasattr(self.canvas, 'setCursor'):
                self.canvas.setCursor(self._slimer_cursor() if self.canvas.slimer_active else Qt.CursorShape.ArrowCursor)
        self.refresh()

    def _slimer_transformed_erase_plan(self, mask):
        """Return a safe single-layer source erase plan, or None.

        Multiple visible layers and pose-specific source buffers remain excluded.
        The selection must cover every rendered occurrence of each source pixel.
        """
        from shws_wizard.studio.pixel_source_mapping import (rendered_source_indices,
            plan_complete_source_erase)
        states = self.model.resolved_pose()
        visible = [i for i, state in enumerate(states) if state.get('visible', True)]
        if len(visible) != 1:
            return None
        i = visible[0]
        state = states[i]
        part = self.model.parts[i]
        if i >= len(self.model.originals):
            return None
        source = self.model.originals[i]
        # A saved pose normally has source_png. Its decoded source must match
        # the active working buffer before a destructive erase is authorized.
        if state.get('source_png'):
            pose_source = self.model._decode_source(state['source_png'])
            if pose_source.size != source.size or pose_source.tobytes() != source.tobytes():
                return None
        w = max(1, int(state.get('width', source.width)))
        h = max(1, int(state.get('height', source.height)))
        # A scaled part is NOT byte-identical to its source. Check the actual
        # nearest-neighbor rendered buffer instead of rejecting every resize.
        expected = source.resize((w, h), Image.Resampling.NEAREST)
        if state.get('source_png') and (part['image'].size != expected.size
                or part['image'].tobytes() != expected.tobytes()):
            return None
        mapping = rendered_source_indices(source.size, self.model.size,
            int(state['x']), int(state['y']), w, h,
            float(state.get('angle', 0)), self.model.anchors.get(i, [w // 2, h // 2]))
        alpha = self.model.render_part(i, state).getchannel('A')
        plan = plan_complete_source_erase(mapping, alpha, mask)
        if plan is None:
            return None
        # Reject any selected visible pixels that have no mapped source.
        for label, a, selected in zip(mapping.get_flattened_data(),
                                     alpha.get_flattened_data(),
                                     mask.get_flattened_data()):
            if selected and a and label <= 0:
                return None
        return i, plan

    def _slimer_layered_erase_plan(self, mask):
        """Plan a lossless multi-layer Move Original before changing any source.

        Each selected source pixel must have all visible occurrences selected.
        Fractional-alpha selected pixels may move only when no other layer
        contributes at those coordinates; otherwise a flattened selection
        cannot represent the underlying artwork without destroying it.
        """
        from shws_wizard.studio.pixel_source_mapping import (rendered_source_indices,
            classify_contributing_source_selection)
        from PIL import ImageChops
        states = self.model.resolved_pose()
        layers, source_ids = [], []
        # Only assets that contribute to the highlighted pixels need source
        # provenance checks. An unrelated asset may have a pose-local source
        # snapshot that differs from its cached buffer; it must not prevent a
        # safe move of pixels on another asset.
        selected = mask.convert('L').point(lambda a: 255 if a else 0)
        # Determine ownership from the TOP of the stack. An obscured lower
        # layer must not veto a move just because its cached source is stale.
        # Preserve bottom-to-top order for the provenance classifier below.
        remaining = selected.copy()
        contributors = set()
        selected_owners = {}
        rendered_alphas = {}
        for i in range(len(states) - 1, -1, -1):
            state = states[i]
            if not state.get('visible', True):
                continue
            alpha = self.model.render_part(i, state).getchannel('A')
            rendered_alphas[i] = alpha
            covered = ImageChops.darker(remaining, alpha.point(lambda a: 255 if a else 0))
            if covered.getbbox() is not None:
                contributors.add(i)
                selected_owners[i] = covered
                remaining = ImageChops.subtract(remaining, covered)
            if remaining.getbbox() is None:
                break
        if remaining.getbbox() is not None:
            return None
        for i, state in enumerate(states):
            # Include every visible layer in ownership classification, even
            # when it contributes no selected pixels. Otherwise an unselected
            # occluder disappears from the classifier and can make a lower
            # scaled source look partially selected when it is fully covered.
            if not state.get('visible', True):
                continue
            alpha = rendered_alphas.get(i)
            if alpha is None:
                alpha = self.model.render_part(i, state).getchannel('A')
            if i >= len(self.model.originals):
                return None
            source = self.model.originals[i]
            if i not in contributors:
                w, h = int(state['width']), int(state['height'])
                mapping = rendered_source_indices(source.size, self.model.size,
                    int(state['x']), int(state['y']), w, h,
                    float(state.get('angle', 0)), self.model.anchors.get(i, [w // 2, h // 2]))
                layers.append((mapping, alpha))
                source_ids.append(i)
                continue
            if state.get('source_png'):
                saved = self.model._decode_source(state['source_png'])
                if saved.size != source.size or saved.tobytes() != source.tobytes():
                    return None
            w, h = int(state['width']), int(state['height'])
            expected = source.resize((w, h), Image.Resampling.NEAREST)
            actual = self.model.parts[i]['image']
            if actual.size != expected.size or actual.tobytes() != expected.tobytes():
                return None
            # A selected semitransparent pixel may be moved intact when it
            # sits over *transparent* pixels of every lower asset. Render()
            # then contains exactly the top source RGBA and its alpha is
            # preserved by the staged layer. Do NOT permit fractional-alpha
            # compositing over artwork: the selection would contain a merged
            # color, and erasing either source could damage the other layer.
            # Opaque top pixels remain safe even when they cover lower art.
            selected_alpha = ImageChops.darker(alpha, selected_owners[i])
            fractional = selected_alpha.point(lambda a: 255 if 0 < a < 255 else 0)
            if fractional.getbbox() is not None:
                for beneath in range(i):
                    if not states[beneath].get('visible', True):
                        continue
                    lower_alpha = rendered_alphas.get(beneath)
                    if lower_alpha is None:
                        lower_alpha = self.model.render_part(beneath, states[beneath]).getchannel('A')
                        rendered_alphas[beneath] = lower_alpha
                    if ImageChops.darker(fractional, lower_alpha).getbbox() is not None:
                        return None
            mapping = rendered_source_indices(source.size, self.model.size,
                int(state['x']), int(state['y']), w, h,
                float(state.get('angle', 0)), self.model.anchors.get(i, [w // 2, h // 2]))
            layers.append((mapping, alpha))
            source_ids.append(i)
        if not layers:
            return None
        # All highlighted pixels must belong to visible artwork.
        visible = Image.new('L', self.model.size, 0)
        for _, alpha in layers:
            # The selection is a binary visibility mask, not a fractional
            # alpha image. Compare against alpha PRESENCE; using raw alpha
            # incorrectly rejects any selected translucent pixel as missing
            # coverage (255 - alpha > 0), even when it has one safe source.
            visible = ImageChops.lighter(visible, alpha.point(lambda a: 255 if a else 0))
        selected = mask.convert('L').point(lambda a: 255 if a else 0)
        if ImageChops.subtract(selected, visible).getbbox():
            return None
        classified = classify_contributing_source_selection(layers, selected)
        if any(partial for _, partial in classified):
            return None
        plans = [(i, complete) for i, (complete, _) in zip(source_ids, classified)
                 if i in contributors and complete]
        return plans if plans else None

    def _slimer_original_erase_safe(self, mask=None):
        """Only erase when canvas pixels map 1:1 to editable source pixels.

        Inspect resolved transforms, not merely local angles: an attached child
        can inherit rotation or movement from a parent without a local angle.
        """
        states = self.model.resolved_pose()
        if mask is not None and getattr(self, '_slimer_layered_erase_plan', lambda _mask: None)(mask) is not None:
            return True
        if mask is not None and getattr(self, '_slimer_transformed_erase_plan', lambda _mask: None)(mask) is not None:
            return True
        # Preflight only the topmost pixels that the erase routine will
        # actually consume. An occluded lower layer must not reject a safe
        # move from the visible top layer (or get erased itself).
        from PIL import ImageChops
        remaining = (mask.convert('L').point(lambda a: 255 if a else 0)
                     if mask is not None else None)
        for i in range(len(states) - 1, -1, -1):
            state = states[i]
            if not state.get('visible', True):
                continue
            if remaining is not None:
                rendered_alpha = self.model.render_part(i, state).getchannel('A')
                consumed = ImageChops.darker(remaining,
                    rendered_alpha.point(lambda a: 255 if a else 0))
                if consumed.getbbox() is None:
                    continue
                # Fallback erasure removes whole source pixels. A selected
                # translucent pixel cannot be treated as opaque provenance:
                # doing so would silently discard its fractional alpha.
                selected_alpha = ImageChops.darker(rendered_alpha, consumed)
                if any(a not in (0, 255) for a in selected_alpha.get_flattened_data()):
                    return False
                remaining = ImageChops.subtract(remaining, consumed)
            if float(state.get('angle', 0)) % 360:
                return False
            # Pure inherited translation is an exact 1:1 pixel mapping.
            # The erase routine uses resolved canvas coordinates below.
            part = self.model.parts[i]
            if i >= len(self.model.originals):
                return False
            source = self.model.originals[i]
            if state.get('source_png'):
                source = self.model._decode_source(state['source_png'])
            # The dedicated Slimer overlay is a pose-local editable source.
            # apply_pose() restores its original buffer but can leave the live
            # part image pointing at the previous pose. This is safe to edit
            # only when the resolved source and originals agree exactly.
            if (part.get('name') == 'Slimer pose overlay'
                    and int(state.get('x', 0)) == 0
                    and int(state.get('y', 0)) == 0
                    and source.size == tuple(self.model.size)
                    and source.size == self.model.originals[i].size
                    and source.tobytes() == self.model.originals[i].tobytes()
                    and (int(state.get('width', source.width)),
                         int(state.get('height', source.height))) == source.size):
                continue
            # Erasing edits part['image'] and originals. If this pose renders a
            # different saved source, those buffers do not describe its pixels.
            # Refuse the destructive move until pose-aware source editing exists.
            # The erase routine mutates both the live part and originals.
            # Both must match the exact source used by the renderer; otherwise
            # a pose-local source could conceal edits or erase another pose.
            if (source.size != part['image'].size
                    or source.tobytes() != part['image'].tobytes()
                    or source.size != self.model.originals[i].size
                    or source.tobytes() != self.model.originals[i].tobytes()):
                return False
            if (int(state.get('width', source.width)),
                    int(state.get('height', source.height))) != source.size:
                return False
        # Every highlighted pixel must be accounted for by a visible,
        # editable source. Otherwise a partial erase could be committed while
        # the user reasonably expects the whole selection to have moved.
        if remaining is not None and remaining.getbbox() is not None:
            return False
        return True

    def _slimer_erase_original_layers(self, mask):
        """Clear selected rendered pixels from their topmost contributing layer.

        Clearing every visible layer would destroy hidden/underlying artwork
        when multiple source layers overlap at the same canvas coordinate.
        """
        staged = getattr(self, '_slimer_pending_part', None)
        staged_visible = staged.get('visible', True) if staged is not None else None
        if staged is not None:
            # Exclude the provisional destination from source ownership,
            # including overlapping source/destination footprints.
            staged['visible'] = False
        try:
            from PIL import ImageChops
            layered = getattr(self, '_slimer_layered_erase_plan', lambda _mask: None)(mask)
            if layered is not None:
                from shws_wizard.studio.pixel_source_mapping import erase_planned_source_pixels
                # Compute every new source before committing any change.
                replacements = [(i, erase_planned_source_pixels(self.model.originals[i], indices))
                                for i, indices in layered]
                for i, image in replacements:
                    self.model.originals[i] = image.copy()
                    width, height = self.model.parts[i]['image'].size
                    self.model.parts[i]['image'] = image.resize((width, height), Image.Resampling.NEAREST)
                return
            plan = getattr(self, '_slimer_transformed_erase_plan', lambda _mask: None)(mask)
            if plan is not None:
                from shws_wizard.studio.pixel_source_mapping import erase_planned_source_pixels
                i, indices = plan
                image = erase_planned_source_pixels(self.model.originals[i], indices)
                # Preserve the live part's nearest-neighbor display dimensions.
                # Replacing a scaled buffer with the native source image changes
                # its geometry and can break the next Slimer selection.
                width, height = self.model.parts[i]['image'].size
                self.model.parts[i]['image'] = image.resize((width, height), Image.Resampling.NEAREST)
                self.model.originals[i] = image.copy()
                return
            remaining = mask.convert('L').point(lambda a: 255 if a else 0)
            states = self.model.resolved_pose()
            for i in range(len(self.model.parts) - 1, -1, -1):
                part = self.model.parts[i]
                if not states[i].get('visible', True) or remaining.getbbox() is None:
                    continue
                # Do not erase pixels from an asset that did not actually
                # contribute to the selected canvas coordinates. In particular,
                # its unrotated local rectangle may overlap a selection even
                # though its rendered, rotated pixels do not.
                if hasattr(self.model, 'render_part'):
                    rendered_alpha = self.model.render_part(i, states[i]).getchannel('A')
                    if ImageChops.darker(remaining, rendered_alpha).getbbox() is None:
                        continue
                state = states[i]
                # A restored saved pose may have a different overlay image than
                # the cached part buffer. Edit the currently rendered pose source,
                # never the image left over from another frame.
                if part.get('name') == 'Slimer pose overlay' and state.get('source_png'):
                    image = self.model._decode_source(state['source_png']).convert('RGBA').copy()
                else:
                    image = part['image'].convert('RGBA').copy()
                x, y = int(state['x']), int(state['y'])
                local = remaining.crop((x, y, x + image.width, y + image.height))
                # Only pixels actually present in this layer can consume the mask.
                present = image.getchannel('A').point(lambda a: 255 if a else 0)
                consumed = ImageChops.darker(local, present)
                if consumed.getbbox() is None:
                    continue
                image.putalpha(ImageChops.subtract(image.getchannel('A'), consumed))
                part['image'] = image
                if i < len(self.model.originals):
                    self.model.originals[i] = image.copy()
                canvas_consumed = Image.new('L', self.model.size, 0)
                canvas_consumed.paste(consumed, (x, y))
                remaining = ImageChops.subtract(remaining, canvas_consumed)

        finally:
            if staged is not None:
                staged['visible'] = staged_visible
        # The fallback must never report success after erasing only a subset.
        # Apply Move owns rollback of every source buffer on this failure.
        if remaining.getbbox() is not None:
            raise RuntimeError("Slimer source erase left unmapped selected pixels")

    @staticmethod
    def _slimer_visible_selection_mask(mask, rendered):
        """Restrict a brush selection to artwork, not transparent canvas.

        The Slimer brush can cross empty pixels while outlining a limb or
        accessory. Those pixels are not editable sources and must not veto an
        otherwise safe Move Original operation.
        """
        from PIL import ImageChops
        if mask.size != rendered.size:
            raise ValueError('Slimer selection and canvas dimensions differ')
        selected = mask.convert('L').point(lambda a: 255 if a else 0)
        visible = rendered.getchannel('A').point(lambda a: 255 if a else 0)
        return ImageChops.darker(selected, visible)

    def _new_asset_scale_baseline(self):
        """Keep one immutable source for this editing session, avoiding quality loss."""
        if not 0 <= self.selected < len(self.model.parts):
            return None
        index = self.selected
        part = self.model.parts[index]
        source = self.model.originals[index].copy()
        slimer_canvas = (part.get('name', '').startswith('Slimer Layer ')
                         and source.size == tuple(self.model.size)
                         and part['image'].size == tuple(self.model.size))
        default_pivot = [source.width // 2, source.height // 2]
        self._asset_scale_baseline = {
            'part': part, 'source': source,
            'display_size': part['image'].size,
            'pivot': tuple(self.model.anchors.get(index, default_pivot)),
            'slimer_canvas': slimer_canvas, 'percent': 100,
        }
        if hasattr(self, 'slimer_scale'):
            with blocked_signals(self.slimer_scale):
                self.slimer_scale.setValue(100)
            self._slimer_sync_numeric_values()
        return self._asset_scale_baseline

    def _resize_active_asset_percent(self, percent):
        """Resize the selected real Asset Library layer (not the old float preview)."""
        if not (self.canvas.asset_controls_enabled and 0 <= self.selected < len(self.model.parts)):
            return False
        part = self.model.parts[self.selected]
        baseline = getattr(self, '_asset_scale_baseline', None)
        if baseline is None or baseline['part'] is not part:
            baseline = self._new_asset_scale_baseline()
        if baseline is None:
            return False
        index = self.selected
        try:
            if baseline['slimer_canvas']:
                from shws_wizard.studio.slimer_asset_scale import scaled_selection_content
                changed = scaled_selection_content(baseline['source'], percent, baseline['pivot'])
            else:
                w = max(1, round(baseline['display_size'][0] * percent / 100))
                h = max(1, round(baseline['display_size'][1] * percent / 100))
                if w > 2048 or h > 2048:
                    raise ValueError('The resized asset would exceed the 2048-pixel limit.')
                changed = baseline['source'].resize((w, h), Image.Resampling.NEAREST)
        except ValueError as exc:
            with blocked_signals(self.slimer_scale):
                self.slimer_scale.setValue(baseline.get('percent', 100))
            self.status.setText(str(exc) + ' Artwork unchanged.')
            return False
        if (part['image'].size == changed.size and part['image'].tobytes() == changed.tobytes()):
            baseline['percent'] = percent
            return True
        self.remember()
        if baseline['slimer_canvas']:
            # Keep the 128x128 Slimer source geometry stable while resizing
            # its opaque/translucent selected CONTENT around the real pivot.
            self.model.originals[index] = changed.copy()
        part['image'] = changed.copy()
        baseline['percent'] = percent
        self.mark_pose_draft()
        self.refresh()
        self.status.setText(f'Resized {part.get("name", "asset")} to {percent}% of its edit-start size. Apply Move confirms placement.')
        return True

    def _show_asset_transform_controls(self, enabled):
        """One-button toggle; controls always belong to the selected library row."""
        self.canvas.asset_controls_enabled = bool(enabled)
        if enabled:
            self._new_asset_scale_baseline()
        else:
            self._asset_scale_baseline = None
        self.slimer_edit_asset.setText('✓ Edit Selection • Hide Handles' if enabled
                                       else 'Edit Selection • Create / Show Handles')
        # Bright green cue only while the actual Edit Selection handles are
        # enabled.  Clearing, applying, canceling, switching poses/projects,
        # and rejected edits all use this same mode source of truth.
        self.slimer_edit_asset.setProperty('editingActive', bool(enabled))
        self.slimer_edit_asset.setStyleSheet(
            'QPushButton { background-color: #548c35; border: 2px solid #c8ff87; '
            'color: #ffffff; font-weight: bold; } '
            'QPushButton:hover { background-color: #619d40; border-color: #e5ffbb; }'
            if enabled else '')
        self._refresh_active_layer_label()
        self.canvas.sync_canvas_handle_layers(self.model.parts, self.selected,
                                              getattr(self, '_slimer_pending_part', None) is not None)
        self.canvas.update()

    def _refresh_active_layer_label(self):
        if not 0 <= self.selected < len(self.model.parts):
            self.active_asset_label.setText('Selected layer: None • Handles OFF')
            return
        item = self.assets.item(self.selected)
        name = item.text() if item is not None else self.model.parts[self.selected].get('name', 'Asset')
        mode = {'move_x': 'X', 'move_y': 'Y', 'rotate': 'R', 'resize': 'S'}[self.canvas.asset_handle_mode]
        state = 'Handles ON: ' + mode if self.canvas.asset_controls_enabled else 'Handles OFF'
        self.active_asset_label.setText(f'Selected layer: {name} • {state}')

    def _slimer_selection_safety_details(self, mask, rendered):
        """Compact non-destructive diagnostics for refused Move Original.

        Count actual *selected* canvas pixels rather than making assumptions
        about the sprite's alpha or the user's brush size.  This is only used
        on rejection, so it does not add rendering work to successful edits.
        """
        from PIL import ImageChops
        bbox = mask.getbbox()
        if bbox is None:
            return 'selected=0, translucent=0, multi-layer=0'
        selected = mask.crop(bbox).convert('L').tobytes()
        composite_alpha = rendered.getchannel('A').crop(bbox).tobytes()
        total = sum(bool(mark and a) for mark, a in zip(selected, composite_alpha))
        translucent = sum(bool(mark and 0 < a < 255)
                          for mark, a in zip(selected, composite_alpha))
        # Count pixels whose layer provenance is ambiguous because more than
        # one visible source has nonzero coverage. Opaque top-over-bottom is
        # sometimes safe, so this is a diagnostic count, not a permission rule.
        counts = bytearray(len(selected))
        for i, state in enumerate(self.model.resolved_pose()):
            if not state.get('visible', True):
                continue
            alpha = self.model.render_part(i, state).getchannel('A').crop(bbox).tobytes()
            for j, (mark, a) in enumerate(zip(selected, alpha)):
                if mark and a and counts[j] < 2:
                    counts[j] += 1
        multi = sum(v > 1 for v in counts)
        return f'selected={total}, translucent={translucent}, multi-layer={multi}'

    def slimer_create_editable_layer(self):
        """One Edit button: stage highlighted pixels or show/hide selected handles.

        Keep the actual source/pixel transaction in this method so its safety
        checks remain the same in the UI and in the Qt-free model harness.
        """
        pending = getattr(self, '_slimer_pending_part', None)
        if pending is not None:
            if not any(p is pending for p in self.model.parts):
                self.status.setText('Staged layer no longer exists. Cancel and select again.')
                return False
            if hasattr(self, '_show_asset_transform_controls'):
                self._show_asset_transform_controls(not self.canvas.asset_controls_enabled)
                self.status.setText('Staged layer handles ' +
                                    ('shown.' if self.canvas.asset_controls_enabled else 'hidden.') +
                                    ' Apply Move still commits the original source-pixel mode.')
                return True
            self.status.setText('Apply Move or Cancel before creating another layer.')
            return False
        selection = self.slimer_selection
        if selection is None or selection.mask.getbbox() is None:
            # The same button serves two distinct, unambiguous cases:
            # a painted highlight stages NEW pixels; an empty highlight with a
            # selected, visible library asset edits THAT existing asset. This
            # is particularly important immediately after Import Asset, when
            # Slimer may still be active but no pixels have been highlighted.
            # Never manufacture a duplicate asset or a pending source erase.
            chosen=(self.model.parts[self.selected]
                    if 0 <= self.selected < len(self.model.parts) else None)
            has_art=(chosen is not None and chosen.get('visible', True)
                     and chosen['image'].convert('RGBA').getchannel('A').getbbox() is not None)
            if has_art and hasattr(self, '_show_asset_transform_controls'):
                if self.canvas.asset_controls_enabled:
                    # Hiding handles also returns to the brush, otherwise a
                    # second highlight would appear to be stuck after editing.
                    self.slimer_clear()
                    self.status.setText('Layer handles hidden. Slimer is ready to highlight another area.')
                else:
                    self.canvas.slimer_active=False
                    self.canvas.slimer_transform_mode=False
                    self.canvas.slimer_bounds=None
                    self._show_asset_transform_controls(True)
                    self.canvas.setCursor(Qt.CursorShape.ArrowCursor)
                    self.refresh()
                    self.status.setText('Editing existing layer: ' + chosen.get('name', 'Asset') +
                                        '. Use X, Y, Rotate or Resize; Apply Move finishes placement without adding a frame.')
                return True
            if (getattr(self.canvas, 'slimer_active', False)
                    and hasattr(self, 'slimer_toggle')
                    and self.slimer_toggle.isChecked()):
                self.status.setText('Nothing highlighted yet. Highlight visible artwork, or select a nonempty Asset Library layer to edit its placement.')
                return False
            self.status.setText('Highlight visible artwork or select an Asset Library layer before Edit Selection.')
            return False
        # Genuine highlighted pixels: keep the existing guarded creation,
        # source-snapshot validation and Apply Move contract below unchanged.
        if self._slimer_pending_layer is not None:
            self.status.setText('Apply Move to confirm the current layer before creating another.')
            return False
        selection=self.slimer_selection
        if selection is None or selection.mask.getbbox() is None:
            self.status.setText('Highlight pixels before clicking Edit Selection.')
            return False
        # Render once for both the selection's source-integrity check and
        # extraction. A second full compositing pass is expensive on large
        # canvases and can observe a different state if a renderer is dynamic.
        source=self.model.render().convert('RGBA')
        if selection.source.convert('RGBA').tobytes()!=source.tobytes():
            self.status.setText('Selection source changed; clear and highlight again.')
            return False
        # Brush strokes often include transparent background. Only visible
        # artwork can become a layer or be erased from a source asset.
        effective_mask=self._slimer_visible_selection_mask(selection.mask, source)
        if effective_mask.getbbox() is None:
            self.status.setText('No visible pixels in this selection. Highlight artwork before Edit Selection.')
            return False
        if self.slimer_move_original.isChecked() and not self._slimer_original_erase_safe(effective_mask):
            details = self._slimer_selection_safety_details(effective_mask, source)
            self.status.setText('Move Original source safety blocked (' + details +
                                '). No pixels changed. This can indicate overlapping layers, partial scaled-pixel selection, or a stale source buffer. You can Clear Selection and edit the entire Asset Library layer, or choose Copy Pixels. Send us the counts if a clearly isolated region is rejected.')
            return False
        # The provisional asset is genuine and editable using the regular asset
        # controls. Do not erase source pixels until Apply Move is confirmed.
        from PIL import ImageChops
        isolated=source.copy()
        isolated.putalpha(ImageChops.multiply(source.getchannel('A'), effective_mask))
        existing={part.get('name','') for part in self.model.parts}
        number=1
        while f'Slimer Layer {number:03d}' in existing:
            number+=1
        # A highlighted region may be entirely transparent. Refuse to create
        # an invisible asset: it cannot be meaningfully moved or confirmed.
        if isolated.getchannel('A').getbbox() is None:
            self.status.setText('No visible pixels in this selection. Highlight artwork before Edit Selection.')
            return False
        # Remember the user's source-layer selection. Once Apply Move finishes,
        # restore it so the next Slimer stroke starts in the familiar source
        # context instead of leaving the new destination row active.
        self._slimer_previous_selected_part = (self.model.parts[self.selected]
            if 0 <= getattr(self, 'selected', -1) < len(self.model.parts) else None)
        self.remember()
        self.model.import_part(f'Slimer Layer {number:03d}',isolated)
        index=len(self.model.parts)-1
        # A Slimer asset is stored as a full-canvas transparent PNG, but its
        # rotation pivot belongs to the selected pixels, not the canvas center.
        # Keep the full-canvas storage layout for backwards compatibility.
        left, top, right, bottom = isolated.getchannel('A').getbbox()
        if hasattr(self.model, 'set_anchor'):
            self.model.set_anchor(index, (left + right) // 2, (top + bottom) // 2)
        self.assets.addItem(self.model.parts[index]['name'])
        self._slimer_pending_layer=index
        self._slimer_pending_part=self.model.parts[index]
        self._slimer_pending_source=source.copy()
        self._slimer_pending_mask=effective_mask.copy()
        self._slimer_pending_move_original=self.slimer_move_original.isChecked()
        # Keep the erase/copy policy stable for the lifetime of this staged layer.
        # Otherwise changing the checkbox could make the UI disagree with Apply Move.
        self.slimer_move_original.setEnabled(False)
        self.assets.setCurrentRow(index)
        # The preview-only degree spinner must now refer to the selected real
        # layer. Its initial angle is zero, regardless of previous selections.
        if hasattr(self, 'slimer_turn'):
            with blocked_signals(self.slimer_turn):
                self.slimer_turn.setValue(0)
            self._slimer_sync_numeric_values()
        # Edit Selection is the ONE transition from painting to editing. The
        # staged object is now the selected real Asset Library layer. Temporarily
        # give normal canvas mouse dragging to that asset, not to the highlight
        # brush or old floating-selection handles. Apply/Cancel restores brush.
        self.canvas.slimer_transform_mode=False
        self.canvas.slimer_active=False
        if hasattr(self, '_show_asset_transform_controls'):
            self._show_asset_transform_controls(True)
        if hasattr(self.canvas, 'setCursor'):
            self.canvas.setCursor(Qt.CursorShape.ArrowCursor)
        self.refresh()
        self.status.setText('Layer ready. Choose X, Y, Rotate, or Resize from the collapsible menu on the canvas; Apply Move confirms safely.')
        return True

    def _slimer_restore_source_row(self):
        """Return focus to the source asset after a finished Slimer transaction.

        Resolve by object identity, never an outdated row index. This changes
        selection only, not source images or the animation timeline.
        """
        source = getattr(self, '_slimer_previous_selected_part', None)
        self._slimer_previous_selected_part = None
        if source is None:
            return
        index = next((i for i, candidate in enumerate(self.model.parts)
                      if candidate is source), None)
        if index is not None and hasattr(self.assets, 'setCurrentRow'):
            self.assets.setCurrentRow(index)

    def slimer_cancel_editable_layer(self):
        """Discard an unconfirmed Edit Selection layer without erasing source pixels.

        The provisional part is tracked by identity because asset-list rows may
        change while the user edits. Never remove a different part by stale index.
        """
        pending = getattr(self, '_slimer_pending_part', None)
        if pending is None:
            self.status.setText('No unconfirmed Slimer layer to cancel.')
            return False
        index = next((i for i, part in enumerate(self.model.parts)
                      if part is pending), None)
        if index is None:
            # A deleted staged asset must not strand Slimer in a permanently
            # locked state. No source pixels were erased by Edit Selection.
            self._slimer_pending_layer = None
            self._slimer_pending_part = None
            self._slimer_pending_source = None
            self._slimer_pending_mask = None
            self._slimer_pending_move_original = None
            self.slimer_move_original.setEnabled(True)
            if hasattr(self, '_slimer_restore_source_row'):
                self._slimer_restore_source_row()
            self.slimer_clear()
            self.status.setText('Missing staged layer discarded; original artwork preserved.')
            return False
        # A provisional layer is appended to the asset library. If other
        # assets have since been appended, refuse destructive index shifts.
        if index != len(self.model.parts) - 1:
            self.status.setText('Cannot cancel: another asset follows the staged layer. Artwork unchanged.')
            return False
        self.remember()
        self.model.remove_unconfirmed_part(index)
        self.assets.takeItem(index)
        self._slimer_pending_layer = None
        self._slimer_pending_part = None
        self._slimer_pending_source = None
        self._slimer_pending_mask = None
        self._slimer_pending_move_original = None
        self.slimer_move_original.setEnabled(True)
        if hasattr(self, '_slimer_restore_source_row'):
            self._slimer_restore_source_row()
        self.slimer_clear()
        self.mark_pose_draft()
        self.refresh()
        self.status.setText('Unconfirmed Slimer layer cancelled; original artwork preserved.')
        return True

    def slimer_apply_move_to_pose(self):
        """Confirm a staged editable layer without adding a pose/frame."""
        index=self._slimer_pending_layer
        # The asset list can be reordered while a provisional layer is being
        # edited. Resolve by object identity rather than applying to a stale
        # numeric row (which could otherwise confirm a different asset).
        pending_part=getattr(self, '_slimer_pending_part', None)
        # An integer row alone is not proof of a live staged transaction.
        # Undo, project reload, or asset removal can reuse the same row for a
        # different asset. Require the exact staged object before committing.
        if pending_part is None:
            # Imported and previously confirmed assets are already real
            # independent layers. Applying their placement ends handle-edit
            # mode; it must NOT run the Move Original source-erase transaction.
            if (self.canvas.asset_controls_enabled
                    and 0 <= self.selected < len(self.model.parts)
                    and self.model.parts[self.selected].get('visible', True)):
                name=self.model.parts[self.selected].get('name', 'Asset')
                self.slimer_clear()
                self.mark_pose_draft()
                self.refresh()
                if hasattr(self, 'anim'):
                    self._next_pose_capture_pending=bool(self.model.animations.get(self.anim.currentText()))
                self.status.setText('Placement confirmed for ' + name +
                                    '. Handles hidden; ready for another selection. No frame created.')
                return True
            self.status.setText('No verified staged Slimer layer. Highlight pixels and click Edit Selection first.')
            return False
        # A restored/invalid transaction must never reach source comparison or
        # erasure with a missing snapshot.  Keep the layer editable for recovery.
        source_snapshot = getattr(self, '_slimer_pending_source', None)
        source_mask = getattr(self, '_slimer_pending_mask', None)
        if (source_snapshot is None or source_mask is None
                or source_snapshot.size != self.model.size
                or source_mask.size != self.model.size
                or source_mask.getbbox() is None
                or getattr(self, '_slimer_pending_move_original', None) not in (True, False)):
            self.status.setText('Staged Slimer source snapshot is missing or invalid. Cancel and select again; artwork unchanged.')
            return False
        index=next((i for i, candidate in enumerate(self.model.parts)
                    if candidate is pending_part), None)
        if index is None:
            if pending_part is not None:
                # Undo or deletion removed the staged asset. Release the
                # pending transaction instead of leaving Apply Move locked.
                self.slimer_cancel_editable_layer()
            else:
                self.status.setText('Highlight pixels and click Edit Selection to create an editable layer first.')
            return False
        if not 0 <= index < len(self.model.parts):
            self.status.setText('The staged layer is no longer available. Clear the selection and try again.')
            return False
        # The source-erasure policy belongs to the selection that created this
        # provisional layer. Do not silently change it mid-operation.
        if self.slimer_move_original.isChecked() != self._slimer_pending_move_original:
            self.status.setText('Move/Copy mode changed after Edit Selection. Restore the original mode before Apply Move.')
            return False
        part=self.model.parts[index]
        # Validate the actual editable asset's destination BEFORE erasing any
        # source pixels. A layer dragged entirely off-canvas must not make its
        # source disappear on a seemingly successful Apply Move.
        if not part.get('visible', True):
            self.status.setText('Staged layer is hidden. Show it before Apply Move; artwork unchanged.')
            return False
        # Check the *unclipped* transformed artwork, including rotations.
        # render_part clips to the canvas before returning and therefore
        # cannot tell whether a partially visible move lost source pixels.
        if self._slimer_pending_move_original and part.get('visible', True):
            from shws_wizard.studio.slimer_destination import destination_fits_canvas
            resolved_destination = (self.model.resolved_pose()[index]
                                    if hasattr(self.model, 'resolved_pose')
                                    else dict(x=part['x'], y=part['y'],
                                              angle=self.model.angles.get(index, 0)))
            angle = resolved_destination.get('angle', 0)
            anchor = getattr(self.model, 'anchors', {}).get(index, [part['image'].width // 2,
                                                     part['image'].height // 2])
            if not destination_fits_canvas(part['image'], resolved_destination['x'], resolved_destination['y'],
                                           angle, anchor, self.model.size):
                self.status.setText('Part of the moved artwork is outside the canvas. Move it fully inside before Apply Move; original pixels preserved.')
                return False
        destination = self.model.render_part(index, self.model.resolved_pose()[index])
        if destination.getchannel('A').getbbox() is None:
            self.status.setText('Staged layer is outside the canvas or empty. Move it back before Apply Move; artwork unchanged.')
            return False
        visible=part.get('visible',True)
        part['visible']=False
        try:
            # Preflight with the provisional destination excluded. Never save
            # undo history while the destination is temporarily hidden.
            source_unchanged=(self.model.render().tobytes()
                              == self._slimer_pending_source.tobytes())
            erase_safe=(not self._slimer_pending_move_original or
                        self._slimer_original_erase_safe(self._slimer_pending_mask)) if source_unchanged else False
        finally:
            part['visible']=visible
        if not source_unchanged:
            self.status.setText('Underlying artwork changed during selection. Move not applied.')
            return False
        if not erase_safe:
            self.status.setText('Cannot safely erase selected source pixels. Move not applied.')
            return False
        # Record the true visible state of every asset, including the staged
        # destination. Preserve the undo/redo stacks: a failed source erase
        # is not an edit and must not create a phantom Undo entry or clear Redo.
        history_past = self.history.past[:]
        history_future = self.history.future[:]
        previous_draft_dirty = self._pose_draft_dirty
        previous_draft_key = self._pose_draft_key
        self.remember()
        # A source-erase failure must never leave half-erased artwork behind.
        # Keep the staged destination and selection available for correction.
        if self._slimer_pending_move_original:
            source_images = [part['image'].copy() for part in self.model.parts]
            source_originals = [image.copy() for image in self.model.originals]
            try:
                self._slimer_erase_original_layers(self._slimer_pending_mask)
            except Exception as error:
                for source_part, image in zip(self.model.parts, source_images):
                    source_part['image'] = image
                self.model.originals[:] = source_originals
                self.history.past[:] = history_past
                self.history.future[:] = history_future
                self._pose_draft_dirty = previous_draft_dirty
                self._pose_draft_key = previous_draft_key
                self.status.setText('Source erase failed; original pixels restored. Move not applied. Cause: ' + str(error)[:180])
                self.refresh()
                return False
        self._slimer_pending_layer=None
        self._slimer_pending_part=None
        self._slimer_pending_source=None
        self._slimer_pending_mask=None
        self._slimer_pending_move_original=None
        self.slimer_move_original.setEnabled(True)
        if hasattr(self, '_slimer_restore_source_row'):
            self._slimer_restore_source_row()
        self.slimer_clear()
        self.mark_pose_draft()
        self.refresh()
        # An approved Slimer movement is a proposed NEXT pose, not
        # permission for recovery autosave to overwrite the current pose.
        if hasattr(self, 'anim'):
            self._next_pose_capture_pending=bool(self.model.animations.get(self.anim.currentText()))
        self.status.setText('Move applied on the working canvas. Place Frame saves the result as a NEW pose and keeps the earlier saved pose unchanged. Use Save Current Pose only to replace the selected pose.')
        return True

    def _slimer_commit(self,as_frame,into_pose=False):
        selection=self.slimer_selection
        if selection is None or selection.mask.getbbox() is None:
            self.status.setText('Highlight some pixels with the Slimer brush first.');return False
        # A selection can outlive a pose switch or an intervening source edit.
        # Never erase pixels based on a stale snapshot: that could delete
        # unrelated artwork, even if the transform itself looks correct.
        if selection.source.size != self.model.render().size or selection.source.tobytes() != self.model.render().tobytes():
            self.status.setText('Move NOT applied; frame NOT placed. Selection source is stale. Clear the highlight and select pixels again from the current pose. Artwork unchanged.')
            return False
        # Validate before touching the timeline. A rejected Move Original must
        # not save a dirty draft or alter the current frame's recovery state.
        if self.slimer_move_original.isChecked() and not self._slimer_original_erase_safe(selection.mask):
            self.status.setText('Move NOT applied; frame NOT placed. Cannot safely map every selected pixel to its editable source. Try a smaller selection, or switch to Copy Pixels. Nothing was changed.')
            return False
        # A transform entirely outside the canvas must never erase the source.
        # Validate the destination before recording history or changing pixels.
        # This also prevents an apparently successful Apply Move that makes the
        # selected artwork disappear instead of leaving it ready for re-editing.
        result = self.slimer_preview()
        if result is None or result.getchannel('A').getbbox() is None:
            self.status.setText('Move NOT applied; frame NOT placed. The selected pixels would land outside the canvas. Adjust the position and try again; artwork unchanged.')
            return False
        # Commit the current pose BEFORE adding a new part. Otherwise an active
        # draft can accidentally save the new Slimer layer into the previous pose.
        if as_frame:
            self.preserve_pose_draft()
        self.remember()  # A complete placement, including new layer/frame, is ONE undo step.
        # The destination preview was validated before any mutation.
        if self.slimer_move_original.isChecked():
            # Clear only the active working pose; the previous timeline pose was
            # snapshotted above before this destructive part of the operation.
            self._slimer_erase_original_layers(selection.mask)
        if as_frame or into_pose:
            # Reuse the dedicated Slimer overlay layer instead of appending a
            # second/third/etc. "Slimer pose" asset on every Place Frame click.
            # Pose snapshots contain their own source_png, so changing this
            # layer's source for the NEW frame cannot rewrite an older frame.
            overlay_index=next((i for i,p in enumerate(self.model.parts)
                if p.get('name') == 'Slimer pose overlay'), None)
            if overlay_index is None:
                self.model.import_part('Slimer pose overlay', result)
                overlay_index=len(self.model.parts)-1
                self.assets.addItem(self.model.parts[-1]['name'])
            else:
                from PIL import Image
                # An overlay hidden by apply_pose() belongs to another pose.
                # Never resurrect its cached pixels in the current frame.
                if self.model.parts[overlay_index].get('visible', True):
                    old_layer=self.model.originals[overlay_index].convert('RGBA').copy()
                else:
                    old_layer=Image.new('RGBA', self.model.size)
                if old_layer.size != tuple(self.model.size):
                    old_layer=old_layer.resize(self.model.size,Image.Resampling.NEAREST)
                # The selected pixels are placed on the existing transparent
                # overlay; previous selections in this pose remain visible.
                # Pixel-art placements must be idempotent. Alpha-compositing a
                # semi-transparent selected pixel repeatedly increases opacity
                # and can corrupt the exact RGBA value. Replace only pixels
                # actually selected, preserving their original alpha.
                placed=result.convert('RGBA')
                selection_mask=placed.getchannel('A').point(lambda a: 255 if a else 0)
                merged=old_layer.copy()
                merged.paste(placed,(0,0),selection_mask)  # binary mask copies exact RGBA
                self.model.originals[overlay_index]=merged.copy()
                self.model.parts[overlay_index]['image']=merged.copy()
                self.model.parts[overlay_index]['x']=0
                self.model.parts[overlay_index]['y']=0
                self.model.parts[overlay_index]['visible']=True
                self.model.angles[overlay_index]=0
            self.assets.setCurrentRow(overlay_index)
        else:
            # Every explicit Place as Layer creates a separate, uniquely named asset.
            existing={part.get('name', '') for part in self.model.parts}
            number=1
            while f'Slimer Layer {number:03d}' in existing:
                number+=1
            self.model.import_part(f'Slimer Layer {number:03d}',result)
            self.assets.addItem(self.model.parts[-1]['name'])
            self.assets.setCurrentRow(len(self.model.parts)-1)
        if as_frame:
            name=self.anim.currentText()
            # The previous frame is already finalized. The new part exists only
            # in the new frame snapshot, not in the older pose's saved state.
            index=self.model.insert_frame(name,self.frame+1)
            self._pose_draft_dirty=False
            self.select_timeline_pose(index)
        self.sync_slimer_asset_labels()
        self.slimer_clear()
        self.status.setText('Slimer placement complete: originals moved.' if self.slimer_move_original.isChecked() else 'Slimer placement complete: originals copied.')
        self.refresh()
        return True

    def slimer_place_layer(self):
        return self._slimer_commit(False)
    @staticmethod
    def _pose_needs_slimer_merge(states):
        """Flatten only Slimer-authored poses, leaving ordinary rig posing intact.

        An already-combined layer counts as a Slimer source so successive new
        poses start from clean artwork even when the latest pose has no newly
        staged Slimer cuts.
        """
        return any(state.get('visible', True) and (
            state.get('name', '').startswith('Slimer Layer ')
            or state.get('name') == 'Slimer pose overlay'
            or state.get('name', '').startswith('Combined Artwork '))
            for state in states)

    def _insert_next_working_pose(self, animation, index, source_pose):
        """Insert one independent pose; Slimer-built sources get one new base.

        The previous saved pose is not flattened.  Only the newly-created
        snapshot gets a composite asset and hides its inherited source layers.
        This is one Undo transaction at the call site, not an animation frame
        created by Apply Move or Edit Selection.
        """
        if self._slimer_pending_layer is not None:
            self.status.setText('Apply Move or Cancel before creating another pose. Artwork unchanged.')
            return None
        if self._pose_needs_slimer_merge(source_pose):
            actual_index = min(max(int(index), 0), len(self.model.animations.get(animation, [])))
            pose = self.model.merged_working_pose(
                source_pose, f'Combined Artwork {len(self.model.parts) + 1:03d}')
            self.assets.addItem(self.model.parts[-1]['name'])
            index = self.model.insert_frame(animation, actual_index, pose)
            # A new model asset is temporarily visible on the live canvas.
            # Never auto-save that transient state onto the previous pose.
            self._pose_draft_key = None
            self._pose_draft_dirty = False
            self.select_timeline_pose(index)
            # Only the merged working art should be selected by default.
            self.assets.setCurrentRow(len(self.model.parts)-1)
            self._reset_slimer_for_project_change()
            return index
        index = self.model.insert_frame(animation, index, source_pose)
        self._pose_draft_key = None
        self._pose_draft_dirty = False
        self.select_timeline_pose(index)
        self._reset_slimer_for_project_change()
        return index

    def slimer_place_frame(self):
        """Create a new pose even when no pixels have been highlighted.

        Place Frame records current live artwork AS THE NEXT POSE.

        Previously it auto-saved the edited canvas into the selected pose
        BEFORE duplicating it. That turned the beginner workflow (place base
        pose, move legs twice, place next frame) into two identical poses.
        The selected saved pose must instead remain unchanged. The separate
        Save Current Pose action is the explicit in-place edit command.
        """
        if not self.model.parts:
            QMessageBox.warning(self,'No artwork','Import creature artwork first.')
            return False
        if self._slimer_pending_layer is not None:
            self.status.setText('Apply Move to confirm the editable layer before placing a frame. Nothing was changed.')
            return False
        # Place Frame is exclusively a timeline operation. Never route it
        # through Slimer's pixel-moving commit path, even when the selection
        # has transform handles or a movement offset. A highlighted selection
        # is not an approved edit and must not erase its original pixels.
        # Capture the live canvas as a NEW frame. Never auto-save it over the
        # already saved selected frame: Apply Move edits the working canvas,
        # and Place Frame is the user's commit-as-next-pose action.
        name = self.anim.currentText()
        if not self._canvas_owns_selected_pose(name):
            return False
        # Snapshot all PREVIOUSLY SAVED frames before creating the next one.
        # Do NOT call preserve_pose_draft() here: that was the actual cause
        # of overwriting the previous pose with the newly edited leg motion.
        # Explicit Save Current Pose still edits an existing frame in-place.
        from copy import deepcopy
        import hashlib
        old_frames = deepcopy(self.model.animations.get(name, []))
        old_ids = self.model._sync_pose_ids(name)[:]
        old_pixels = [hashlib.sha256(self.model.render(pose).tobytes()).hexdigest()
                      for pose in old_frames]
        self.remember()
        source_pose = self.model.snapshot()
        # A Slimer-edited source becomes a combined editable artwork asset in
        # the NEW pose. Older saved snapshots are immutable here, even when
        # the working canvas has two freshly applied leg moves.
        combined = self._pose_needs_slimer_merge(source_pose)
        if combined:
            index = self._insert_next_working_pose(name, self.frame + 1, source_pose)
            if index is None:
                return False
        else:
            index = self.model.insert_frame(name, self.frame + 1, source_pose)
            # No merge must still disconnect the old live draft before the
            # Qt timeline switches ownership to the newly inserted pose.
            self._pose_draft_key = None
            self._pose_draft_dirty = False
            self.select_timeline_pose(index)
        # An independent frame is more than a new timeline row: prove the
        # immutable saved pixels and layer snapshots of EVERY older frame
        # survived the real GUI insertion. A failed check is a bug, not a
        # success notification. Restore saved frames before displaying it.
        current_ids = self.model._sync_pose_ids(name)
        surviving_ids = [pose_id for pose_id in current_ids if pose_id in old_ids]
        saved_by_id = {pid: pose for pid, pose in zip(current_ids, self.model.animations[name])}
        unchanged = (surviving_ids == old_ids and all(
            saved_by_id.get(pid) == before and
            hashlib.sha256(self.model.render(saved_by_id[pid]).tobytes()).hexdigest() == signature
            for pid, before, signature in zip(old_ids, old_frames, old_pixels)
            if pid in saved_by_id))
        unchanged = unchanged and all(pid in saved_by_id for pid in old_ids)
        if not unchanged:
            for pid, previous in zip(old_ids, old_frames):
                if pid in current_ids:
                    self.model.animations[name][current_ids.index(pid)] = deepcopy(previous)
            # Remove the rejected newly inserted pose so a reported failure
            # does not silently leave an extra timeline row behind. The
            # library can retain an inactive asset until Undo/restart.
            if 0 <= index < len(self.model.animations.get(name, [])):
                self.model.delete_frame(name, index)
            self._pose_draft_key = None
            self._pose_live_id = None
            if old_ids:
                self.select_timeline_pose(min(max(index - 1, 0), len(old_ids) - 1))
            self.status.setText('POSE PROTECTION: an earlier saved frame changed during Place Frame. Existing snapshots restored; new frame rejected. Save a separate backup and send the exact message for debugging.')
            self.refresh_timeline()
            return False
        self._next_pose_capture_pending=False
        self.model.unplaced_next_pose = None
        if old_frames:
            prior = old_frames[min(max(index - 1, 0), len(old_frames) - 1)]
            visually_changed = (self.model.render(prior).tobytes()
                                != self.model.render(self.model.animations[name][index]).tobytes())
            self.status.setText(
                f'Pose {index + 1} saved as NEW frame; older {len(old_frames)} pose(s) verified unchanged. '
                + ('Leg/artwork edits belong ONLY to the new pose. '
                   if visually_changed else 'This pose is an identical starting copy; make your next edit. ')
                + 'Use Save Current Pose ONLY to intentionally replace the selected saved pose.'
            )
        else:
            self.status.setText(
                'Pose 1 saved as your starting frame. Move the legs, click Apply Move, '
                'then Place Frame to capture those edits AS Pose 2 without changing Pose 1.'
            )
        self.refresh_timeline()
        return True

    def remember(self):
        self._slimer_redo_transaction = None
        self.history.record(self.model)
        self.mark_pose_draft()

    def _after_history_change(self):
        self.selected=min(self.selected,len(self.model.parts)-1)
        was_blocked = self.assets.blockSignals(True)
        try:
            self.assets.clear()
            self.assets.addItems([p['name'] for p in self.model.parts])
            self.assets.setCurrentRow(self.selected)
        finally:
            self.assets.blockSignals(was_blocked)
        self.refresh_parent_picker()
        self.refresh_timeline()
        self.refresh()

    def _timeline_history_signature(self):
        """Identity/order of saved poses, excluding ordinary pixel edits."""
        return tuple((name, tuple(self.model.pose_id(name, i)
                                  for i in range(len(poses))))
                     for name, poses in sorted(self.model.animations.items()))

    def _history_selection(self):
        """Remember the selected pose by identity, not its shifting row number."""
        animation = self.anim.currentText()
        poses = self.model.animations.get(animation, [])
        pose_id = self.model.pose_id(animation, self.frame) if 0 <= self.frame < len(poses) else None
        return animation, pose_id, self.frame

    def _after_history_restore(self, previous_timeline, selection):
        """Restore history, animation selector, pose canvas and Slimer source together."""
        previous_animation, pose_id, old_index = selection
        animation = self.model.current
        if animation not in self.model.animations:
            animation = (previous_animation if previous_animation in self.model.animations
                         else next(iter(self.model.animations), ''))
        if animation != previous_animation:
            pose_id = None  # IDs from another animation must never select this pose.
            old_index = 0
        # History restores fresh part dictionaries. A pending Slimer layer is
        # tracked by object identity, so its old pointer must never survive a
        # snapshot restore (or Apply Move could target an unrelated asset).
        # Undoing a staged creation therefore releases its pending transaction.
        self._slimer_pending_layer = None
        self._slimer_pending_part = None
        self._slimer_pending_source = None
        self._slimer_pending_mask = None
        self._slimer_pending_move_original = None
        self.slimer_move_original.setEnabled(True)
        # History may replace the entire pixel source. A live Slimer selection
        # refers to pixels from before Undo/Redo and must not survive that swap.
        self._pose_draft_key = None
        self._pose_draft_dirty = False
        self._reset_slimer_for_project_change()
        # Undo/Redo can restore an animation name that did not exist when the
        # selector was last populated. Ensure the entry exists before selecting.
        was_blocked = self.anim.blockSignals(True)
        try:
            if animation and self.anim.findText(animation) < 0:
                self.anim.addItem(animation)
            if self.anim.currentText() != animation:
                self.anim.setCurrentText(animation)
        finally:
            self.anim.blockSignals(was_blocked)
        # A restored history snapshot can point at a removed animation.
        # Keep the model and selector on the same valid fallback before
        # refreshing the timeline or loading any saved pose.
        self.model.current = animation
        self._after_history_change()
        poses = self.model.animations.get(animation, [])
        if not poses:
            self.frame = 0
            self._pose_draft_key = None
        else:
            ids = [self.model.pose_id(animation, i) for i in range(len(poses))]
            index = ids.index(pose_id) if pose_id in ids else min(max(old_index, 0), len(poses) - 1)
            self.select_timeline_pose(index)
        if self._timeline_history_signature() != previous_timeline:
            self._timeline_structure_changed()

    def _capture_pending_slimer_for_redo(self):
        """Keep a transaction token outside model history for the next Redo."""
        part = getattr(self, '_slimer_pending_part', None)
        if part is None:
            return None
        index = next((i for i, item in enumerate(self.model.parts) if item is part), None)
        if index is None:
            return None
        return (index, part.get('name'),
                self._slimer_pending_source.copy(), self._slimer_pending_mask.copy(),
                self._slimer_pending_move_original)

    def _restore_pending_slimer_after_redo(self, token):
        """Rebind only if the restored layer still has its original source underneath."""
        if token is None:
            return False
        index, name, source, mask, move_original = token
        if index != len(self.model.parts) - 1 or self.model.parts[index].get('name') != name:
            return False
        part = self.model.parts[index]
        visible = part.get('visible', True)
        part['visible'] = False
        try:
            matches = self.model.render().convert('RGBA').tobytes() == source.tobytes()
        finally:
            part['visible'] = visible
        if not matches:
            return False
        self._slimer_pending_layer = index
        self._slimer_pending_part = part
        self._slimer_pending_source = source.copy()
        self._slimer_pending_mask = mask.copy()
        self._slimer_pending_move_original = move_original
        self.slimer_move_original.setChecked(bool(move_original))
        self.slimer_move_original.setEnabled(False)
        return True

    def undo(self):
        if (getattr(self, '_slimer_pending_part', None) is None
                and self.slimer_toggle.isChecked() and self.slimer_selection_undo):
            self.slimer_undo_selection();self.status.setText("Undid Slimer selection or transform.");return
        previous_timeline = self._timeline_history_signature()
        selection = self._history_selection()
        token = self._capture_pending_slimer_for_redo()
        if self.history.undo(self.model):
            self._pose_draft_dirty=False
            self._after_history_restore(previous_timeline, selection)
            self._slimer_redo_transaction = token
            self.status.setText('Undid the last edit. Redo restores it.')

    def redo(self):
        if (getattr(self, '_slimer_pending_part', None) is None
                and self.slimer_toggle.isChecked() and self.slimer_selection_redo):
            self.slimer_redo_selection();self.status.setText("Restored Slimer selection or transform.");return
        previous_timeline = self._timeline_history_signature()
        selection = self._history_selection()
        token = getattr(self, '_slimer_redo_transaction', None)
        self._slimer_redo_transaction = None
        if self.history.redo(self.model):
            self._pose_draft_dirty=False
            self._after_history_restore(previous_timeline, selection)
            if self._restore_pending_slimer_after_redo(token):
                self.status.setText('Restored unfinished Slimer layer. Apply Move or cancel it.')
            else:
                self.status.setText('Restored the edit.')

    def _set_asset_visibility_in_current_pose(self, visible):
        """Non-destructive per-pose removal; never reindex shared rig assets."""
        index=self.selected
        name=self.anim.currentText()
        poses=self.model.animations.get(name,[])
        if not 0 <= index < len(self.model.parts):
            self.status.setText('Select an asset in the Asset Library first.')
            return
        if getattr(self, '_slimer_pending_part', None) is not None:
            self.status.setText('Apply Move or cancel the staged Slimer layer before changing pose visibility.')
            return
        if not 0 <= self.frame < len(poses):
            self.status.setText('Select a saved pose before changing its assets.')
            return
        if not self._canvas_owns_selected_pose(name):
            return
        self.remember()
        self.model.parts[index]['visible']=visible
        self.model.save_pose_at(name,self.frame)
        self._pose_draft_key=self._saved_pose_key(name,self.frame)
        self._pose_draft_dirty=False
        self.refresh_timeline()
        self.sync_slimer_asset_labels()
        self.refresh()
        self.status.setText(('Restored' if visible else 'Removed') + ' asset in this pose only. Ctrl+Z to undo.')

    def remove_asset_from_current_pose(self):
        self._set_asset_visibility_in_current_pose(False)

    def restore_asset_in_current_pose(self):
        self._set_asset_visibility_in_current_pose(True)

    def move_layer(self,direction):
        if getattr(self, '_slimer_pending_part', None) is not None:
            self.status.setText('Apply Move or cancel the staged Slimer layer before reordering assets.')
            return
        i=self.selected
        if i<0 or not 0<=i+direction<len(self.model.parts):return
        self.remember()
        if self.model.reorder_part(i,direction):
            self.assets.clear();self.assets.addItems([p['name'] for p in self.model.parts])
            self.assets.setCurrentRow(i+direction);self.refresh_parent_picker();self.refresh()
    def refresh_parent_picker(self):
        if not hasattr(self,'parent_picker'):return
        current=self.parent_picker.currentData()
        was_blocked = self.parent_picker.blockSignals(True)
        try:
            self.parent_picker.clear()
            for i,part in enumerate(self.model.parts):
                if i != self.selected:
                    self.parent_picker.addItem(part['name'], i)
            pos = self.parent_picker.findData(current)
            if pos >= 0:
                self.parent_picker.setCurrentIndex(pos)
        finally:
            self.parent_picker.blockSignals(was_blocked)

    def connect_part(self):
        parent=self.parent_picker.currentData()
        if self.selected<0 or parent is None:
            self.status.setText('First select a part, then choose what it connects to.');return
        try:
            self.remember();self.model.attach(self.selected,parent)
            self.status.setText(f"Connected {self.model.parts[self.selected]['name']} to {self.model.parts[parent]['name']}! Move the parent to try it.")
        except ValueError as e:QMessageBox.information(self,'Connection tip',str(e))

    def disconnect_part(self):
        if self.selected<0:return
        self.remember();self.model.detach(self.selected)
        self.status.setText('Part unlinked. You can move it independently.')

    def export_asset_for_shs(self):
        """Export a real selected-layer PNG, suitable for opening in SHS.

        An imported source with unchanged size/rotation keeps its native PNG
        dimensions. A Slimer-generated full-canvas layer or any transformed
        asset exports the *visible selected artwork* with transparent margins
        trimmed, rather than an apparently blank full-canvas source PNG.
        The frame, other assets, UI handles and highlight overlays are excluded.
        """
        if getattr(self, '_slimer_pending_part', None) is not None:
            self.status.setText('Apply Move or Cancel the unfinished Slimer layer before exporting an asset.')
            return False
        index=self.selected
        if not 0 <= index < len(self.model.parts):
            self.status.setText('Select an Asset Library layer before exporting to SHS.')
            return False
        part=self.model.parts[index]
        if not part.get('visible', True):
            self.status.setText('This layer is hidden in the current pose. Restore it before exporting.')
            return False
        try:
            state=self.model.resolved_pose()[index]
            # Render the selected layer only, using the same pose-local source,
            # geometry and rotation the actual canvas displays.
            rendered=self.model.render_part(index, state).convert('RGBA')
            occupied=rendered.getchannel('A').getbbox()
            if occupied is None:
                self.status.setText('Selected layer has no visible pixels on the canvas. Nothing exported.')
                return False
            source=(self.model._decode_source(state['source_png'])
                    if state.get('source_png') else self.model.originals[index]).convert('RGBA')
            if source.getchannel('A').getbbox() is None:
                self.status.setText('Selected layer has no source pixels to export. Nothing exported.')
                return False
            # Small imported PNGs retain their intentional native padding.
            # Full-canvas Slimer layers are trimmed to the selected pixels;
            # rotated/resized assets export their actual visible result.
            keep_native=(source.size != tuple(self.model.size)
                         and source.size == (int(state.get('width', source.width)),
                                             int(state.get('height', source.height)))
                         and float(state.get('angle', 0)) % 360 == 0)
            image=source.copy() if keep_native else rendered.crop(occupied)
        except Exception as error:
            self.status.setText('Could not prepare asset for SHS: ' + str(error)[:180])
            return False
        raw_name=part.get('name','asset')
        safe_name=''.join(ch if ch.isalnum() or ch in ' _-.' else '_' for ch in raw_name).strip(' .') or 'asset'
        initial=str(Path.home()/(safe_name + '.png'))
        dest,_=QFileDialog.getSaveFileName(self,'Export Asset PNG for SHS',initial,'PNG image (*.png)')
        if not dest:
            return False
        target=Path(dest)
        if target.suffix.lower() != '.png':
            target=target.with_suffix('.png')
        # Don't leave an empty/truncated file if disk write or validation fails.
        import tempfile
        temporary=None
        try:
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.'+target.stem+'_',
                                             suffix='.png', delete=False) as output:
                temporary=Path(output.name)
            image.save(temporary, format='PNG')
            with Image.open(temporary) as verify:
                verify.load()
                if (verify.format != 'PNG' or verify.size != image.size
                        or verify.convert('RGBA').getchannel('A').getbbox() is None
                        or verify.convert('RGBA').tobytes() != image.tobytes()):
                    raise ValueError('Exported file did not contain valid visible PNG pixels.')
            temporary.replace(target)
        except Exception as error:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            self.status.setText('Asset export failed; original file left unchanged. Cause: ' + str(error)[:180])
            return False
        self.status.setText(f'Exported {raw_name}: {image.width} x {image.height} PNG to {target}. Open this file in SHS.')
        return True

    def import_assets(self):
        # An uncommitted Slimer destination must remain the last asset.
        # Appending an import would invalidate Cancel and the source lock.
        if getattr(self, '_slimer_pending_part', None) is not None:
            self.status.setText('Apply Move or Cancel the unfinished Slimer layer before importing another asset.')
            return False
        paths,_=QFileDialog.getOpenFileNames(self,'Import creature assets','','PNG (*.png)')
        for path in paths:
            try:
                im=Image.open(path).convert('RGBA')
                cw,ch=self.model.size
                if im.width>cw or im.height>ch:
                    answer=QMessageBox.question(self,'Large PNG asset',f'{Path(path).name} is {im.width} × {im.height} pixels, larger than the {cw} × {ch} canvas.\n\nFit inside canvas without cropping? (No keeps original size.)',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Yes)
                    if answer==QMessageBox.StandardButton.Cancel:continue
                    if answer==QMessageBox.StandardButton.Yes:
                        im.thumbnail((cw,ch),Image.Resampling.NEAREST)
                self.remember();self.model.import_part(Path(path).stem,im)
                self.assets.addItem(Path(path).stem)
            except Exception as e:QMessageBox.warning(self,'Import failed',str(e))
        if paths:self.refresh_parent_picker()
        if paths:self.assets.setCurrentRow(len(self.model.parts)-1)
        # Importing while Slimer is in highlight mode changes the rendered
        # source. Reset its empty/old selection snapshot automatically so
        # Edit Selection doesn't get stuck with stale source provenance.
        if paths and getattr(self, 'slimer_selection', None) is not None:
            self.slimer_clear()
            self.status.setText('Asset imported. Slimer highlight refreshed for the new artwork.')
        self.refresh()
        return bool(paths)
    def _canvas_model_pixel_hit(self,index,x,y):
        """Match the exact per-layer RGBA render, including rotations/rig pose.

        Hit-testing is read-only and does not create undo entries, change pose
        ownership, or perform any Slimer source erase.
        """
        xi,yi=int(x),int(y)
        width,height=self.model.size
        if not (0 <= index < len(self.model.parts) and
                0 <= xi < width and 0 <= yi < height):
            return False
        state=self.model.resolved_pose()[index]
        return self.model.render_part(index,state).getpixel((xi,yi))[3] > 0

    def select_asset(self,i):
        pending=getattr(self,'_slimer_pending_part',None)
        if pending is not None:
            live_index=next((j for j,p in enumerate(self.model.parts) if p is pending),None)
            if live_index is not None and i != live_index:
                # Moving another asset during an uncommitted Move Original
                # could make its source snapshot unsafe. Keep the identity clear.
                with blocked_signals(self.assets):
                    self.assets.setCurrentRow(live_index)
                self.status.setText('Apply Move or Cancel the staged layer before editing a different Asset Library layer.')
                i=live_index
        self.selected=i
        self.canvas.selected=i
        if (getattr(self.canvas, 'asset_controls_enabled', False)
                and pending is None and 0 <= i < len(self.model.parts)):
            # Layer picker changes are a new edit session; 100% now means
            # this newly chosen layer's current dimensions, not the last one's.
            self._new_asset_scale_baseline()
        self.canvas.sync_canvas_handle_layers(self.model.parts, i,
                                              pending is not None)
        self._refresh_active_layer_label()
        if i<0 or i>=len(self.model.parts):
            self.canvas.update()
            return
        p=self.model.parts[i]
        self.canvas.update()
        self.refresh_parent_picker()
        self._refresh_pose_asset_controls()
        for spin,val in ((self.x,p['x']),(self.y,p['y']),(self.w,p['image'].width),(self.h,p['image'].height)):
            was_blocked = spin.blockSignals(True)
            try:
                spin.setValue(val)
            finally:
                spin.blockSignals(was_blocked)
        was_blocked = self.angle.blockSignals(True)
        try:
            self.angle.setValue(round(self.model.angles.get(i,0)))
        finally:
            self.angle.blockSignals(was_blocked)
    def update_asset(self):
        if not 0 <= self.selected < len(self.model.parts):
            return
        # A staged Slimer destination is the only asset editable until Apply.
        pending = getattr(self, '_slimer_pending_part', None)
        if pending is not None and self.model.parts[self.selected] is not pending:
            self.select_asset(self.selected)
            self.status.setText('Apply Move or cancel the staged Slimer layer before editing another asset.')
            return
        p = self.model.parts[self.selected]
        x, y = self.x.value(), self.y.value()
        w, h = self.w.value(), self.h.value()
        if self.lock.isChecked():
            ow, oh = self.model.originals[self.selected].size
            sender = self.sender()
            if sender is self.w:
                h = max(1, round(w * oh / ow))
                with blocked_signals(self.h):
                    self.h.setValue(h)
            elif sender is self.h:
                w = max(1, round(h * ow / oh))
                with blocked_signals(self.w):
                    self.w.setValue(w)
        old_geometry = (p['x'], p['y'], p['image'].width, p['image'].height)
        new_geometry = (x, y, w, h)
        if new_geometry == old_geometry:
            return
        # Snapshot the final geometry once. In particular, X/Y-only edits
        # must not resample the entire layer image on each spinbox change.
        self.remember()
        p['x'], p['y'] = x, y
        if (w, h) != old_geometry[2:]:
            self.model.resize_part(self.selected, w, h)
        self.refresh()
    def _selected_or_tip(self):
        if 0 <= self.selected < len(self.model.parts):
            return True
        self.status.setText('🌱 Choose a PNG part in the Asset Library first, then try that tool.')
        return False

    def _slimer_protect_staged_source(self, operation):
        """Block non-table transforms of a different asset during staging.

        Editing the staged destination is allowed; editing the frozen source
        would make the eventual Move Original preflight stale.
        """
        pending = getattr(self, '_slimer_pending_part', None)
        if (pending is not None and 0 <= self.selected < len(self.model.parts)
                and self.model.parts[self.selected] is not pending):
            self.status.setText(
                f'Apply Move or cancel the staged Slimer layer before {operation} another asset.')
            return False
        return True

    def flip_selected(self, axis):
        if not self._selected_or_tip():return
        if not self._slimer_protect_staged_source('flipping'):return
        self.remember();self.model.flip_part(self.selected,axis)
        self.select_asset(self.selected);self.refresh()
        self.status.setText('Flipped the selected part. Press Ctrl+Z to undo.')

    def center_selected(self, axis):
        if not self._selected_or_tip():return
        if not self._slimer_protect_staged_source('centering'):return
        self.remember();self.model.center_part(self.selected,axis)
        self.select_asset(self.selected);self.refresh()
        self.status.setText('Centered the selected part. Press Ctrl+Z to undo.')

    def reset_size(self):
        if not self._selected_or_tip():return
        if not self._slimer_protect_staged_source('resizing'):return
        self.remember();self.model.reset_part_size(self.selected)
        self.select_asset(self.selected);self.refresh()
        self.status.setText('Restored the original PNG size. Press Ctrl+Z to undo.')

    def _saved_pose_key(self, animation, index):
        """Bind a canvas draft to a stable pose identity, not just its row.

        A timeline insertion, drag or deletion can change row numbers while the
        artwork on the canvas still belongs to its original pose. A numeric
        index alone is not permission to overwrite a saved frame.
        """
        return (self._active_project_id, animation, index,
                self.model.pose_id(animation, index))

    def _apply_saved_pose(self, animation, index):
        """Load one saved frame and remember which frame owns live pixels."""
        pose = self.model.animations[animation][index]
        self.model.apply_pose(pose)
        self._pose_live_id = self.model.pose_id(animation, index)

    def _canvas_owns_selected_pose(self, animation):
        """Fail closed if the UI row and the live canvas are different poses.

        A new unsaved creature has no pose owner yet; Place Frame may create
        its first pose. After that, a timeline selection must load that saved
        pose before Place Frame, Save Current Pose or per-pose visibility edits.
        """
        frames = self.model.animations.get(animation, [])
        if not frames:
            return True
        if not 0 <= self.frame < len(frames):
            self.status.setText('Select a valid saved pose before editing the timeline.')
            return False
        # The Qt-selected thumbnail is the user's visible editing target.
        # An out-of-sync row must not silently write another pose, even if
        # the internal live-canvas/draft IDs still happen to match each other.
        if hasattr(self, 'timeline') and self.timeline.currentRow() != self.frame:
            self.status.setText('Pose mismatch: the highlighted timeline row differs from the editing canvas. Click the intended pose thumbnail again before Place Frame.')
            return False
        owner = self._saved_pose_key(animation, self.frame)
        if self._pose_draft_key != owner or self._pose_live_id != owner[3]:
            self.status.setText('Frame change blocked: the live canvas belongs to a different pose. Select the timeline pose to reload its pixels.')
            return False
        return True

    def preserve_pose_draft(self):
        """Save a draft only back into its own *identity-verified* pose.

        Never write live artwork into another pose when the timeline selection
        changed, a frame was inserted, or a drop reordered row numbers.
        """
        if getattr(self, '_next_pose_capture_pending', False):
            # The canvas holds an unsaved NEXT pose. Automatic recovery, tab
            # switches, and other housekeeping must not turn this into an
            # implicit Save Current Pose over the previous saved frame.
            return
        key = self._pose_draft_key
        if key is None:
            return
        if len(key) != 4:
            # Unknown/legacy draft ownership is not safe for an auto-save.
            self.status.setText('Pose not auto-saved: its owning frame cannot be verified. Select the pose again.')
            return
        project_id, animation, old_index, pose_id = key
        if project_id != self._active_project_id:
            return
        poses = self.model.animations.get(animation, [])
        ids = self.model._sync_pose_ids(animation)
        if pose_id not in ids or self._pose_live_id != pose_id:
            # Failing closed here is crucial: do not write the next frame's
            # pixels into a previous frame simply because it occupies row N.
            self.status.setText('Pose not auto-saved: active canvas identity does not match this saved pose. Artwork left untouched.')
            return
        index = ids.index(pose_id)
        pending_slimer = (self._slimer_pending_layer is not None or bool(
            getattr(self.canvas, 'slimer_transform_mode', False)
            and self.slimer_selection is not None
            and self.slimer_selection.mask.getbbox() is not None))
        if pending_slimer:return
        if self._pose_draft_dirty or self.model.snapshot() != poses[index]:
            self.model.save_pose_at(animation, index)
        self._pose_draft_key = (project_id, animation, index, pose_id)
        self._pose_draft_dirty = False

    def mark_pose_draft(self):
        if self._loading_pose:
            return
        key = self._pose_draft_key
        if (key and len(key) == 4 and key[0] == self._active_project_id
                and self._pose_live_id == key[3]
                and key[3] in self.model._sync_pose_ids(key[1])):
            self._pose_draft_dirty = True

    def begin_pose_draft(self, animation, index):
        self.preserve_pose_draft()
        self._pose_draft_key = self._saved_pose_key(animation, index)
        self._pose_draft_dirty = False

    def change_anim(self,name):
        if (getattr(self, '_next_pose_capture_pending', False)
                and name != self.model.current):
            old=self.anim.blockSignals(True)
            try:self.anim.setCurrentText(self.model.current)
            finally:self.anim.blockSignals(old)
            self.status.setText('Finish your next-pose edits with Place Frame or Save Current Pose before switching animations.')
            return
        # Switching animations starts the new preview at its first pose.
        # Rebase the clock so elapsed time from the old animation cannot
        # advance the new one on the next timer tick.
        self.restart_playback()
        previous_animation=self.model.current
        self.preserve_pose_draft()
        self._pose_draft_key=None
        self.model.current=name
        poses=self.model.animations.get(name,[])
        if poses:
            self.select_step(0)
        else:
            # No saved destination pose exists. Keep shared creature base art,
            # but never show a Slimer overlay from the previous animation.
            # Existing saved snapshots own their own overlay pixels, so hiding
            # the live layer here does not alter any saved timeline pose.
            self._pose_draft_key=None
            self._pose_live_id=None
            self.frame=0
            if previous_animation != name:
                for part in self.model.parts:
                    if part.get('name') == 'Slimer pose overlay':
                        part['visible'] = False
        if previous_animation != name:
            # The destination has now been applied (if saved), so derive the
            # fresh Slimer source from the destination rather than the old pose.
            self._reset_slimer_for_project_change()
        if not poses:
            self.refresh()
        self.refresh_timeline()
        self.refresh_preview()
    def select_step(self,index):
        if index<0:return
        animation=self.anim.currentText()
        previous_key=self._pose_draft_key
        next_key=self._saved_pose_key(animation,index)
        if (previous_key is not None and previous_key != next_key
                and self._next_pose_capture_pending):
            self.status.setText('Place Frame to keep your next-pose edits, or Save Current Pose to intentionally replace this pose, before switching frames.')
            return
        changing_pose=previous_key is not None and previous_key != next_key
        self.begin_pose_draft(animation,index)
        self.frame=index
        poses=self.model.animations.get(animation,[])
        if index<len(poses):
            self._apply_saved_pose(animation,index)
            if not (0 <= self.selected < len(self.model.parts)
                    and self.model.parts[self.selected].get('visible', True)):
                self.selected=next((i for i in range(len(poses[index])-1,-1,-1)
                    if poses[index][i].get('visible', True)), -1)
            self.select_asset(self.selected)
        if changing_pose:
            self._reset_slimer_for_project_change()
        self.refresh()
    def sync_slimer_asset_labels(self):
        """Number the Slimer overlay by its selected timeline pose, not by layer count.

        The canonical model layer name remains unchanged: the UI label is only a
        presentation of the active pose. This avoids using mutable display names
        as layer identifiers and does not rewrite saved pose snapshots.
        """
        if not hasattr(self, 'assets'):
            return
        animation = self.anim.currentText()
        poses = self.model.animations.get(animation, [])
        number = self.frame + 1 if 0 <= self.frame < len(poses) else None
        merged_working_pose = (number is not None
            and self._pose_needs_slimer_merge(poses[self.frame])
            and any(state.get('visible', True) and
                    state.get('name','').startswith('Combined Artwork ')
                    for state in poses[self.frame]))
        for index, part in enumerate(self.model.parts):
            if index >= self.assets.count():
                break
            canonical = part.get('name', '')
            if canonical == 'Slimer pose overlay':
                # A pose predating this layer must not claim ownership of it.
                owned = (number is not None and index < len(poses[self.frame])
                         and poses[self.frame][index].get('visible', True))
                label = f'Slimer Pose {number:03d}' if owned else 'Slimer pose overlay (not in this pose)'
            else:
                label = canonical
            # Visibility is pose-specific: never rename or delete the shared
            # model asset merely to indicate that this pose hides it.
            visible = bool(part.get('visible', True))
            if not visible:
                label += '  [hidden in this pose]'
            item = self.assets.item(index)
            item.setText(label)
            # Preserve every old asset in the model and older pose snapshots,
            # but hide its inactive row when working from a combined pose.
            # QListWidgetItem hiding does not change model asset indices.
            # Inactive inherited assets are *not* part of this pose's working
            # artwork.  Keep them in the saved snapshots and global index,
            # but show only this pose's editable source by default.  The
            # optional toggle still allows users to inspect/restore a layer.
            item.setHidden(bool(not visible and not self.show_hidden_assets.isChecked()))
            item.setToolTip('Hidden in the selected working pose; restore to show it.' if not visible else 'Visible in the selected working pose.')
            from PySide6.QtGui import QColor
            item.setForeground(QColor('#84919e') if not visible else QColor('#e5e7eb'))
        self._refresh_pose_asset_controls()
        if 0 <= self.selected < self.assets.count():
            self.active_asset_label.setText(f'Editing: {self.assets.item(self.selected).text()}')

    def _refresh_pose_asset_controls(self):
        if not hasattr(self, 'pose_asset_remove'):
            return
        frames = self.model.animations.get(self.anim.currentText(), [])
        valid = 0 <= self.frame < len(frames) and 0 <= self.selected < len(self.model.parts)
        visible = bool(self.model.parts[self.selected].get('visible', True)) if valid else False
        self.pose_asset_remove.setEnabled(valid and visible)
        self.pose_asset_restore.setEnabled(valid and not visible)
        if hasattr(self, 'pose_asset_state'):
            self.pose_asset_state.setText(
                ('Visible in this pose' if visible else 'Hidden in this pose — other poses unaffected')
                if valid else 'Select a saved pose and asset to manage visibility.')

    def _timeline_rows_moved(self, parent, start, end, destination_parent, destination_row):
        """Queue identity-preserving model reconciliation until Qt finishes drop.

        rowsMoved fires *inside* QListWidget's drop processing, where clearing
        and repopulating the widget can invalidate item pointers. A queued
        model commit avoids both premature selection loads and unsafe refresh.
        """
        if end != start or parent.isValid() or destination_parent.isValid():
            QTimer.singleShot(0, self.refresh_timeline)
            return
        target = destination_row - 1 if destination_row > start else destination_row
        name = self.anim.currentText()
        poses = self.model.animations.get(name, [])
        if not (0 <= start < len(poses) and 0 <= target < len(poses)):
            QTimer.singleShot(0, self.refresh_timeline)
            return
        # Current index still refers to the *old model*, never the visually
        # relocated QListWidget row. Do not call load_frame before commit.
        QTimer.singleShot(0, lambda: self._commit_timeline_drag(name, start, target))

    def _commit_timeline_drag(self, name, start, target):
        """Reorder pose pixels, stable IDs and durations in one undoable step."""
        if self.anim.currentText() != name:
            self.refresh_timeline()
            return
        frames = self.model.animations.get(name, [])
        if not (0 <= start < len(frames) and 0 <= target < len(frames)):
            self.refresh_timeline()
            return
        if start == target:
            self.select_timeline_pose(self.frame)
            return
        # The previously edited canvas belongs to self._pose_draft_key;
        # saving it before touching model order prevents cross-pose leakage.
        self.preserve_pose_draft()
        self.remember()
        new_index = self.model.reorder_frame(name, start, target)
        self._pose_draft_key = None
        self._pose_draft_dirty = False
        self._timeline_structure_changed()
        self.select_timeline_pose(new_index)
        self.status.setText(
            f'Reordered pose {start+1} to position {new_index+1}. '
            'Artwork and timing stayed with their poses. Ctrl+Z to undo.')

    def refresh_timeline(self):
        if not hasattr(self,'timeline'):return
        was_blocked = self.timeline.blockSignals(True)
        try:
            self.timeline.clear()
            for i,_ in enumerate(self.model.animations.get(self.anim.currentText(),[])):
                # A real rendered miniature helps new animators identify each pose at a glance.
                pose=self.model.animations[self.anim.currentText()][i]
                item_text=f'Pose {i+1} · {self.model.frame_duration(self.anim.currentText(),i)}ms'
                from PySide6.QtWidgets import QListWidgetItem
                item=QListWidgetItem(item_text)
                try:
                    image=self.model.render(pose)
                    item.setIcon(QIcon(pixmap(image,66)))
                except (ValueError, IndexError, KeyError, OSError) as exc:
                    item.setToolTip(f'Preview unavailable: {exc}')
                self.timeline.addItem(item)
            if 0 <= self.frame < self.timeline.count():
                self.timeline.setCurrentRow(self.frame)
        finally:
            self.timeline.blockSignals(was_blocked)
        self.sync_slimer_asset_labels()
    def load_frame(self,index):
        self.elapsed_ms=0
        animation=self.anim.currentText()
        poses=self.model.animations.get(animation,[])
        if 0<=index<len(poses):
            # An unfinished selection is derived from one pose's pixels. It
            # must never be replayed on another pose, even when Slimer remains
            # the active tool. A same-pose refresh should not discard it.
            previous_key=self._pose_draft_key
            next_key=self._saved_pose_key(animation,index)
            changing_pose=previous_key is not None and previous_key != next_key
            if previous_key is not None and self._next_pose_capture_pending:
                # Even re-clicking the SAME saved thumbnail must not discard
                # an unfinished next-pose draft after Save Creature/reopen.
                blocked=self.timeline.blockSignals(True)
                try:self.timeline.setCurrentRow(self.frame)
                finally:self.timeline.blockSignals(blocked)
                self.status.setText('Unplaced next-pose edits: Place Frame to create the new pose or Save Current Pose to intentionally replace this pose. Nothing was overwritten.')
                return
            self.begin_pose_draft(animation,index)
            self.frame=index;self._apply_saved_pose(animation,index)
            if not (0 <= self.selected < len(self.model.parts)
                    and self.model.parts[self.selected].get('visible', True)):
                self.selected=next((i for i in range(len(poses[index])-1,-1,-1)
                    if poses[index][i].get('visible', True)), -1)
            self.select_asset(self.selected)
            if changing_pose:
                self._reset_slimer_for_project_change()
            was_blocked = self.duration.blockSignals(True)
            try:
                self.duration.setValue(self.model.frame_duration(animation,index))
            finally:
                self.duration.blockSignals(was_blocked)
            self.sync_slimer_asset_labels();self.refresh()
    def save_frame(self):
        """Save only an existing selected pose; never create frames implicitly."""
        if not self.model.parts:
            QMessageBox.warning(self,'No assets','Import creature parts first.')
            return
        name=self.anim.currentText()
        poses=self.model.animations.get(name,[])
        if not 0 <= self.frame < len(poses):
            QMessageBox.information(self,'No selected pose','Use Place Frame to create a pose first.')
            return
        target_key = self._saved_pose_key(name, self.frame)
        if not self._canvas_owns_selected_pose(name):
            self.status.setText('Cannot save this pose: the canvas belongs to a different frame. Select this pose to reload it safely.')
            return
        self.remember()
        self.model.save_pose_at(name,self.frame)
        self._next_pose_capture_pending=False
        self.model.unplaced_next_pose = None
        self._pose_draft_key=target_key
        self._pose_draft_dirty=False
        self.refresh_timeline()
        self.status.setText(f'Saved {name} pose {self.frame+1} without changing other poses.')
        self.refresh()
    def restore_previous_timeline_pose(self):
        """Restore only the selected saved pose, then reload its canvas and thumbnail."""
        name = self.anim.currentText()
        index = self.timeline.currentRow()
        poses = self.model.animations.get(name, [])
        if not 0 <= index < len(poses):
            QMessageBox.information(self, 'No selected pose', 'Select a saved timeline pose first.')
            return
        pose_id = self.model.pose_id(name, index)
        if not self.model.pose_recovery.get(pose_id):
            QMessageBox.information(self, 'No previous version', 'This pose has no earlier saved version to restore.')
            return
        # A restore deliberately discards the current unsaved draft. Do not
        # allow load_frame() to auto-save it over the recovered snapshot.
        self.remember()
        self._pose_draft_dirty = False
        if not self.model.restore_previous_pose(name, index):
            return
        self._pose_draft_key = None
        self.select_timeline_pose(index)
        # The recovered pose is now the only valid selection source. A Slimer
        # selection made against the discarded version must not be replayed.
        # Keep the Slimer tool active, but clear its transient selection state.
        self._reset_slimer_for_project_change()
        self.refresh()
        self.status.setText(f'Restored previous version of {name} pose {index+1}. Save Creature to keep this recovery on disk.')

    def duplicate_frame(self):
        """Append an independent snapshot through the identity-safe model API."""
        if self._slimer_pending_layer is not None:
            self.status.setText('Apply Move or Cancel before duplicating a pose.')
            return
        if not self._canvas_owns_selected_pose(self.anim.currentText()):
            return
        self.preserve_pose_draft()
        if not self.model.parts:
            QMessageBox.warning(self, 'No artwork', 'Import creature artwork first.')
            return
        name = self.anim.currentText()
        frames = self.model.animations.get(name, [])
        if not frames:
            QMessageBox.information(self, 'No pose to duplicate', 'Use Place Frame to create your first timeline pose.')
            return
        self.remember()
        # Duplicate the selected saved snapshot, not whatever temporary Slimer
        # overlay happens to be visible on the working canvas.
        source_index = min(max(self.frame, 0), len(frames) - 1)
        if self._pose_needs_slimer_merge(frames[source_index]):
            index = self._insert_next_working_pose(name, source_index + 1, frames[source_index])
            if index is None:
                return
        else:
            index = self.model.copy_frame(name, source_index)
            self._pose_draft_key = None
            self.select_timeline_pose(index)
        self._timeline_structure_changed()
        self.status.setText(f'Duplicated pose {source_index + 1} as pose {index + 1} in {name}. '
                            'Slimer layers were combined only in the new pose.'
                            if self._pose_needs_slimer_merge(frames[source_index])
                            else f'Duplicated pose {source_index + 1} as pose {index + 1} in {name}.')
    def select_timeline_pose(self,index):
        """Load the requested pose even if the row number did not change.

        A new frame inserted at the same row index as the previously selected
        frame must still load its own snapshot and update the draft identity.
        """
        self.refresh_timeline()
        if not 0 <= index < self.timeline.count():
            return
        was_blocked = self.timeline.blockSignals(True)
        try:
            self.timeline.setCurrentRow(index)
        finally:
            self.timeline.blockSignals(was_blocked)
        self.load_frame(index)

    def _timeline_structure_changed(self):
        """Restart preview timing after frame count/order changes.

        Keep the user's Play/Pause choice; never carry elapsed time from a
        different timeline layout into the new one.
        """
        self.restart_playback()

    def insert_pose(self):
        if self._slimer_pending_layer is not None:
            self.status.setText('Apply Move or Cancel before inserting a pose.')
            return
        if not self._canvas_owns_selected_pose(self.anim.currentText()):
            return
        self.preserve_pose_draft()
        if not self.model.parts:
            QMessageBox.warning(self,'Add a creature first','Import your creature parts before adding a pose.');return
        self.remember()
        animation=self.anim.currentText()
        poses=self.model.animations.get(animation,[])
        # Insert immediately after the selected pose, even in the middle.
        # The model creates an independent snapshot and shifts later poses.
        source_pose = self.model.snapshot()
        if self._pose_needs_slimer_merge(source_pose):
            index=self._insert_next_working_pose(animation,min(max(self.frame+1,0),len(poses)),source_pose)
            if index is None:
                return
        else:
            index=self.model.insert_frame(animation,min(max(self.frame+1,0),len(poses)))
            self.select_timeline_pose(index)
        self._timeline_structure_changed()
        self.status.setText(f'Inserted pose {index+1} after the selected pose. Later poses were preserved.')

    def import_pose_png_overlay(self):
        """Build one new editable pose over the selected saved pose."""
        return self.import_pose_png(mode='overlay')

    def import_pose_png(self, *, mode='exact'):
        """Import a PNG as an exact or over-previous independent new pose."""
        if mode not in ('exact', 'overlay'):
            raise ValueError('Unsupported pose import mode.')
        if self._slimer_pending_layer is not None:
            self.status.setText('Apply Move or Cancel the unconfirmed Slimer layer before importing a pose.')
            return
        path,_=QFileDialog.getOpenFileName(self,'Import PNG as new pose','','PNG images (*.png)')
        if not path:return
        try:
            with Image.open(path) as opened:
                image=opened.convert('RGBA')
            if image.size!=tuple(self.model.size):
                QMessageBox.warning(self,'Pose size mismatch',
                    f'The PNG is {image.width} × {image.height} pixels, but this canvas is '
                    f'{self.model.size[0]} × {self.model.size[1]}. Export a frame PNG '
                    'to get the correct transparent canvas dimensions.')
                return
            self.preserve_pose_draft()
            self.remember()
            animation=self.anim.currentText()
            frames=self.model.animations.get(animation,[])
            # The base must be captured before inserting or importing anything.
            # For a blank timeline, the current unsaved work is the base.
            if frames:
                source_index=min(max(self.frame,0),len(frames)-1)
                base_pose=deepcopy(frames[source_index])
            else:
                base_pose=deepcopy(self.model.snapshot())
            index=self.model.insert_frame(animation,min(self.frame+1,len(frames)))
            self.model.replace_frame_image(animation,index,image,mode=mode,base_pose=base_pose if mode=='overlay' else None)
            # Importing the new PNG asset temporarily changes the live model.
            # The previous pose was already preserved above: clear its draft
            # identity BEFORE loading the imported pose, or load_frame() can
            # accidentally save the imported source into the old pose.
            self._pose_draft_key = None
            self._pose_draft_dirty = False
            self.assets.addItem(self.model.parts[-1]['name'])
            self._timeline_structure_changed()
            self.select_timeline_pose(index)
            opaque_black=sum(1 for r,g,b,a in image.getdata() if (r,g,b)==(0,0,0) and a==255)
            if mode=='overlay':
                description='built over the previous pose; transparent PNG pixels reveal the previous artwork'
            else:
                description='exact RGBA imported; transparent pixels stay transparent'
            self.status.setText(
                f'Imported {Path(path).name} as independent pose {index+1} ({description}; '
                f'opaque black in PNG: {opaque_black} px). Other poses unchanged.')
        except (OSError,ValueError) as exc:
            QMessageBox.warning(self,'Could not import pose',str(exc))

    def copy_pose(self):
        if self._slimer_pending_layer is not None:
            self.status.setText('Apply Move or Cancel before copying a pose.')
            return
        if not self._canvas_owns_selected_pose(self.anim.currentText()):
            return
        self.preserve_pose_draft()
        frames=self.model.animations.get(self.anim.currentText(),[])
        if not frames:
            self.insert_pose();return
        self.remember()
        name=self.anim.currentText()
        source_index=min(self.frame,len(frames)-1)
        if self._pose_needs_slimer_merge(frames[source_index]):
            index=self._insert_next_working_pose(name,source_index+1,frames[source_index])
            if index is None:
                return
        else:
            index=self.model.copy_frame(self.anim.currentText(),min(self.frame,len(frames)-1))
            self.select_timeline_pose(index)
        self._timeline_structure_changed()
        self.status.setText('Copied your pose. Make a small change to animate it!')

    def remove_pose(self):
        self.preserve_pose_draft()
        self._pose_draft_key=None
        frames=self.model.animations.get(self.anim.currentText(),[])
        if not frames:return
        self.remember()
        self.model.delete_frame(self.anim.currentText(),min(self.frame,len(frames)-1))
        self._timeline_structure_changed()
        if frames:
            # Load the surviving snapshot; never leave the deleted pose active.
            self.select_timeline_pose(min(self.frame, len(frames)-1))
        else:
            # Deleting the final pose must not leave its Slimer overlay visible
            # as if it were still saved in the empty timeline.
            self.frame = 0
            self._pose_draft_key = None
            self._pose_draft_dirty = False
            for part in self.model.parts:
                if part.get('name') == 'Slimer pose overlay':
                    part['visible'] = False
            self._reset_slimer_for_project_change()
            self.refresh_timeline()
            self.refresh()
        self.status.setText('Pose removed. Use Undo if you change your mind.')

    def shift_pose(self,direction):
        self.preserve_pose_draft()
        self._pose_draft_key=None
        frames=self.model.animations.get(self.anim.currentText(),[])
        if not frames:return
        index=min(self.frame,len(frames)-1)
        if not 0 <= index+direction < len(frames):return
        self.remember()
        self._timeline_structure_changed()
        self.select_timeline_pose(self.model.move_frame(self.anim.currentText(),index,direction))
        self.status.setText('Pose order updated.')

    def change_duration(self, value):
        frames=self.model.animations.get(self.anim.currentText(),[])
        if 0 <= self.frame < len(frames):
            name = self.anim.currentText()
            old_durations = [self.model.frame_duration(name, i) for i in range(len(frames))]
            if old_durations[self.frame] != value:
                self.remember()
                # Consume time already spent playing before changing the timeline.
                if self.play.isChecked():
                    self.elapsed_ms += self.playback_clock.delta_ms() * float(self.speed.currentData())
                self.elapsed_ms = retime_elapsed(old_durations, self.frame, self.elapsed_ms, value, self.loop.isChecked())
            self.model.set_frame_duration(name,self.frame,value)
            self.refresh_timeline()
            summary=timeline_summary([self.model.frame_duration(self.anim.currentText(),i) for i in range(len(frames))])
            self.status.setText(f'Pose timing updated • {summary["seconds"]:.2f}s total for {summary["frames"]} poses. Shorter means faster!')

    def prev_frame(self):
        """Navigate to the previous saved timeline pose."""
        poses = self.model.animations.get(self.anim.currentText(), [])
        if poses:
            self.select_timeline_pose(max(0, min(self.frame, len(poses)-1)-1))

    def next_frame(self):
        """Navigate saved poses, respecting the current animation's length."""
        poses = self.model.animations.get(self.anim.currentText(), [])
        if poses:
            self.select_timeline_pose(min(len(poses)-1, max(0, self.frame)+1))
    def play_toggled(self, playing):
        name = self.anim.currentText()
        poses = self.model.animations.get(name, [])
        if playing and not poses:
            was_blocked = self.play.blockSignals(True)
            try:
                self.play.setChecked(False)
            finally:
                self.play.blockSignals(was_blocked)
            self.playback_clock.pause()
            self.play.setText('▶ Play your animation')
            self.status.setText('Add a pose first, then press Play.')
            self.refresh_preview()
            return
        if playing:
            durations = [self.model.frame_duration(name, i) for i in range(len(poses))]
            self.elapsed_ms = resume_position(self.elapsed_ms, durations, self.loop.isChecked())
            self.playback_clock.resume()
        else:
            self.playback_clock.pause()
        self.play.setText('⏸ Pause animation' if playing else '▶ Play your animation')
        self.refresh_preview()
    def restart_playback(self,*_):
        self.elapsed_ms=0;self.playframe=0
        if self.play.isChecked():
            self.playback_clock.resume()
        else:
            self.playback_clock.pause()
        self.refresh_preview()
    def tick(self):
        if not self.play.isChecked():return
        name=self.anim.currentText();poses=self.model.animations.get(name,[])
        if not poses:return
        durations=[self.model.frame_duration(name,i) for i in range(len(poses))]
        self.elapsed_ms+=self.playback_clock.delta_ms()*float(self.speed.currentData())
        if not self.loop.isChecked() and self.elapsed_ms>=sum(durations):
            self.elapsed_ms=float(sum(durations))
            self.play.setChecked(False)
        self.refresh_preview()
    def canvas_view_changed(self):
        self.zoom_label.setText(f'{round(self.canvas.zoom*100)}%')
        self.canvas.update()
    def change_preview_zoom(self,step):
        self.preview_zoom=150 if step==0 else max(50,min(600,self.preview_zoom+step))
        self.refresh_preview()

    def export_current_frame(self):
        name=self.anim.currentText()
        poses=self.model.animations.get(name,[])
        pose=poses[self.frame] if 0<=self.frame<len(poses) else None
        filename,_=QFileDialog.getSaveFileName(self,'Export current frame as transparent PNG',f'friendly_frame_{self.frame+1}.png','PNG images (*.png)')
        if filename:
            self.model.render(pose).save(filename,'PNG')
            self.status.setText('Exported transparent frame PNG for editing in Slime House Studios.')

    def export_all_frames(self):
        """Save every timeline pose as a transparent PNG with timing JSON."""
        filename,_=QFileDialog.getSaveFileName(
            self,'Export all animation frames', 'friendly_frames',
            'Frame set base name (*)')
        if not filename:
            return
        destination=Path(filename)
        try:
            images, metadata=self.model.export_individual_frames(destination.parent, destination.stem)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self,'Could not export frames',str(exc))
            return
        self.status.setText(f'Exported {len(images)} transparent pose PNGs and {metadata.name}.')

    def choose_shs_location(self):
        """Let the user choose the installed or portable SHS .exe once."""
        previous=str(self.settings.value('shs_executable','') or '')
        start=str(Path(previous).parent) if previous and Path(previous).is_file() else ''
        exe,_=QFileDialog.getOpenFileName(
            self,'Select Slime House Studios application',start,
            'Windows applications (*.exe)')
        if not exe:
            return None
        selected=Path(exe)
        if selected.suffix.lower()!='.exe' or not selected.is_file():
            QMessageBox.warning(self,'Invalid SHS application','Please select an existing Windows .exe file.')
            return None
        self.settings.setValue('shs_executable',str(selected))
        self.status.setText(f'SHS application location saved: {selected}')
        return str(selected)

    def _locate_shs(self):
        """Reuse the saved application path, or request it from the user."""
        stored=str(self.settings.value('shs_executable','') or '')
        if stored and Path(stored).is_file() and Path(stored).suffix.lower()=='.exe':
            return stored
        if stored:
            QMessageBox.information(self,'SHS location changed',
                'The previously selected SHS application was moved or removed. Please select it again.')
        return self.choose_shs_location()

    def edit_frame_in_shs(self):
        """Export one independent frame to a temporary PNG and open it in SHS."""
        animation=self.anim.currentText()
        poses=self.model.animations.get(animation,[])
        if not 0<=self.frame<len(poses):
            QMessageBox.information(self,'Choose a pose','Save or select a pose first.')
            return
        exe=self._locate_shs()
        if not exe:return
        work=Path(tempfile.mkdtemp(prefix='friendly_animator_shs_'))
        png=work/f'frame_{self.frame+1}.png'
        try:
            self.model.render(poses[self.frame]).save(png,'PNG')
            subprocess.Popen([exe,str(png)])
        except (OSError,ValueError) as exc:
            QMessageBox.warning(self,'Could not open SHS',str(exc));return
        self._shs_edit=(str(png),self._active_project_id,animation,self.frame)
        self.status.setText('Opened frame in SHS. Save the PNG there, then click Reload SHS Edit.')

    def reload_shs_edit(self):
        """Import an SHS PNG into its original stable timeline pose; report success.

        The linked frame is never appended as a new pose. Its original pose ID,
        current canvas ownership and active project must still match; otherwise
        keep the saved external PNG and fail closed without modifying the rig.
        """
        if not self._shs_edit:
            QMessageBox.information(self,'No SHS edit','Click Edit Frame in SHS first.')
            return False
        path,project_id,animation,index=self._shs_edit
        if project_id!=self._active_project_id or animation!=self.anim.currentText() or index!=self.frame:
            QMessageBox.information(self,'Select original pose','Switch back to the original project, animation, and pose before reloading.')
            return False
        poses=self.model.animations.get(animation,[])
        if not 0 <= index < len(poses):
            QMessageBox.warning(self,'Original pose unavailable','The original saved pose no longer exists. Nothing was imported.')
            return False
        expected_id=getattr(self,'_shs_pose_id',None)
        if expected_id is not None and self.model.pose_id(animation,index)!=expected_id:
            QMessageBox.warning(self,'Original pose changed',
                'The original frame was reordered or replaced. Nothing was imported into a different pose.')
            return False
        if (getattr(self,'_next_pose_capture_pending',False)
                or getattr(self,'_slimer_pending_part',None) is not None
                or getattr(self,'_slimer_pending_layer',None) is not None):
            QMessageBox.information(self,'Unfinished Wizard edit',
                'Place, apply, or cancel the unfinished Wizard edit before importing the SHS PNG.')
            return False
        try:
            with Image.open(path) as source:
                source.load()
                if source.format!='PNG':
                    raise ValueError('The edited file is not a PNG.')
                edited=source.convert('RGBA').copy()
            if edited.size!=tuple(self.model.size):
                QMessageBox.warning(self,'Canvas size mismatch',f'Edited PNG is {edited.size}; expected {self.model.size}. Keep the canvas size unchanged in SHS.')
                return False
            self.preserve_pose_draft();self.remember()
            self.model.replace_frame_image(animation,index,edited)
            self.assets.addItem(self.model.parts[-1]['name'])
            self._pose_draft_key=self._saved_pose_key(animation,index)
            self._pose_draft_dirty=False
            self._apply_saved_pose(animation,index)
            self.assets.setCurrentRow(len(self.model.parts)-1)
            self.refresh_timeline();self.refresh()
            self.status.setText(f'Reloaded SHS edit into pose {index+1} only. Main Undo can reverse it.')
            return True
        except (OSError,ValueError,IndexError,KeyError) as exc:
            QMessageBox.warning(self,'Could not reload SHS edit',str(exc))
            return False

    def replace_current_frame_png(self):
        """Replace only the selected saved pose with an edited full-canvas PNG."""
        animation=self.anim.currentText()
        poses=self.model.animations.get(animation,[])
        if not 0<=self.frame<len(poses):
            QMessageBox.information(self,'Choose a frame','Select a saved frame in the Pose Timeline first.')
            return
        path,_=QFileDialog.getOpenFileName(self,'Replace current frame from Slime House Studios','','PNG images (*.png)')
        if not path:return
        try:
            with Image.open(path) as opened:
                edited=opened.convert('RGBA')
            if edited.size!=tuple(self.model.size):
                QMessageBox.warning(self,'Frame size mismatch',
                    f'This PNG is {edited.width} × {edited.height} pixels. The creature canvas is {self.model.size[0]} × {self.model.size[1]}.\n\nExport the frame first and keep its original canvas dimensions when editing in Slime House Studios.')
                return
            # Capture the current frame before adding a new independent overlay.
            # Existing saved poses keep their own source pixels and remain untouched.
            self.preserve_pose_draft()
            self.remember()
            self.model.replace_frame_image(animation,self.frame,edited)
            self.assets.addItem(self.model.parts[-1]['name'])
            self._pose_draft_key=self._saved_pose_key(animation,self.frame)
            self._pose_draft_dirty=False
            self._apply_saved_pose(animation,self.frame)
            self.assets.setCurrentRow(len(self.model.parts)-1)
            self.refresh_timeline()
            self.refresh()
            self.status.setText(f'Replaced only frame {self.frame+1} from PNG. Main Undo reverses this change.')
        except (OSError,ValueError) as exc:
            QMessageBox.warning(self,'Could not replace frame',str(exc))

    def refresh_preview(self, current_render=None):
        name=self.anim.currentText()
        poses=self.model.animations.get(name,[])
        if poses and (self.play.isChecked() or self.elapsed_ms > 0):
            durations=[self.model.frame_duration(name,i) for i in range(len(poses))]
            creature_index=frame_at_time(durations,self.elapsed_ms,self.loop.isChecked())
        else:
            creature_index=self.frame if 0<=self.frame<len(poses) else None
        pose=poses[creature_index] if creature_index is not None else None
        # The live canvas was already rendered by refresh(). Reuse it only
        # when no saved pose is selected; saved poses must keep their own
        # independent frame image instead of borrowing unsaved canvas edits.
        preview_image = current_render if pose is None and isinstance(current_render, Image.Image) else self.model.render(pose)
        self.preview.setPixmap(pixmap(preview_image,self.preview_zoom))
        self.preview.resize(max(150,self.preview_zoom),max(150,self.preview_zoom))
    def refresh(self):
        self.canvas._image_size=self.model.size;self.canvas.parts=self.model.parts;self.canvas.selected=self.selected;self.canvas.anchors=self.model.anchors;self.canvas.angles=self.model.angles
        self.canvas.slimer_staged_part=getattr(self, '_slimer_pending_part', None)
        self.canvas.sync_canvas_handle_layers(self.model.parts, self.selected,
                                              self._slimer_pending_part is not None)
        # Preserve an untouched model render for clean Slimer/Frame previews.
        # Selection tints and joint guides must only modify the *editor* image.
        # PIL alpha_composite() mutates its receiver in place: if composed and
        # live_render are aliases, the supposedly clean preview turns green.
        live_render=self.model.render()
        composed=live_render
        if self.onion.isChecked():
            poses=self.model.animations.get(self.anim.currentText(),[])
            previous=self.model.render(poses[self.frame-1]) if 0<self.frame<=len(poses) else None
            following=self.model.render(poses[self.frame+1]) if self.onion_next.isChecked() and self.frame+1<len(poses) else None
            composed=onion_composite(composed,previous,following)
        # Layer handles are drawn in DragCanvas.paintEvent (fixed-size UI)
        # rather than baked into the artwork, preview or exported pixel buffer.
        # Joint dots are editor-only guides and never appear in exported sprites.
        # Slimer creates a rotation pivot on every staged move layer; displaying
        # every stored pivot indefinitely leaves a misleading yellow "knob" on
        # artwork after Apply Move. Show joint guides ONLY while the user has
        # deliberately activated the Place a joint dot tool. Retain all pivots
        # in the model for future rotations, even when their guides are hidden.
        if self.canvas.anchor_mode and self.model.anchors:
            if composed is live_render:
                composed=live_render.copy()
            from PIL import ImageDraw
            guide=Image.new('RGBA',composed.size)
            draw=ImageDraw.Draw(guide)
            for index in self.model.anchors:
                if index>=len(self.model.parts):continue
                ax,ay=self.model.anchor_position(index)
                draw.ellipse((ax-2,ay-2,ax+2,ay+2),fill=(255,204,51,255),outline=(35,40,35,255))
            composed.alpha_composite(guide)
        self.canvas.slimer_bounds=None
        confirmed_slimer_preview=None
        if self.slimer_toggle.isChecked() and self.slimer_selection is not None and self._slimer_pending_part is None:
            from PIL import ImageDraw
            # Preview highlighted pixels immediately, but only float the result
            # over the canvas after entering transform mode.
            if self.slimer_selection.mask.getbbox() is not None:
                confirmed_slimer_preview=self.slimer_preview()
            if self.canvas.slimer_transform_mode:
                preview=confirmed_slimer_preview
                self.canvas.slimer_bounds=preview.getchannel('A').getbbox()
                if self.canvas.slimer_bounds is None and self.slimer_selection.mask.getbbox():
                    x0,y0,x1,y1=self.slimer_selection.mask.getbbox()
                    self.canvas.slimer_bounds=(x0+self.slimer_dx.value(),y0+self.slimer_dy.value(),x1+self.slimer_dx.value(),y1+self.slimer_dy.value())
                if composed is live_render:
                    composed=live_render.copy()
                composed.alpha_composite(preview)
            else:
                self.canvas.slimer_bounds=self.slimer_selection.mask.getbbox()
            marker=Image.new('RGBA',composed.size)
            # A 10% tint (alpha 26) was nearly invisible on detailed pixel art.
            # Keep the selected color clearly visible without changing source pixels.
            marker.putalpha(self.slimer_selection.mask.point(lambda v: 120 if v else 0))
            chosen=QColor(self.slimer_phase_colors.get(self.slimer_phase_picker.currentText(),'#54e88a'))
            tint=Image.new('RGBA',composed.size,(chosen.red(),chosen.green(),chosen.blue(),0));tint.putalpha(marker.getchannel('A'))
            if not self.canvas.slimer_transform_mode:
                if composed is live_render:
                    composed=live_render.copy()
                composed.alpha_composite(tint)
        # Convert the final editor composite once, after Slimer highlights.
        # Avoid allocating two full-size RGBA buffers on every brush stroke,
        # especially for optional 512/1024-pixel canvases.
        rgba=composed.convert('RGBA')
        data=rgba.tobytes('raw','RGBA')
        image=QImage(data,rgba.width,rgba.height,rgba.width*4,QImage.Format.Format_RGBA8888).copy()
        self.canvas.set_art(QPixmap.fromImage(image))
        if hasattr(self, 'slimer_preview_label'):
            # Slimer Preview is a clean LIVE view of the current canvas,
            # matching the frame preview's full-artwork composition instead
            # of isolating the brush mask.  All editor-only overlays are drawn
            # onto `composed` or by DragCanvas.paintEvent, not `live_render`.
            if self.slimer_toggle.isChecked() or self._slimer_pending_part is not None:
                self.slimer_preview_label.setPixmap(pixmap(live_render, 132))
                self.slimer_preview_label.setText('')
            else:
                self.slimer_preview_label.clear()
                self.slimer_preview_label.setText('Activate Slimer for a clean canvas preview')
        self.refresh_preview(live_render)

    def _reset_slimer_for_project_change(self):
        """Discard transient selection state, never project artwork or saved poses.

        The Slimer tool may stay selected across creature tabs. Its source image,
        masks, drag state and transform controls must not survive that boundary.
        """
        self._show_asset_transform_controls(False)
        self._slimer_previous_selected_part = None
        self.slimer_selection_undo.clear()
        self.slimer_selection_redo.clear()
        self.slimer_phase_masks={}
        self.slimer_phase_transforms={}
        self.slimer_phase_histories={}
        self._slimer_current_phase=self.slimer_phase_picker.currentText()
        self._slimer_mouse_transforming=False
        self.canvas._slimer_painting=False
        self.canvas._slimer_last=None
        self.canvas._slimer_handle=None
        self.canvas.slimer_bounds=None
        self.canvas.slimer_transform_mode=False
        with blocked_signals(self.slimer_drag_toggle):
            self.slimer_drag_toggle.setChecked(False)
        self.slimer_drag_toggle.setText('Drag selected pixels (Shift=resize, Alt=rotate)')
        for control,value in ((self.slimer_dx,0),(self.slimer_dy,0),
                              (self.slimer_turn,0),(self.slimer_scale,100)):
            with blocked_signals(control):
                control.setValue(value)
        self.slimer_selection=(SlimerSelection.empty(self.model.render())
                               if self.slimer_toggle.isChecked() else None)
        self._slimer_sync_numeric_values()

    def activate_project(self,project_id):
        if project_id not in self._projects:return
        self.preserve_pose_draft()
        if project_id==self._active_project_id:return
        # Preserve an unplaced next-pose canvas when switching creature tabs.
        # No implicit Save Current Pose, no new timeline frame.
        if getattr(self, '_next_pose_capture_pending', False):
            if not self._remember_unplaced_next_pose():
                return
        else:
            self.model.unplaced_next_pose = None
        self._pose_draft_key=None
        self._pose_live_id=None
        self._projects[self._active_project_id]=self.model
        # Remember the selected timeline index independently for each creature.
        # Project tabs must not inherit another creature's active pose number.
        if not hasattr(self, '_project_timeline_index'):
            self._project_timeline_index = {}
        self._project_timeline_index[self._active_project_id] = self.frame
        self._project_frames[self._active_project_id]=dict(self._workspace_frames)
        self._project_selected[self._active_project_id]=self.selected
        self._project_animation[self._active_project_id]=self.anim.currentText()
        self._project_views[self._active_project_id]=(self.canvas.zoom,self.canvas.pan_x,self.canvas.pan_y)
        self._active_project_id=project_id
        self._workspace_frames=dict(self._project_frames.get(project_id,{}))
        self.model=self._projects[project_id]
        self.canvas.zoom,self.canvas.pan_x,self.canvas.pan_y=self._project_views.get(project_id,(1.0,0.0,0.0))
        self.canvas_view_changed()
        self._project_name=self._project_labels.get(project_id,'Creature')
        self.history=self._project_histories.setdefault(project_id,EditHistory());self.selected=self._project_selected.get(project_id,-1);self.frame=0;self.playframe=0
        remembered=self._project_selected.get(project_id,-1)
        asset_row = remembered if 0<=remembered<len(self.model.parts) else (0 if self.model.parts else -1)
        was_blocked = self.assets.blockSignals(True)
        try:
            self.assets.clear()
            self.assets.addItems([p['name'] for p in self.model.parts])
            self.assets.setCurrentRow(asset_row)
        finally:
            self.assets.blockSignals(was_blocked)
        self.selected = asset_row
        self.refresh_parent_picker()
        was_blocked = self.anim.blockSignals(True)
        try:
            self.anim.clear()
            self.anim.addItems(available_animation_names(self.model))
            self.anim.setCurrentText(preferred_animation(self.model, self._project_animation.get(project_id,self.model.current)))
        finally:
            self.anim.blockSignals(was_blocked)
        animation = self.anim.currentText()
        # Selector signals were blocked during project restoration.
        # Synchronize the model explicitly before restoring its pose.
        self.model.current = animation
        poses = self.model.animations.get(animation, [])
        unplaced = getattr(self.model, 'unplaced_next_pose', None)
        self._next_pose_capture_pending = False
        if poses:
            ids = self.model._sync_pose_ids(animation)
            # A pending draft belongs to one stable saved pose ID. Its pixels
            # live in model.parts, NOT in animations[animation][index].
            # Applying the selected saved pose here would destroy that draft.
            restore_unplaced = (isinstance(unplaced, dict)
                                and unplaced.get('animation') == animation
                                and unplaced.get('pose_id') in ids)
            index = (ids.index(unplaced['pose_id']) if restore_unplaced else
                     min(max(0, self._project_timeline_index.get(project_id, 0)), len(poses)-1))
            self.frame = index
            if restore_unplaced:
                self._pose_live_id = ids[index]
                self._next_pose_capture_pending = True
            else:
                self._apply_saved_pose(animation,index)
            self._pose_draft_key = (project_id, animation, index, ids[index])
        else:
            self.frame = 0
            self._pose_draft_key = None
            self._pose_live_id = None
            self.model.unplaced_next_pose = None
            for part in self.model.parts:
                if part.get('name') == 'Slimer pose overlay':
                    part['visible'] = False
        self._pose_draft_dirty = False
        self._reset_slimer_for_project_change()
        self.refresh_timeline();self.refresh()

    def add_project(self,model,label,path=None):
        self._projects[self._active_project_id]=self.model
        self._project_id+=1;project_id=self._project_id
        self._projects[project_id]=model
        self._project_histories[project_id]=EditHistory()
        self._project_views[project_id]=(1.0,0.0,0.0)
        self._project_frames[project_id]={};self._project_selected[project_id]=-1;self._project_animation[project_id]=preferred_animation(model, model.current)
        self._project_labels[project_id]=label
        if path:self._saved_fingerprints[project_id]=model.content_fingerprint()
        if path:self._project_paths[project_id]=str(path)
        key=('project',f'{project_id}::{label}')
        self.select_workspace_key(key)
        return project_id

    def project_is_dirty(self,project_id):
        model=self.model if project_id==self._active_project_id else self._projects[project_id]
        return model.content_fingerprint()!=self._saved_fingerprints.get(project_id)

    def export_animated(self):
        self.preserve_pose_draft()
        filename,_=QFileDialog.getSaveFileName(
            self,'Choose animation export base filename (GIF + APNG)', 'creature.gif', 'GIF animation (*.gif)')
        if not filename:return
        target=Path(filename)
        basename=target.stem if target.suffix.lower()=='.gif' else target.name
        if not basename.strip():return
        folder=str(target.parent)
        try:
            exported=self.model.export_animations(folder,basename=basename)
            self.status.setText(f'Exported {len(exported)} animation files to {folder}')
        except Exception as exc:
            QMessageBox.warning(self,'Animation export failed',str(exc))

    def confirm_unsaved_projects(self,project_ids):
        """Ask Save/Discard/Cancel for each changed creature, aborting on failed save."""
        self.preserve_pose_draft()
        original_id=self._active_project_id
        for pid in project_ids:
            if pid not in self._projects or not self.project_is_dirty(pid):
                continue
            name=self._project_labels.get(pid,'Creature')
            answer=QMessageBox.question(
                self,'Unsaved creature',
                f'\"{name}\" has unsaved changes.\nSave before closing?',
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save)
            if answer==QMessageBox.StandardButton.Cancel:
                return False
            if answer==QMessageBox.StandardButton.Save:
                if not self.save_project_by_id(pid):
                    return False
        return True

    def _remember_unplaced_next_pose(self):
        """Record the owner of a live next-pose draft without committing it.

        The model saves the live canvas as `parts` and the *previous* saved
        frames as `animations`. Only this small marker is needed for reopening
        the live canvas as unplaced work. Never guess a pose by row number.
        """
        if not self._next_pose_capture_pending:
            self.model.unplaced_next_pose = None
            return True
        animation = self.anim.currentText()
        if not self._canvas_owns_selected_pose(animation):
            self.status.setText('Save blocked: next-pose draft owner could not be verified. The previous poses were not changed.')
            return False
        self.model.unplaced_next_pose = {
            'animation': animation,
            'pose_id': self.model.pose_id(animation, self.frame),
        }
        return True

    def save_project_by_id(self,project_id,force_new_path=False):
        """Save project in place, or explicitly Save As to a distinct rig JSON."""
        if project_id not in self._projects:return False
        if project_id == self._active_project_id:
            if not self._remember_unplaced_next_pose():
                return False
        # A provisional Slimer layer is not yet a committed pose edit. Saving
        # here would serialize the destination asset but omit the source erase,
        # leaving a misleading and potentially doubled-up project on reopen.
        if project_id == self._active_project_id and getattr(self, '_slimer_pending_part', None) is not None:
            self.status.setText('Apply Move or Cancel Unconfirmed Layer before saving this creature.')
            return False
        if project_id==self._active_project_id:self.preserve_pose_draft()
        previous=self._project_paths.get(project_id)
        path=None if force_new_path else previous
        if not path:
            suggested=(str(Path(previous).with_name(Path(previous).stem+'.copy.rig.json'))
                       if force_new_path and previous else
                       self._project_labels.get(project_id,'creature')+'.rig.json')
            path,_=QFileDialog.getSaveFileName(
                self,'Save Creature As' if force_new_path else 'Save creature',
                suggested,'Editable rig project (*.rig.json *.json)')
            if not path:return False
            if not path.lower().endswith('.json'):
                path += '.rig.json'
            if force_new_path and previous and Path(path).resolve()==Path(previous).resolve():
                QMessageBox.warning(self,'Choose another filename',
                    'Save Creature As needs a different filename so the original is preserved.')
                return False
            # Prevent two open tabs from inadvertently sharing a save target.
            for other_id, other_path in self._project_paths.items():
                if other_id!=project_id and other_path and Path(path).resolve()==Path(other_path).resolve():
                    QMessageBox.warning(self,'Already open',
                        'That filename belongs to another open creature. Choose a new name.')
                    return False
        model=self.model if project_id==self._active_project_id else self._projects[project_id]
        try:
            model.save_project(path)
        except Exception as exc:
            QMessageBox.warning(self,'Save failed',str(exc))
            return False
        self._project_paths[project_id]=str(path)
        self._saved_fingerprints[project_id]=model.content_fingerprint()
        self._dirty_projects.discard(project_id)
        discard_project_recovery(project_id)
        if project_id == self._active_project_id and self._next_pose_capture_pending:
            self.status.setText(f'Saved {path} — unfinished NEXT pose preserved as an editable draft; no new timeline frame placed.')
        else:
            self.status.setText(f'Saved {path}')
        return True

    def close_creature_project(self,project_id):
        """Close a creature with Save/Discard/Cancel protection."""
        if project_id not in self._projects:return False
        if len(self._projects)<=1:
            self.status.setText('Keep at least one creature open. Use New creature to start fresh.')
            return False
        if not self.confirm_unsaved_projects([project_id]):return False
        key=next((k for k in self._workspace_tab_keys if k[0]=='project' and k[1].startswith(f'{project_id}::')),None)
        if project_id==self._active_project_id:
            next_id=next(pid for pid in self._projects if pid!=project_id)
            self.activate_project(next_id)
        if key in self._workspace_tab_keys:
            index=self._workspace_tab_keys.index(key)
            self._switching_tab=True
            try:
                self._workspace_tab_keys.pop(index);self.workspace_tabs.removeTab(index)
            finally:self._switching_tab=False
        for mapping in (self._projects,self._project_labels,self._project_paths,self._project_frames,self._project_selected,self._project_animation,self._project_histories,self._project_views):
            mapping.pop(project_id,None)
        self._dirty_projects.discard(project_id);self._saved_fingerprints.pop(project_id,None)
        discard_project_recovery(project_id)
        self.select_workspace_key(('project',next(k[1] for k in self._workspace_tab_keys if k[0]=='project' and k[1].startswith(f'{self._active_project_id}::'))))
        self.status.setText('Creature tab closed.')
        return True

    def rename_project(self):
        pid=self._active_project_id
        old=self._project_labels[pid]
        name,ok=QInputDialog.getText(self,'Rename creature','Creature name:',text=old)
        if not ok or not name.strip():return
        name=name.strip()
        self._project_labels[pid]=name
        self._project_name=name
        for index,key in enumerate(self._workspace_tab_keys):
            if key[0]=='project' and key[1].startswith(f'{pid}::'):
                new_key=('project',f'{pid}::{name}')
                self._workspace_tab_keys[index]=new_key
                self.workspace_tabs.setTabText(index,'🐾 '+name)
                if self._active_workspace==key:self._active_workspace=new_key
        self.status.setText(f'Renamed creature to {name}.')

    def new_project(self):
        # Do not abandon a provisional layer by switching to a new canvas.
        # A staged Move Original has not erased its source yet; changing
        # projects here would discard the pending transaction bookkeeping.
        if getattr(self, '_slimer_pending_part', None) is not None:
            self.status.setText('Apply Move or Cancel Unconfirmed Layer before creating another creature.')
            return
        # Canvas dimensions belong to the creature, not to a global preference.
        # Never resize an existing project as a side effect of creating another.
        presets = ('128 × 128 (default)', '64 × 64', '256 × 256',
                   '512 × 512', '1024 × 1024', 'Custom width × height')
        choice, ok = QInputDialog.getItem(
            self, 'New creature — canvas size',
            'Choose the transparent canvas size (pixels):', presets, 0, False)
        if not ok:
            return
        if choice == 'Custom width × height':
            width, ok = QInputDialog.getInt(
                self, 'Custom canvas width', 'Width (pixels):', 128, 1, 1024, 1)
            if not ok:
                return
            height, ok = QInputDialog.getInt(
                self, 'Custom canvas height', 'Height (pixels):', 128, 1, 1024, 1)
            if not ok:
                return
        else:
            width = height = int(choice.split(' ')[0])
        self.add_project(PetSuiteModel((width, height)),
                         f'Creature {self._project_id+2}')
        self.status.setText(f'New transparent canvas: {width} × {height} pixels.')

    def save_project(self):
        return self.save_project_by_id(self._active_project_id)

    def save_project_as(self):
        return self.save_project_by_id(self._active_project_id,force_new_path=True)

    def open_project(self):
        path,_=QFileDialog.getOpenFileName(self,'Open creature','','Rig project (*.json)')
        if path:
            try:
                resolved=str(Path(path).resolve())
                for pid,existing in self._project_paths.items():
                    if str(Path(existing).resolve())==resolved:
                        self.select_workspace_key(('project',next(k[1] for k in self._workspace_tab_keys if k[0]=='project' and k[1].startswith(f'{pid}::'))))
                        self.status.setText('That creature is already open; switched to its tab.')
                        return
                model=PetSuiteModel.load_project(path)
                self.add_project(model,Path(path).stem,path)
                self.status.setText(f'Opened {path} in a new project tab')
            except Exception as e:QMessageBox.warning(self,'Open failed',str(e))
    def export(self):
        if getattr(self, '_slimer_pending_part', None) is not None:
            self.status.setText('Apply Move or Cancel Unconfirmed Layer before exporting.')
            return
        self.preserve_pose_draft()
        filename,_=QFileDialog.getSaveFileName(
            self,'Choose sprite sheet filename','creature_sheet.png','PNG sprite sheet (*.png)')
        if filename:
            target=Path(filename)
            stem=target.stem if target.suffix.lower()=='.png' else target.name
            basename=stem[:-6] if stem.endswith('_sheet') else stem
            if not basename.strip():return
            try:
                result=self.model.export(target.parent,basename=basename);self.status.setText(f'Exported {result} and JSON metadata')
            except Exception as e:QMessageBox.warning(self,'Export failed',str(e))

def main():
    app=QApplication(sys.argv)
    app.setWindowIcon(wizard_slime_app_icon())
    if '--smoke-test' in sys.argv:
        # Exercise the actual packaged GUI without user interaction.
        # The same executable is used for regular startup and this test.
        try:
            window=Suite()
            window.show()
            app.processEvents()
            if not window.isVisible():
                raise RuntimeError('Main window did not become visible')
            # Exercise transitions with event processing, not only method presence.
            for transition in (window.showMinimized, window.showNormal,
                               window.showMaximized, window.showNormal):
                transition()
                app.processEvents()
            if not window.isVisible() or window.isMinimized() or window.isMaximized():
                raise RuntimeError('Main window failed to restore to normal state')
            # Available geometry differs with taskbars and DPI scaling. Qt's
            # logical coordinates, rather than physical pixels, are authoritative.
            screen=app.primaryScreen()
            if screen is None:
                raise RuntimeError('No screen available for window test')
            area=screen.availableGeometry()
            if area.width() < 1 or area.height() < 1:
                raise RuntimeError('Screen reports invalid available geometry')
            for width,height in ((800,600),(1280,720),(1920,1080)):
                window.showNormal()
                window.resize(min(width,area.width()),min(height,area.height()))
                app.processEvents()
                if not window.isVisible() or window.isMinimized():
                    raise RuntimeError(f'Window became unusable at {width}x{height}')
            window.showMaximized()
            app.processEvents()
            if not window.isMaximized():
                raise RuntimeError('Window failed to maximize')
            window.showNormal()
            app.processEvents()
            if window.isMaximized() or window.isMinimized():
                raise RuntimeError('Window failed to leave maximized state')
            problems=bundled_resource_report()
            if problems:
                raise RuntimeError('; '.join(problems))
            window.hide()
            return 0
        except Exception as exc:
            print(f'GUI smoke test failed: {exc}', file=sys.stderr)
            return 1
    window=Suite();window.show();return app.exec()
if __name__=='__main__':sys.exit(main())
