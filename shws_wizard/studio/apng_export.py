"""Atomic, verified RGBA APNG encoding for independently editable poses.

Frames are always full-canvas replacements. Previous-frame disposal (2)
corrupted a 9-pose Swordcat sequence even though Pillow decoded the first
2 frames correctly. Background disposal (1) plus source blend (0) preserves
all pixels in every independent frame, including the alpha channel.
"""
import os
from pathlib import Path
import tempfile
from PIL import Image


def encode_apng(frames, durations, output, loop=0):
    if not frames or len(frames) != len(durations):
        raise ValueError('APNG requires a duration for every frame.')
    size = frames[0].size
    if any(frame.size != size for frame in frames):
        raise ValueError('All APNG frames must have the same canvas size.')
    if any(not isinstance(d, (int, float)) or int(d) <= 0 for d in durations):
        raise ValueError('APNG frame durations must be positive.')
    if int(loop) < 0:
        raise ValueError('APNG loop count cannot be negative.')
    copies = [frame.convert('RGBA').copy() for frame in frames]
    lengths = [int(d) for d in durations]
    output = Path(output)
    # Never overwrite the previous valid export until the new file has been
    # decoded and pixel-checked, including every individual alpha channel.
    fd, temporary = tempfile.mkstemp(prefix=f'.{output.stem}-apng-', suffix='.png', dir=output.parent)
    os.close(fd)
    try:
        copies[0].save(temporary, format='PNG', save_all=True,
                       append_images=copies[1:], duration=lengths,
                       loop=int(loop), disposal=1, blend=0)
        with Image.open(temporary) as decoded:
            if not decoded.is_animated or decoded.n_frames != len(copies):
                raise ValueError(f'APNG verification failed: expected {len(copies)} frames, got {decoded.n_frames}.')
            if int(decoded.info.get('loop', -1)) != int(loop):
                raise ValueError('APNG loop count did not survive export.')
            for index, (expected, duration) in enumerate(zip(copies, lengths)):
                decoded.seek(index)
                if decoded.convert('RGBA').tobytes() != expected.tobytes():
                    raise ValueError(f'APNG verification failed: frame {index+1} lost or changed RGBA pixels.')
                # APNG stores integer fractions; decoder can round at most 1 ms.
                if abs(float(decoded.info.get('duration', 0)) - duration) > 1:
                    raise ValueError(f'APNG verification failed: duration changed in frame {index+1}.')
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return output
