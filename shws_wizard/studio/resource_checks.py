"""Offline checks for retained editor resources; no generated recipe assets."""

def bundled_resource_report():
    from .animation_registry import LEGACY_ANIMATION_NAMES
    from .slime_buddy import STATIONS, station_guide
    problems = []
    if not LEGACY_ANIMATION_NAMES:
        problems.append('Animation name registry is missing')
    if not STATIONS:
        problems.append('Slime Buddy stations are missing')
    for name in STATIONS:
        try:
            if not station_guide(name):
                problems.append(f'Empty Slime Buddy guidance: {name}')
        except Exception as exc:
            problems.append(f'Slime Buddy station {name}: {exc}')
    return problems
