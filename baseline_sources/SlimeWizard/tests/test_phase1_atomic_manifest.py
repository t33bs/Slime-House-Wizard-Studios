import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from studio.pet_suite_model import PetSuiteModel


def test_failed_manifest_replace_keeps_previous_project_readable():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'creature.json'
        model = PetSuiteModel((128, 128))
        model.save_project(path)
        original = path.read_bytes()
        with patch('studio.pet_suite_model.os.replace', side_effect=OSError('simulated write failure')):
            with pytest.raises(OSError, match='simulated write failure'):
                model.save_project(path)
        assert path.read_bytes() == original
        assert not list(Path(directory).glob('.creature.json.*.tmp'))
        assert PetSuiteModel.load_project(path).size == (128, 128)
