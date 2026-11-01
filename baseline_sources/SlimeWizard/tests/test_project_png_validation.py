import json
import pytest
from PIL import Image
from studio.pet_suite_model import PetSuiteModel
from studio.project_png_validation import InvalidProjectArtworkError


def project_with_png(tmp_path, contents=None):
    path = tmp_path / 'cat.json'
    folder = tmp_path / 'cat'
    folder.mkdir()
    artwork = folder / 'part_000.png'
    if contents is None:
        Image.new('RGBA', (4, 4), (0, 255, 0, 128)).save(artwork)
    else:
        artwork.write_bytes(contents)
    path.write_text(json.dumps({'size': [128, 128], 'parts': [
        {'name': 'cat', 'x': 0, 'y': 0, 'width': 4, 'height': 4}]}))
    return path, artwork


@pytest.mark.parametrize('bad', [b'not a png', b'\x89PNG\r\n\x1a\n', b''])
def test_damaged_png_rejected_without_changes(tmp_path, bad):
    path, artwork = project_with_png(tmp_path, bad)
    before = (path.read_bytes(), artwork.read_bytes())
    with pytest.raises(InvalidProjectArtworkError, match='artwork part_000.png'):
        PetSuiteModel.load_project(path)
    assert (path.read_bytes(), artwork.read_bytes()) == before


def test_valid_png_still_loads(tmp_path):
    path, _ = project_with_png(tmp_path)
    assert len(PetSuiteModel.load_project(path).originals) == 1


def test_png_with_wrong_extension_contents_rejected(tmp_path):
    path, artwork = project_with_png(tmp_path)
    Image.new('RGB', (4, 4)).save(artwork, format='JPEG')
    with pytest.raises(InvalidProjectArtworkError, match='not a readable PNG'):
        PetSuiteModel.load_project(path)
