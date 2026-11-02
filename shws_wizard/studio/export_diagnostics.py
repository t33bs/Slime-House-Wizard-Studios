"""Optional non-destructive technical diagnostics for exported sprite poses.

An isolated cluster may be intentional (sparkles, particles, stray sword etc).
Never change pixels, block an export, or judge character anatomy/design.
"""

def detached_pixel_clusters(image, min_pixels=4, max_pixels=32):
    """Return small 8-connected islands detached from a dominant sprite.

    Each result has a count and inclusive pixel-space bounds (x0,y0,x1,y1).
    Ignoring components smaller than 4 avoids noisy single-pixel warnings.
    """
    alpha = image.convert('RGBA').getchannel('A')
    width, height = alpha.size
    pixels = alpha.load()
    seen = set()
    components = []
    for y in range(height):
        for x in range(width):
            if pixels[x, y] == 0 or (x, y) in seen:
                continue
            pending = [(x, y)]
            seen.add((x, y))
            count = 0
            x0=x1=x; y0=y1=y
            while pending:
                px,py=pending.pop()
                count += 1
                x0=min(x0,px);x1=max(x1,px)
                y0=min(y0,py);y1=max(y1,py)
                for ny in (py-1,py,py+1):
                    for nx in (px-1,px,px+1):
                        if not (0<=nx<width and 0<=ny<height):
                            continue
                        if (nx,ny) in seen or pixels[nx,ny]==0:
                            continue
                        seen.add((nx,ny));pending.append((nx,ny))
            components.append((count,(x0,y0,x1,y1)))
    if len(components)<2:
        return []
    largest = max(count for count,_ in components)
    if largest < 100:
        return []  # no clear dominant sprite; do not guess about small art
    return [dict(pixels=count, bounds=bounds) for count,bounds in components
            if min_pixels <= count <= max_pixels and count != largest]
