from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1].joinpath("friendly_animator.py").read_text()


def test_place_frame_does_not_commit_slimer_move():
    body = SOURCE.split("    def slimer_place_frame(self):", 1)[1].split("    def remember(self):", 1)[0]
    assert "self._slimer_commit(True)" not in body
    assert "self.model.insert_frame(name, self.frame + 1, source_pose)" in body
    assert "self._slimer_pending_layer is not None" in body
    assert '\n        self.preserve_pose_draft()' not in body  # Save-as-next must not overwrite current pose
