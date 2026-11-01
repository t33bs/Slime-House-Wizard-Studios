"""Pixel-coordinate canvas navigation, independent of Qt."""
def geometry(view_w,view_h,image_w,image_h,zoom=1.0,pan_x=0.0,pan_y=0.0):
    if min(view_w,view_h,image_w,image_h)<=0:raise ValueError('Dimensions must be positive')
    if zoom<=0:raise ValueError('Zoom must be positive')
    scale=min(view_w/image_w,view_h/image_h,max(180,view_h-12)/max(image_w,image_h),540/max(image_w,image_h))*zoom
    return scale,(view_w-image_w*scale)/2+pan_x,(view_h-image_h*scale)/2+pan_y

def zoom_at(view_w,view_h,image_w,image_h,zoom,pan_x,pan_y,x,y,steps):
    old,ox,oy=geometry(view_w,view_h,image_w,image_h,zoom,pan_x,pan_y)
    ix,iy=(x-ox)/old,(y-oy)/old
    updated=max(.25,min(8.0,zoom*1.2**steps))
    new,nx,ny=geometry(view_w,view_h,image_w,image_h,updated,pan_x,pan_y)
    return updated,pan_x+x-(nx+ix*new),pan_y+y-(ny+iy*new)
