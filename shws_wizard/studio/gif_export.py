"""Deterministic GIF export: shared palette, explicit transparency and timing."""
from PIL import Image


def encode_gif(frames, durations, output):
    if not frames or len(frames) != len(durations):
        raise ValueError('GIF export needs matching frames and durations.')
    frames = [frame.convert('RGBA') for frame in frames]
    if any(frame.size != frames[0].size for frame in frames):
        raise ValueError('GIF frames must have the same canvas size.')
    if any(not isinstance(d, (int, float)) or d <= 0 for d in durations):
        raise ValueError('GIF frame durations must be positive.')
    # Build a shared palette from all opaque colors, avoiding per-frame palette drift.
    w, h = frames[0].size
    sample = Image.new('RGB', (w, h * len(frames)), (0, 0, 0))
    for i, frame in enumerate(frames):
        background = Image.new('RGB', frame.size, (0, 0, 0))
        background.paste(frame, mask=frame.getchannel('A'))
        sample.paste(background, (0, i * h))
    palette_source = sample.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    palette = palette_source.getpalette()[:255 * 3] + [0, 0, 0]
    encoded = []
    for frame in frames:
        background = Image.new('RGB', frame.size, (0, 0, 0))
        background.paste(frame, mask=frame.getchannel('A'))
        indexed = background.quantize(palette=palette_source, dither=Image.Dither.NONE)
        indexed.putpalette(palette)
        alpha = frame.getchannel('A').point(lambda a: 255 if a < 128 else 0)
        indexed.paste(255, mask=alpha)
        indexed.info['transparency'] = 255
        encoded.append(indexed)
    # GIF can only represent multiples of 10 ms; round, never drop below 10 ms.
    centiseconds = [max(1, round(float(d) / 10)) * 10 for d in durations]
    encoded[0].save(output, save_all=True, append_images=encoded[1:],
                    duration=centiseconds, loop=0, disposal=2,
                    optimize=False, transparency=255)
    return output
