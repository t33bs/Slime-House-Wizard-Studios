"""Build 1.2: exactly defined Yes / No / Cancel behavior on SHS close.

Uses the real PySide6 QMessageBox enum and the real production closeEvent
without constructing a full editor. This cannot run without PySide6 and is
required in the Windows CI test job, not just in a Linux code-only audit.
"""
import pytest
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QMessageBox
from studio.app import MainWindow


class CloseEvent:
    def __init__(self): self.accepted=None
    def accept(self): self.accepted=True
    def ignore(self): self.accepted=False


class UnsavedEditor:
    def __init__(self, path, backup_ok=True, dirty=True):
        self._dirty=dirty
        self.recovery_path=path
        self.backup_ok=backup_ok
        self.backup_calls=0
    def write_recovery(self):
        self.backup_calls+=1
        if self.backup_ok:
            self.recovery_path.write_text('recovery saved',encoding='utf8')
        return self.backup_ok


def close_with_choice(monkeypatch, fake, choice):
    messages=[]
    def question(_parent, title, message, buttons, default):
        assert title=='Unsaved changes'
        assert 'No: Close WITHOUT saving' in message
        assert buttons & QMessageBox.StandardButton.Yes
        assert buttons & QMessageBox.StandardButton.No
        assert buttons & QMessageBox.StandardButton.Cancel
        assert default==QMessageBox.StandardButton.Cancel
        return choice
    monkeypatch.setattr(QMessageBox,'question',question)
    monkeypatch.setattr(QMessageBox,'warning',lambda *args: messages.append(args))
    event=CloseEvent()
    MainWindow.closeEvent(fake,event)
    return event,messages


def test_no_exits_without_saving_and_deletes_old_autosave(tmp_path,monkeypatch):
    path=tmp_path/'recovery.json';path.write_text('outdated auto recovery')
    fake=UnsavedEditor(path)
    event,messages=close_with_choice(monkeypatch,fake,QMessageBox.StandardButton.No)
    assert event.accepted is True
    assert fake.backup_calls==0
    assert not path.exists()
    assert not messages


def test_cancel_stays_open_and_preserves_unsaved_recovery(tmp_path,monkeypatch):
    path=tmp_path/'recovery.json';path.write_text('existing recovery')
    fake=UnsavedEditor(path)
    event,messages=close_with_choice(monkeypatch,fake,QMessageBox.StandardButton.Cancel)
    assert event.accepted is False
    assert fake.backup_calls==0
    assert path.read_text()=='existing recovery'
    assert not messages


def test_yes_creates_recovery_and_closes(tmp_path,monkeypatch):
    path=tmp_path/'recovery.json'
    fake=UnsavedEditor(path)
    event,messages=close_with_choice(monkeypatch,fake,QMessageBox.StandardButton.Yes)
    assert event.accepted is True
    assert fake.backup_calls==1
    assert path.read_text()=='recovery saved'
    assert not messages


def test_yes_failed_recovery_blocks_close(tmp_path,monkeypatch):
    path=tmp_path/'recovery.json'
    fake=UnsavedEditor(path,backup_ok=False)
    event,messages=close_with_choice(monkeypatch,fake,QMessageBox.StandardButton.Yes)
    assert event.accepted is False
    assert fake.backup_calls==1
    assert not path.exists()
    assert len(messages)==1


def test_unrecognized_choice_safely_stays_open(tmp_path,monkeypatch):
    path=tmp_path/'recovery.json'
    fake=UnsavedEditor(path)
    event,messages=close_with_choice(monkeypatch,fake,QMessageBox.StandardButton.NoButton)
    assert event.accepted is False
    assert fake.backup_calls==0
    assert not messages


def test_no_failed_recovery_cleanup_blocks_close(tmp_path,monkeypatch):
    class FailingPath:
        def unlink(self,**kwargs): raise OSError('access denied')
    fake=UnsavedEditor(FailingPath())
    event,messages=close_with_choice(monkeypatch,fake,QMessageBox.StandardButton.No)
    assert event.accepted is False
    assert fake.backup_calls==0
    assert len(messages)==1


def test_clean_editor_closes_without_dialog(tmp_path,monkeypatch):
    fake=UnsavedEditor(tmp_path/'recovery.json',dirty=False)
    monkeypatch.setattr(QMessageBox,'question',lambda *args: pytest.fail('clean project should not ask'))
    event=CloseEvent()
    MainWindow.closeEvent(fake,event)
    assert event.accepted is True
    assert fake.backup_calls==0
