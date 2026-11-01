"""Animation selector labels independent of obsolete pose recipes.

Legacy labels are kept only as names so existing projects can still select them;
no example frames, motion steps or creature design rules are generated here.
"""
LEGACY_ANIMATION_NAMES = (
    'Idle / Breathing', 'Walking', 'Sleeping', 'Eating',
    'Happy / Celebrating', 'Grooming', 'Flying / Hovering', 'Custom',
    'Sitting Down', 'Yawning', 'Drinking', 'Stretching',
    'Curious Head Tilt', 'Hopping', 'Being Petted', 'Confused',
    'Excited', 'Sad / Lonely', 'Angry / Pouting', 'Shy / Blushing',
    'Startled', 'Bored', 'Affectionate', 'Running', 'Turning Around',
    'Sniffing', 'Looking Around', 'Getting Picked Up', 'Waving Hello',
    'Falling Asleep', 'Pooping',
)

def available_animation_names(model):
    """Include saved user-defined animation names without altering project data."""
    names = list(LEGACY_ANIMATION_NAMES)
    for name in (getattr(model, 'animations', {}) or {}):
        if name and name not in names:
            names.append(name)
    current = getattr(model, 'current', '')
    if current and current not in names:
        names.append(current)
    return names

def preferred_animation(model, requested=None):
    names = available_animation_names(model)
    if requested in names:
        return requested
    current = getattr(model, 'current', '')
    return current if current in names else names[0]
