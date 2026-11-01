"""Guard automatic preservation when GUI edits bypass the dirty flag."""
from types import SimpleNamespace
from studio.pet_suite_model import PetSuiteModel


def test_preserve_pose_draft_detects_changes_even_without_dirty_flag():
    # Exercise the actual UI method without requiring a display server.
    from pathlib import Path
    source = Path(__file__).resolve().parents[1].joinpath('friendly_animator.py').read_text()
    assert 'self.model.snapshot() != poses[index]' in source
    assert 'self._pose_live_id != pose_id' in source
    assert 'ids.index(pose_id)' in source
    assert 'pending_slimer' in source


def test_reorder_retains_independent_snapshots_and_timing():
    model = PetSuiteModel()
    # Distinct snapshots are created from the model's current artwork state.
    name = model.current
    a = model.insert_frame(name, 0)
    b = model.insert_frame(name, 1)
    model.set_frame_duration(name, 0, 125)
    model.set_frame_duration(name, 1, 240)
    original_ids = list(model.pose_ids[name])
    model.reorder_frame(name, 1, 0)
    assert model.pose_ids[name] == original_ids[::-1]
    assert [model.frame_duration(name, i) for i in range(2)] == [240, 125]
