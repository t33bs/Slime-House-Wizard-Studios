"""SLIME HOUSE WIZARD STUDIOS — one native Qt window, two complete editors.

This host intentionally keeps each editor's QWidget/QMainWindow implementation
intact, with distinct model namespaces and independent project persistence.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QMainWindow, QMessageBox, QPushButton,
    QTabWidget, QVBoxLayout, QWidget, QLabel,
)

from studio.app import MainWindow as SHSEditor
from studio.app import resource_path
from shws_wizard.friendly_animator import Suite as WizardEditor


class EmbeddedWizard(WizardEditor):
    """Adapter for Wizard-only actions that formerly launched another EXE."""

    def __init__(self, host: "SlimeHouseWizardStudios"):
        super().__init__()
        self._unified_host = host

    def ensure_window_visible(self):
        # The unified host controls window bounds. Restoring an old standalone
        # Wizard geometry must not resize/move a widget inside a tab.
        return

    def choose_shs_location(self):
        QMessageBox.information(
            self, 'SHS is already integrated',
            'Slime House Studios is available in the SHS Studio tab. '
            'Use Edit Frame in SHS to send a saved pose directly there.'
        )
        return None

    def edit_frame_in_shs(self):
        """Retain Wizard frame provenance; hand off a PNG without subprocesses."""
        if getattr(self, '_slimer_pending_part', None) is not None:
            self.status.setText('Apply Move or Cancel the unconfirmed layer before editing in SHS.')
            return
        animation = self.anim.currentText()
        poses = self.model.animations.get(animation, [])
        if not 0 <= self.frame < len(poses):
            QMessageBox.information(self, 'Choose a saved pose',
                                    'Save or select a pose in the timeline first.')
            return
        self.preserve_pose_draft()
        poses = self.model.animations.get(animation, [])
        if not 0 <= self.frame < len(poses):
            return
        work = Path(tempfile.mkdtemp(prefix='shws_frame_edit_'))
        png = work / f'frame_{self.frame + 1}.png'
        try:
            self.model.render(poses[self.frame]).save(png, 'PNG')
            # SHS refuses to replace a dirty document, protecting unsaved art.
            self._unified_host.studio.open_external_png(str(png))
        except Exception as exc:
            QMessageBox.warning(self, 'Could not open frame in SHS', str(exc))
            return
        self._shs_edit = (str(png), self._active_project_id, animation, self.frame)
        self._unified_host.tabs.setCurrentWidget(self._unified_host.studio)
        self.status.setText('Frame opened in SHS tab. Save Back to Animator PNG, then reload in Wizard.')


class SlimeHouseWizardStudios(QMainWindow):
    """Tabbed application host; the original full editors remain child widgets."""

    def __init__(self):
        super().__init__()
        self.setObjectName('slimeHouseWizardStudios')
        self.setWindowTitle('SLIME HOUSE WIZARD STUDIOS — Build 1')
        self.setWindowIcon(QIcon(str(resource_path('assets/slime_mascot.png'))))
        self.resize(1500, 900)
        self.setMinimumSize(900, 600)
        self._settings = QSettings('Slime House Wizard Studios', 'UnifiedWorkspace')

        root = QWidget(self)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        top = QWidget(root)
        tools = QHBoxLayout(top)
        tools.setContentsMargins(9, 4, 9, 4)
        brand = QLabel('✦  SLIME HOUSE WIZARD STUDIOS  ✦', top)
        brand.setObjectName('shwsBrand')
        tools.addWidget(brand)
        tools.addStretch(1)
        self.send_back = QPushButton('Save SHS PNG + Reload Wizard Pose', top)
        self.send_back.setToolTip('Only for an Edit Frame in SHS handoff: save the linked PNG and reload the original Wizard pose. Undo remains available in Wizard.')
        self.send_back.clicked.connect(self.reload_edited_frame)
        tools.addWidget(self.send_back)
        layout.addWidget(top)

        self.tabs = QTabWidget(root)
        self.tabs.setObjectName('shwsStudios')
        self.tabs.setDocumentMode(False)
        self.tabs.setMovable(False)
        layout.addWidget(self.tabs, 1)
        self.setCentralWidget(root)

        # Editors have distinct module namespaces. Do not import both as studio.
        self.studio = SHSEditor()
        self.wizard = EmbeddedWizard(self)
        self.tabs.addTab(self.studio, '🎨  SHS Studio')
        self.tabs.addTab(self.wizard, '🧙  Slime Wizard')
        self.tabs.currentChanged.connect(self._tab_changed)
        self.tabs.setCurrentIndex(0)
        self._tab_changed(0)

        self.setStyleSheet('''
            QMainWindow#slimeHouseWizardStudios { background: #151c2c; }
            QLabel#shwsBrand { color: #c7f4dc; font-size: 15px; font-weight: bold; }
            QTabWidget#shwsStudios::pane { border: 1px solid #566586; }
            QTabWidget#shwsStudios > QTabBar::tab {
                color: #e4eafa; background: #273451; padding: 10px 24px;
                border: 1px solid #4c607b; border-bottom: 0;
            }
            QTabWidget#shwsStudios > QTabBar::tab:selected { background: #435683; color: white; }
        ''')

    def _tab_changed(self, index: int):
        is_shs = index == 0
        self.send_back.setVisible(is_shs and bool(self.wizard._shs_edit))
        self._settings.setValue('active_tab', index)

    def reload_edited_frame(self):
        details = self.wizard._shs_edit
        if not details:
            QMessageBox.information(self, 'No linked frame',
                                    'Open a saved Wizard pose using Edit Frame in SHS first.')
            return
        png = Path(details[0]).resolve()
        linked = self.studio.external_png_path
        if linked is None or Path(linked).resolve() != png:
            QMessageBox.warning(self, 'Linked frame changed',
                                'The active SHS document is not the linked Wizard frame. '
                                'Open the original frame again before reloading.')
            return
        # Saving here is explicit. The source project and all other Wizard poses
        # are not replaced; Wizard validates project, animation, pose, and size.
        self.studio.save_external_png()
        if self.studio._dirty:
            return
        self.tabs.setCurrentWidget(self.wizard)
        self.wizard.reload_shs_edit()

    def closeEvent(self, event):
        # Child windows have independent unsaved-work guards. Closing the host
        # must ask both guards instead of allowing Qt to destroy children silently.
        closed = []
        for editor in (self.studio, self.wizard):
            if not editor.close():
                for previous in closed:
                    previous.show()
                event.ignore()
                return
            closed.append(editor)
        self._settings.setValue('window_geometry', self.saveGeometry())
        event.accept()


def main(argv=None):
    argv = sys.argv if argv is None else argv
    app = QApplication.instance() or QApplication(argv)
    app.setApplicationName('Slime House Wizard Studios')
    app.setOrganizationName('Slime House Studios')
    window = SlimeHouseWizardStudios()
    window.show()
    if '--smoke-test' in argv:
        try:
            app.processEvents()
            assert window.isVisible()
            assert window.tabs.count() == 2
            assert window.studio.__class__.__name__ == 'MainWindow'
            assert isinstance(window.wizard, WizardEditor)
            # Switch both live editors, not placeholder screenshots or EXE launchers.
            for index in (0, 1, 0):
                window.tabs.setCurrentIndex(index)
                app.processEvents()
                assert window.tabs.currentWidget().isVisible()
            from studio.pet_suite_model import PetSuiteModel as SHSModel
            from shws_wizard.studio.pet_suite_model import PetSuiteModel as WizardModel
            assert SHSModel is not WizardModel
            assert hasattr(window.studio, 'save_project')
            assert hasattr(window.wizard, 'export_animated')
            print('SHWS smoke test PASS: both live editors, isolated models, and tabs')
            return 0
        except Exception as exc:
            print(f'SHWS smoke test FAIL: {exc}', file=sys.stderr)
            return 1
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
