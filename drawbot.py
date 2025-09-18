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
            case ["close_path"]:
                closePath()

def draw_dlists(dlists):
    for dlist in dlists:
        draw_dlist(dlist)
        drawPath()



size(W, W)

def start_page():
    fill(0)
    stroke(None)
    rect(0, 0, width(), height())
    translate(W/2, W/2)
    scale(W/2, W/2)
    fill(None)
    stroke(1, 1, 1, 0.5)
    strokeWidth(4/W)


sorter = None
for i in range(FRAMES):
    ii = 0.01
    if i > 0:
        newPage()
    #f = Fluidity(LinearNoise(seed=55, istep=ii, istart=ii*i), npoints=15, nlines=10, one_order=True, sorter=sorter)
    f = Fluidity(CircularNoise(seed=SEED, isteps=FRAMES, istep=ii, istart=i), npoints=NPOINTS, nlines=NLINES, one_order=True, sorter=sorter)
    if i == 0:
        sorter = f.sorter
    start_page()
    draw_dlists(f.dlists())

saveImage("f.gif", imageGIFLoop=True)

# the svg's don't seem to close the curve path properly?
# saveImage("f.svg", multipage=True)
