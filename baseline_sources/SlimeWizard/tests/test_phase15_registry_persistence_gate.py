"""Recipe-free selector regression: reopened projects and current unsaved names."""
from pathlib import Path
from tempfile import TemporaryDirectory

from studio.animation_registry import available_animation_names, preferred_animation
from studio.pet_suite_model import PetSuiteModel


def test_reopened_custom_and_legacy_names_remain_selectable_without_mutation():
    model = PetSuiteModel((16, 16))
    model.save_frame('Pooping')
    model.save_frame('A unique creature animation')
    with TemporaryDirectory() as folder:
        path = Path(folder) / 'creature.json'
        model.save_project(path)
        restored = PetSuiteModel.load_project(path)
        before = restored.content_fingerprint()
        names = available_animation_names(restored)
        assert names.count('Pooping') == 1
        assert names.count('A unique creature animation') == 1
        assert preferred_animation(restored, 'A unique creature animation') == 'A unique creature animation'
        assert restored.content_fingerprint() == before
        assert PetSuiteModel.load_project(path).content_fingerprint() == before


def test_unsaved_current_name_is_selectable_without_creating_frames():
    class Model:
        animations = {'Walking': []}
        current = 'An unsaved custom animation'
    model = Model()
    assert preferred_animation(model) == 'An unsaved custom animation'
    assert available_animation_names(model).count('Walking') == 1
    assert model.animations == {'Walking': []}
