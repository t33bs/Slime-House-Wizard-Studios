"""Registry must remain deterministic and read-only after recipe removal."""
from studio.animation_registry import (
    LEGACY_ANIMATION_NAMES, available_animation_names, preferred_animation,
)
from studio.pet_suite_model import PetSuiteModel


def test_registry_keeps_historical_names_in_order_and_appends_custom_names_once():
    model = PetSuiteModel((16, 16))
    model.animations = {
        'My creature rolls': [], 'Walking': [], 'My creature dances': [],
    }
    model.current = 'My unsaved creature pose'
    before = model.content_fingerprint()
    first = available_animation_names(model)
    assert first[:len(LEGACY_ANIMATION_NAMES)] == list(LEGACY_ANIMATION_NAMES)
    assert first[-3:] == ['My creature rolls', 'My creature dances', 'My unsaved creature pose']
    assert len(first) == len(set(first))
    for _ in range(20):
        assert available_animation_names(model) == first
        assert preferred_animation(model, 'Walking') == 'Walking'
        assert preferred_animation(model, 'missing') == 'My unsaved creature pose'
    assert model.content_fingerprint() == before


def test_unknown_requested_animation_falls_back_to_current_project_not_other_project():
    first = PetSuiteModel((16, 16))
    second = PetSuiteModel((16, 16))
    first.current = 'Creature A dance'
    second.current = 'Creature B dance'
    first.animations = {'Creature A dance': []}
    second.animations = {'Creature B dance': []}
    assert preferred_animation(second, 'Creature A dance') == 'Creature B dance'
    assert 'Creature A dance' not in available_animation_names(second)
    assert preferred_animation(first, 'Creature B dance') == 'Creature A dance'
