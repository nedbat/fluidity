# The diagrams for the blog post.

from drawing import *
from fluidity import *

if 0:
    for seed in range(100):
        with cairo_context(600, 600, format="png", output=f"repro/{seed:02d}.png") as context:
            Fluidity(
                LinearNoise(seed=seed+100, istep=0.001, istart=0.07),
                npoints=10, nlines=40, curver=hobby_curve, sorter=HilbertSortEveryLine()
            ).draw_in_context(
                context,
                curve_color=(0, 0, 0, 0.3),
                curve_width=1.5,
            )

with cairo_context(600, 600, format="png", output=f"pix/repro_139.png") as context:
    Fluidity(
        LinearNoise(seed=139, istep=0.001, istart=0.07),
        npoints=10, nlines=40, curver=hobby_curve, sorter=HilbertSortEveryLine()
    ).draw_in_context(
        context,
        curve_color=(0, 0, 0, 0.3),
        curve_width=1.5,
    )

with cairo_context(400, 400, format="png", output=f"pix/point_motion.png") as context:
    f = Fluidity(LinearNoise(seed=7, istep=0.03), npoints=4, nlines=50)
    f.draw_in_context(context, curve_color=None, point_color=(1, 0, 0, 1), point_size=1.5)
