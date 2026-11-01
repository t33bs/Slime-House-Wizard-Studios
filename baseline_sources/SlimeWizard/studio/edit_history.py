"""Bounded, per-project undo/redo of complete editable creature state."""
from copy import deepcopy


def capture(model):
    """Capture all editable state, including pixel sources and layer order."""
    return deepcopy({
        'size': model.size, 'parts': model.parts, 'originals': model.originals,
        'animations': model.animations, 'current': model.current,
        'frame_durations': model.frame_durations, 'pose_ids': model.pose_ids,
        'pose_recovery': model.pose_recovery, 'anchors': model.anchors,
        'angles': model.angles, 'attachments': model.attachments,
    })


def restore(model, state):
    for key, value in state.items():
        setattr(model, key, deepcopy(value))


class EditHistory:
    def __init__(self, limit=100):
        self.limit = limit
        self.past = []
        self.future = []

    def record(self, model):
        self.past.append(capture(model))
        del self.past[:-self.limit]
        self.future.clear()

    def undo(self, model):
        if not self.past:
            return False
        self.future.append(capture(model))
        restore(model, self.past.pop())
        return True

    def redo(self, model):
        if not self.future:
            return False
        self.past.append(capture(model))
        restore(model, self.future.pop())
        return True
