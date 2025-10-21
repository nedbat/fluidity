from drawing import *
from fluidity import *

for fname, sorter, curver in [
    ("linear_hobby.gif", HilbertSortFirstLine(), hobby_curve),
    ("linear_cubic.gif", HilbertSortFirstLine(), cubic_curve),
]:
    with Animation(size=(600, 600), output=f"pix/{fname}") as anim:
        for i in range(100):
            if i > 0:
                anim.new_frame()
            f = Fluidity(
                LinearNoise(seed=139, istep=0.005, istart=i * 0.005),
                npoints=7, nlines=40, curver=curver, sorter=sorter,
            )
            f.draw_in_context(
                anim.context,
                curve_color=(0, 0, 0, 0.3),
                curve_width=1,
            )

W = 600
with cairo_context(W * 2, W * 3, output="pix/hobby_vs_cubic.png") as ctx:
    tiles = context_tiles(ctx, rows=3, cols=2)
    for seed in [2, 3, 4]:
        for curver in [hobby_curve, cubic_curve]:
            f = Fluidity(LinearNoise(seed=seed, istep=0.003), npoints=10, nlines=1, curver=curver, sorter=HilbertSortFirstLine())
            f.draw_in_context(next(tiles), curve_width=2, curve_color=(0, 0, 0, 0.3), point_color=(1, 0, 0, 1), point_size=4)


colors = [(1, 0, 0, 1), (0, .85, 0, 1), (.25, .25, 1, 1)]
with cairo_context(W * 2, W, output="pix/point_trails.png") as ctx:
    tiles = context_tiles(ctx, rows=1, cols=2)
    f = Fluidity(LinearNoise(seed=15, istep=0.02), npoints=3, nlines=150)
    f.draw_in_context(next(tiles), curve_color=None, point_colors=colors, point_size=3)

    f = Fluidity(CircularNoise(seed=26, istep=0.02, isteps=120), npoints=3, nlines=120)
    f.draw_in_context(next(tiles), curve_color=None, point_colors=colors, point_size=3)


for seed in [5, 9, 25]:
    with Animation(size=(W, W), output=f"pix/circular_{seed}.gif") as anim:
        sorter = HilbertSortFirstLine()
        for i in range(100):
            if i > 0:
                anim.new_frame()
            f = Fluidity(
                CircularNoise(seed=seed, istep=0.01, isteps=100, istart=i),
                npoints=7, nlines=40, curver=cubic_curve, sorter=sorter,
            )
            f.draw_in_context(
                anim.context,
                curve_color=(0, 0, 0, 0.3),
                curve_width=1,
            )
