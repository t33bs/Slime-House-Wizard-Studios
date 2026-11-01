"""Pure helpers for timeline timing and non-destructive onion-skin previews."""
from PIL import Image

def timeline_summary(durations):
    values=[int(v) for v in durations]
    if any(v<=0 for v in values):
        raise ValueError("Frame durations must be positive")
    total=sum(values)
    return {"frames":len(values),"milliseconds":total,"seconds":total/1000,"fps_equivalent":(1000*len(values)/total if total else 0)}

def onion_composite(current, previous=None, following=None, opacity=0.3):
    """Ghost neighboring frames beneath current without mutating originals."""
    if not 0<=opacity<=1:raise ValueError("Opacity must be between 0 and 1")
    output=Image.new("RGBA",current.size,(0,0,0,0))
    for image in (previous,following):
        if image is None:continue
        if image.size!=current.size:raise ValueError("Neighbor frame size mismatch")
        ghost=image.convert("RGBA").copy()
        ghost.putalpha(ghost.getchannel("A").point(lambda a:round(a*opacity)))
        output.alpha_composite(ghost)
    output.alpha_composite(current.convert("RGBA"))
    return output
