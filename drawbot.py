import sys
sys.path.extend([
    '/Users/ned/art/fluidity',
    '/usr/local/pyenv/pyenv/versions/3.12.11/lib/python312.zip',
    '/usr/local/pyenv/pyenv/versions/3.12.11/lib/python3.12',
    '/usr/local/pyenv/pyenv/versions/3.12.11/lib/python3.12/lib-dynload',
    '/Users/ned/art/fluidity/.venv/lib/python3.12/site-packages',
])

if "fluidity" in sys.modules:
    del sys.modules["fluidity"]

from fluidity import *

def draw_dlist(dlist):
    newPath()
    for entry in dlist:
        match entry:
            case ["move_to", x, y]:
                moveTo((x, y))
            case ["curve_to", a, b, c, d, e, f]:
                curveTo((a, b), (c, d), (e, f))

def draw_dlists(dlists):
    for dlist in dlists:
        draw_dlist(dlist)
        drawPath()
