from drawing import *
from fluidity import *

for seed in range(100):
    with cairo_context(600, 600, format="png", output=f"repro/{seed:02d}.png") as context:
        Fluidity(
            LinearNoise(seed=seed, istep=0.001, istart=0.07),
            npoints=10, nlines=40, curver=hobby_curve, sorter=HilbertSortEveryLine()
        ).draw_in_context(
            context,
            size=(600, 600),
            curve_color=(0, 0, 0, 0.3),
            curve_size=1,
        )
