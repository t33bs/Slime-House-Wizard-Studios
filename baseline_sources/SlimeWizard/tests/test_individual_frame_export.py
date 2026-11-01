import json
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def test_export_individual_frames_preserves_pixels_timing_and_unique_names(tmp_path):
    model = PetSuiteModel(size=(8, 8))
    model.import_part('base', Image.new('RGBA', (8, 8), (1, 2, 3, 255)))
    for animation, color in [('Walk / Left', (255, 0, 0, 120)), ('Walk ? Left', (0, 0, 255, 90))]:
        index = model.insert_frame(animation, 0)
        image = Image.new('RGBA', (8, 8))
        image.putpixel((2, 3), color)
        model.replace_frame_image(animation, index, image)
        model.set_frame_duration(animation, index, 175)
    before = model.content_fingerprint()
    paths, metadata = model.export_individual_frames(tmp_path, 'my_cat')
    assert len(paths) == 2
    assert len({p.name.casefold() for p in paths}) == 2
    data = json.loads(metadata.read_text())
    assert [frame['duration_ms'] for frame in data['frames']] == [175, 175]
    assert [frame['animation'] for frame in data['frames']] == ['Walk / Left', 'Walk ? Left']
    for path, color in zip(paths, [(255, 0, 0, 120), (0, 0, 255, 90)]):
        with Image.open(path) as frame:
            assert frame.mode == 'RGBA'
            assert frame.getpixel((2, 3)) == color
    assert model.content_fingerprint() == before


def test_export_individual_frames_requires_saved_poses(tmp_path):
    model = PetSuiteModel(size=(8, 8))
    try:
        model.export_individual_frames(tmp_path)
    except ValueError:
        pass
    else:
        raise AssertionError('Empty timeline should not export')
    assert list(tmp_path.iterdir()) == []
