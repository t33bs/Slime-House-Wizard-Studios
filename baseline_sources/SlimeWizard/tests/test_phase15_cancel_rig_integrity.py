from PIL import Image
import pytest
from studio.pet_suite_model import PetSuiteModel


def test_cancel_provisional_layer_removes_all_rig_metadata_and_keeps_sources():
    model = PetSuiteModel((32, 32))
    png = Image.new('RGBA', (4, 4), (255, 0, 0, 255))
    model.import_part('Source', png)
    model.import_part('Slimer Layer 001', png)
    model.set_anchor(1, 2, 3)
    model.rotate_part(1, 45)
    model.attach(1, 0)
    original = model.originals[0].tobytes()
    model.remove_unconfirmed_part(1)
    assert len(model.parts) == len(model.originals) == 1
    assert model.originals[0].tobytes() == original
    assert 1 not in model.anchors and 1 not in model.angles
    assert 1 not in model.attachments
    model.import_part('Slimer Layer 002', png)
    assert len(model.parts) == 2
    assert model.angles.get(1, 0) == 0
    assert 1 not in model.anchors and 1 not in model.attachments


def test_cancel_detaches_children_of_provisional_layer():
    model = PetSuiteModel((32, 32))
    png = Image.new('RGBA', (4, 4), (1, 2, 3, 255))
    model.import_part('Source', png)
    model.import_part('Provisional', png)
    model.attachments[0] = {'parent': 1, 'offset_x': 0, 'offset_y': 0}
    model.remove_unconfirmed_part(1)
    assert model.attachments == {}


def test_cancel_refuses_index_shift_without_mutation():
    model = PetSuiteModel((32, 32))
    png = Image.new('RGBA', (2, 2), (1, 2, 3, 255))
    for name in ('Original', 'Staged', 'Later'):
        model.import_part(name, png)
    with pytest.raises(ValueError):
        model.remove_unconfirmed_part(1)
    assert [p['name'] for p in model.parts] == ['Original', 'Staged', 'Later']
