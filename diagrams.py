# The diagrams for the blog post.

import itertools

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

with cairo_context(600, 600, format="png", output="pix/repro_139.png") as context:
    Fluidity(
        LinearNoise(seed=139, istep=0.001, istart=0.07),
        npoints=10, nlines=40, curver=hobby_curve, sorter=HilbertSortEveryLine()
    ).draw_in_context(
        context,
        curve_color=(0, 0, 0, 0.3),
        curve_width=1.5,
    )

with cairo_context(400, 400, format="png", output="pix/point_motion.png") as context:
    f = Fluidity(LinearNoise(seed=7, istep=0.03), npoints=4, nlines=50)
    f.draw_in_context(context, curve_color=None, point_color=(1, 0, 0, 1), point_size=1.5)


SEEDS = [0, 5, 3]
for fname, sorter in [
    ("hobby_unsorted.png", None),
    ("hobby_sorted.png", HilbertSortEveryLine()),
]:
    fs = [
        Fluidity(LinearNoise(seed=seed), npoints=10, nlines=1, curver=hobby_curve, sorter=sorter)
        for seed in SEEDS
    ]
    with cairo_context(1200, 400, output=f"pix/{fname}") as ctx:
        for f, tctx in zip(fs, context_tiles(ctx, rows=1, cols=3)):
            f.draw_in_context(tctx, curve_width=1, point_color=(1, 0, 0, 1), point_size=4, line_color=(0, 1, 0, 1), line_width=1)


with cairo_context(800, 1200, output=f"pix/hilbert_compared.png") as ctx:
    # confusing: product is (rows, cols)
    seeds_sorters = itertools.product(SEEDS, [None, HilbertSortEveryLine()])
    for (seed, sorter), tctx in zip(seeds_sorters, context_tiles(ctx, rows=3, cols=2)):
        f = Fluidity(LinearNoise(seed=seed), npoints=10, nlines=1, curver=hobby_curve, sorter=sorter)
        f.draw_in_context(tctx, curve_width=1, point_color=(1, 0, 0, 1), point_size=4, line_color=(0, 1, 0, 1), line_width=1)
