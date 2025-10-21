import dataclasses
import math
from typing import Any, Callable

from drawing import cairo_context

import super_simplex
import numpy as np
from hilbertcurve.hilbertcurve import HilbertCurve
from hobby import HobbyCurve
from cubic_bezier_spline import new_closed_interpolating_spline


def hobby_curve(points):
    ctrls = HobbyCurve(points, cyclic=True).get_ctrl_points()
    curve = []
    for i in range(len(points)):
        curve.append(
            (points[i], ctrls[2 * i], ctrls[2 * i + 1], points[(i + 1) % len(points)])
        )
    return curve


def cubic_curve(points):
    cbc = new_closed_interpolating_spline(points)
    return cbc.cpts


def draw_lines(ctx, points, *, closed):
    ctx.move_to(*points[0])
    for pt in points[1:]:
        ctx.line_to(*pt)
    if closed:
        ctx.close_path()
    ctx.stroke()


def curve_dlist(curve):
    dlist = []
    dlist.append(("move_to", *curve[0][0]))
    for seg in curve:
        dlist.append(("curve_to", *seg[1], *seg[2], *seg[3]))
    dlist.append(("close_path",))
    return dlist


def draw_dlist(ctx, dlist):
    for op, *args in dlist:
        getattr(ctx, op)(*args)


def draw_dlists(ctx, dlists):
    for dlist in dlists:
        draw_dlist(ctx, dlist)
        ctx.stroke()


class HilbertSorter:
    def __init__(self):
        self.sorted_indices = None

    def choose_order(self, points):
        P = 6  # 2^6 = 64 resolution per dimension
        hilbert_curve = HilbertCurve(P, 2)
        max_coord = 2**P - 1
        pointsa = np.array(points)
        min_vals = pointsa.min(axis=0)
        max_vals = pointsa.max(axis=0)

        normalized_points = (
            (pointsa - min_vals) / (max_vals - min_vals) * max_coord
        ).astype(int)

        hilbert_distances = hilbert_curve.distances_from_points(
            normalized_points.tolist()
        )
        self.sorted_indices = np.argsort(hilbert_distances)

    def _sort(self, points):
        pointsa = np.array(points)
        sorted_points = pointsa[self.sorted_indices]
        return sorted_points.tolist()


class HilbertSortEveryLine(HilbertSorter):
    def __call__(self, points):
        self.choose_order(points)
        return self._sort(points)


class HilbertSortFirstLine(HilbertSorter):
    def __call__(self, points):
        if self.sorted_indices is None:
            self.choose_order(points)
        return self._sort(points)


@dataclasses.dataclass(kw_only=True)
class Noise:
    seed: int = 1

    def __post_init__(self):
        self.gen_simplex = super_simplex.Gener([self.seed])

    def _simplex(self, x, y):
        return self.gen_simplex.noise_2d(x, y)[0]


@dataclasses.dataclass(kw_only=True)
class LinearNoise(Noise):
    # Incremental changes: change of 1 makes very small change in output.
    istart: float = 0.001
    istep: float = 0.002
    # Jump changes: change of 1 makes uncorrelated change in output.
    jstart: float = 1.0
    jstep: float = 17.0

    def point(self, i, j):
        # i changes a little, j changes a lot
        sx = i * self.istep + self.istart
        sy = j * self.jstep + self.jstart
        return (
            self._simplex(sx, sy),
            self._simplex(sx + 1, sy),
        )


@dataclasses.dataclass(kw_only=True)
class CircularNoise(Noise):
    # Incremental changes: change of 1 makes very small change in output.
    istart: int = 0
    istep: float = 0.002
    isteps: int = 50
    # Jump changes: change of 1 makes uncorrelated change in output.
    jstart: float = 1.0
    jstep: float = 17.0

    def __post_init__(self) -> None:
        super().__post_init__()
        self.r = self.istep * self.isteps / (2 * math.pi)

    def point(self, i, j):
        # i changes a little, j changes a lot
        sx = 42.17
        sy = j * self.jstep + self.jstart
        theta = 2 * math.pi / self.isteps * ((self.istart + i) % self.isteps)
        dx = self.r * math.cos(theta)
        dy = self.r * math.sin(theta)
        return (
            self._simplex(sx + dx, sy + dy),
            self._simplex(sx + 1 + dx, sy + dy),
        )


@dataclasses.dataclass
class Fluidity:
    noise: Noise
    npoints: int = 10
    nlines: int = 100
    sorter: HilbertSorter | None = None
    curver: Callable = hobby_curve

    def __post_init__(self):
        lines = [
            [self.noise.point(i, j) for j in range(self.npoints)]
            for i in range(self.nlines)
        ]

        self.lines = []
        self.curves = []

        for line in lines:
            if self.sorter is not None:
                line = self.sorter(line)
            self.lines.append(line)
            self.curves.append(self.curver(line))

    def tweak(self, **changes):
        return dataclasses.replace(self, **changes)

    def draw(
        self,
        *,
        format="svg",
        size=(600, 600),
        **kwargs,
    ):
        with cairo_context(*size, format=format) as context:
            self.draw_in_context(context, **kwargs)
        return context

    def draw_in_context(
        self,
        context,
        *,
        curve_color=(0, 0, 0, 1),
        curve_width=0.25,
        point_color=None,
        point_size=1,
        line_color=None,
        line_width=0.25,
        point_colors=None,
    ):
        sizew, sizeh = context.size()
        scale_x = sizew / 2
        scale_y = sizeh / 2
        scale = min(scale_x, scale_y)
        offset_x = (sizew - 2 * scale) / 2 + scale
        offset_y = (sizeh - 2 * scale) / 2 + scale
        context.translate(offset_x, offset_y)
        context.scale(scale, scale)
        context.rectangle(-1, -1, 2, 2)
        context.set_source_rgb(1, 1, 1)
        context.fill()

        if line_color:
            context.set_source_rgba(*line_color)
            context.set_line_width(line_width / scale)
            for line in self.lines:
                draw_lines(context, line, closed=True)

        if curve_color:
            context.set_source_rgba(*curve_color)
            context.set_line_width(curve_width / scale)
            draw_dlists(context, self.dlists())

        if point_color or point_colors:
            if point_color:
                assert point_colors is None
                point_colors = [point_color] * self.npoints
            for line in self.lines:
                for pt, point_color in zip(line, point_colors):
                    context.set_source_rgba(*point_color)
                    context.circle(*pt, point_size / scale)
                    context.fill()

    def dlists(self):
        return [curve_dlist(c) for c in self.curves]
