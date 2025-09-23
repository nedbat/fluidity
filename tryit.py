from drawing import *
from fluidity import *

W = 600
FRAMES = 200
SEED = 9
NPOINTS = 8
NLINES = 30
ISTEP = 0.01


for fname, sorter, curver in [
    ("fnew.gif", HilbertSortFirstLine(), cubic_curve),
    ("fhobby.gif", HilbertSortFirstLine(), hobby_curve),
    ("funsort.gif", None, cubic_curve),
    ("fevery.gif", HilbertSortEveryLine(), cubic_curve),
]:
    with Animation(size=(600, 600), output=fname) as anim:
        for i in range(FRAMES):
            if i > 0:
                anim.new_frame()
            f = Fluidity(
                CircularNoise(seed=SEED, isteps=FRAMES, istep=ISTEP, istart=i), 
                npoints=NPOINTS, nlines=NLINES, sorter=sorter, curver=curver,
            )
            f.draw_in_context(anim.context, (600, 600), point_color=(1, 0, 0, 1))
