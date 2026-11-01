"""Pure geometry helpers for restoring a window on changed display configurations."""

def fit_window_rect(rect, screens, min_width=480, min_height=360):
    """Fit a normal window within one available monitor without losing title bar.

    Coordinates can be negative for monitors to the left of the primary.
    Maximized state is handled by the GUI caller.
    """
    x,y,w,h=map(int,rect)
    candidates=[tuple(map(int,s)) for s in screens if s[2]>0 and s[3]>0]
    if not candidates:return (x,y,max(1,w),max(1,h))
    def overlap(s):
        sx,sy,sw,sh=s
        return max(0,min(x+w,sx+sw)-max(x,sx))*max(0,min(y+h,sy+sh)-max(y,sy))
    target=max(candidates,key=overlap)
    if overlap(target)==0:
        target=candidates[0]
    sx,sy,sw,sh=target
    w=min(max(min_width,w),sw)
    h=min(max(min_height,h),sh)
    x=min(max(x,sx),sx+sw-w)
    y=min(max(y,sy),sy+sh-h)
    return (x,y,w,h)
