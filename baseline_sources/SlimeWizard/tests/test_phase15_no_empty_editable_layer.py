from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / "friendly_animator.py").read_text()

def test_finish_selecting_widget_is_removed():
    assert "self.slimer_finish=QPushButton" not in SOURCE
    assert "self.slimer_edit_asset.clicked.connect(self.slimer_create_editable_layer)" in SOURCE

def test_empty_transparent_selection_does_not_create_a_layer():
    create = SOURCE.split("def slimer_create_editable_layer(self):", 1)[1].split("def slimer_apply_move_to_pose(self):", 1)[0]
    assert "if isolated.getchannel('A').getbbox() is None:" in create
    assert create.index("if isolated.getchannel('A').getbbox() is None:") < create.index("self.model.import_part(")
