"""Project-scoped tab identities. Keeps different creatures' timelines independent."""

def animation_key(project_id, animation):
    if not isinstance(project_id, int) or project_id < 0: raise ValueError('Invalid project')
    if not isinstance(animation,str) or not animation: raise ValueError('Invalid animation')
    return ('animation', f'{project_id}::{animation}')

def parse_animation_key(key):
    kind, name=key
    if kind!='animation' or '::' not in name: raise ValueError('Not a scoped animation tab')
    pid, animation=name.split('::',1)
    if not pid.isdigit() or not animation: raise ValueError('Invalid scoped animation tab')
    return int(pid),animation

def belongs_to_project(key,project_id):
    try:return parse_animation_key(key)[0]==project_id
    except (ValueError,TypeError):return False
