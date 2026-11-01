"""Lossless RGBA APNG encoding, independent of the editable source frames."""
from pathlib import Path
from PIL import Image

def encode_apng(frames, durations, output, loop=0):
    if not frames or len(frames) != len(durations):
        raise ValueError("APNG requires a duration for every frame.")
    size = frames[0].size
    if any(frame.size != size for frame in frames):
        raise ValueError("All APNG frames must have the same canvas size.")
    if any(int(duration) <= 0 for duration in durations):
        raise ValueError("APNG frame durations must be positive.")
    if int(loop) < 0:
        raise ValueError("APNG loop count cannot be negative.")
    copies = [frame.convert("RGBA").copy() for frame in frames]
    output = Path(output)
    copies[0].save(output, format="PNG", save_all=True,
                   append_images=copies[1:], duration=[int(x) for x in durations],
                   loop=int(loop), disposal=2, blend=0)
    return output
