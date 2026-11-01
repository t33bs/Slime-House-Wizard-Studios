import json
import pytest
from studio.project_validation import validate_project_data, InvalidProjectDataError
from studio.pet_suite_model import PetSuiteModel


def valid():
    return {'size': [128,128], 'parts': [], 'animations': {'Walk': [[]]}, 'frame_durations': {'Walk':[125]}}


@pytest.mark.parametrize('change,reason', [
    (lambda d: d.update(size=[0,128]), 'canvas size'),
    (lambda d: d.update(parts='bad'), 'parts'),
    (lambda d: d.update(animations={'Walk':[{}]}), 'pose'),
    (lambda d: d.update(frame_durations={'Walk':[-1]}), 'duration'),
    (lambda d: d.update(animations={'Walk':[[{'x':0,'y':0,'width':1,'height':1}]]}), 'more parts'),
])
def test_rejects_corrupt_structure(change, reason):
    data=valid()
    change(data)
    with pytest.raises(InvalidProjectDataError, match=reason):
        validate_project_data(data)


def test_invalid_project_does_not_touch_existing_file(tmp_path):
    path=tmp_path/'creature.json'
    data=valid(); data['size']=[-2,128]
    path.write_text(json.dumps(data))
    before=path.read_bytes()
    with pytest.raises(InvalidProjectDataError):
        PetSuiteModel.load_project(path)
    assert path.read_bytes()==before


def test_valid_empty_project_loads(tmp_path):
    path=tmp_path/'creature.json'
    path.write_text(json.dumps(valid()))
    assert PetSuiteModel.load_project(path).size == (128,128)
