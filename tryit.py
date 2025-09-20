from drawing import *
from fluidity import *

W = 600
FRAMES = 200
SEED = 9
NPOINTS = 8
NLINES = 30
ISTEP = 0.01


sorter = None
with Animation(size=(600, 600), output="fnew.gif") as anim:
    for i in range(FRAMES):
        if i > 0:
            anim.new_frame()
        f = Fluidity(
            CircularNoise(seed=SEED, isteps=FRAMES, istep=ISTEP, istart=i), 
            npoints=NPOINTS, nlines=NLINES, one_order=True, sorter=sorter, curve="cubic",
        )
        if i == 0:
            sorter = f.sorter
        f.draw_in_context(anim.context, (600, 600), point_color=(1, 0, 0, 1))
