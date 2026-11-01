"""Static safety contracts for the Phase 15 editor workflow."""
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text(encoding='utf-8')


def test_sequential_apply_and_explicit_frame_insertion_are_separate_actions():
    assert 'def slimer_apply_move_to_pose(self):' in SOURCE
    assert 'self._slimer_pending_layer=None' in SOURCE
    assert 'def slimer_create_editable_layer(self):' in SOURCE
    assert 'self._slimer_erase_original_layers(self._slimer_pending_mask)' in SOURCE
    assert 'def slimer_place_frame(self):' in SOURCE
    assert 'self.model.insert_frame(name,self.frame+1)' in SOURCE


def test_legacy_recipe_and_multitab_controls_are_not_visible():
    assert 'self.slimer_phase_picker.hide()' in SOURCE
    assert 'self.recipe_toggle' not in SOURCE
    assert 'self.steps' not in SOURCE
    assert 'self.instruction' not in SOURCE
    assert 'self.slimer_confirm_all.hide()' in SOURCE


def test_pose_visibility_actions_exist_without_global_deletion():
    assert 'def remove_asset_from_current_pose(self):' in SOURCE
    assert 'def restore_asset_in_current_pose(self):' in SOURCE
    assert 'self.model.save_pose_at(name,self.frame)' in SOURCE
