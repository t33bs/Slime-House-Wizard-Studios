"""Non-judgmental animation readiness checks; never inspect aesthetic choices."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Check:
    severity: str
    message: str
    action: str

def check_animation(model, animation):
    """Report only objectively actionable data/export concerns; do not mutate model."""
    issues = []
    if not model.parts:
        issues.append(Check('warning', 'No PNG parts are loaded.', 'Import PNG artwork before exporting.'))
    poses = model.animations.get(animation, [])
    if not poses:
        issues.append(Check('warning', 'This animation has no saved poses.', 'Choose Add pose or Save / replace this frame.'))
        return issues
    for i, pose in enumerate(poses, 1):
        if not isinstance(pose, list):
            issues.append(Check('error', f'Pose {i} has unreadable frame data.', 'Recreate this pose from a working one.'))
        elif len(pose) != len(model.parts):
            issues.append(Check('warning', f'Pose {i} has {len(pose)} parts, but the creature has {len(model.parts)}.', 'Review this pose after adding or removing parts.'))
    times = model.frame_durations.get(animation, [])
    if len(times) != len(poses):
        issues.append(Check('info', 'Some poses use default timing.', 'Open the timeline to review frame durations.'))
    for i, value in enumerate(times[:len(poses)], 1):
        if not isinstance(value, (int,float)) or not 40 <= value <= 2000:
            issues.append(Check('warning', f'Pose {i} has timing outside the editor range.', 'Set its duration between 40 and 2000 ms.'))
    return issues
