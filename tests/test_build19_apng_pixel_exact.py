"""Regression for nine-frame APNG corruption; no Swordcat art redistributed."""
from pathlib import Path
from PIL import Image
import pytest

from shws_wizard.studio.apng_export import encode_apng
from shws_wizard.studio.export_diagnostics import detached_pixel_clusters


def nine_frames():
    frames=[]
    for i in range(9):
        frame=Image.new('RGBA',(128,128),(0,0,0,0))
        # First two are identical, like the real nine-frame user animation.
        j=max(0, i-1)
        for y in range(20,72):
            for x in range(24,78):
                frame.putpixel((x,y),(90+(j*9),36+(x%22),210-(y%41),100+(x%150)))
        for x in range(30,78):
            frame.putpixel((x,90+j),(45,5,8,255))
        frames.append(frame)
    return frames


def assert_apng_matches(path, frames, durations):
    with Image.open(path) as decoded:
        assert decoded.is_animated
        assert decoded.n_frames==len(frames)
        assert decoded.info['loop']==0
        for i, expected in enumerate(frames):
            decoded.seek(i)
            assert decoded.convert('RGBA').tobytes()==expected.tobytes(), f'APNG frame {i+1} changed'
            assert abs(decoded.info['duration']-durations[i])<=1


def test_nine_full_frames_survive_export_with_duplicate_first_pair(tmp_path):
    frames=nine_frames(); durations=[125]*9
    original=[f.tobytes() for f in frames]
    output=tmp_path/'walk.png'
    encode_apng(frames,durations,output)
    assert_apng_matches(output,frames,durations)
    assert [f.tobytes() for f in frames]==original


def test_no_corrupt_replacement_when_decode_validation_fails(tmp_path,monkeypatch):
    from shws_wizard.studio import apng_export
    output=tmp_path/'walk.png';output.write_bytes(b'existing-good-previous-export')
    def bogus_save(self, file, *args, **kwargs):
        Path(file).write_bytes(b'invalid apng')
    monkeypatch.setattr(apng_export.Image.Image,'save',bogus_save)
    with pytest.raises(Exception):
        encode_apng(nine_frames(),[125]*9,output)
    assert output.read_bytes()==b'existing-good-previous-export'
    assert list(tmp_path.glob('.*-apng-*.png'))==[]


def test_detect_stray_horizontal_line_without_editing_artwork():
    frame=Image.new('RGBA',(128,128),(0,0,0,0))
    for x in range(35,80):
        for y in range(20,100):frame.putpixel((x,y),(20,20,20,255))
    for x in range(49,59):frame.putpixel((x,118),(10,10,10,255))
    original=frame.tobytes()
    result=detached_pixel_clusters(frame)
    assert dict(pixels=10,bounds=(49,118,58,118)) in result
    assert frame.tobytes()==original


def test_no_warning_for_single_contiguous_character():
    frame=Image.new('RGBA',(128,128),(0,0,0,0))
    for x in range(20,85):
        for y in range(20,99):frame.putpixel((x,y),(35,36,37,190))
    assert detached_pixel_clusters(frame)==[]
