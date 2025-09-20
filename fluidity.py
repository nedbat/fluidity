import dataclasses
import math
from typing import Any

from drawing import cairo_context

import super_simplex
import numpy as np
from hilbertcurve.hilbertcurve import HilbertCurve
from hobby import HobbyCurve
from cubic_bezier_spline import new_closed_interpolating_spline


def hobby_points(points):
    curve = HobbyCurve(points, cyclic=True)
    return curve.get_ctrl_points()


def cubic_points(points):
    cbc = new_closed_interpolating_spline(points)
    return cbc.cpts


def draw_lines(ctx, points, *, closed):
    ctx.move_to(*points[0])
    for pt in points[1:]:
        ctx.line_to(*pt)
    if closed:
        ctx.close_path()
    ctx.stroke()


def hobby_dlist(points, ctrls):
    dlist = []
    numpt = len(points)
    dlist.append(("move_to", *points[0]))
    for i in range(numpt):
        dlist.append(
            ("curve_to", *ctrls[2 * i], *ctrls[2 * i + 1], *points[(i + 1) % numpt])
        )
    dlist.append(("close_path",))
    return dlist


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


def draw_hobby(ctx, points, ctrls):
    dlist = hobby_dlist(points, ctrls)
    draw_dlist(ctx, dlist)
    ctx.stroke()


class HilbertSorter:
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

    def sort(self, points):
        pointsa = np.array(points)
        sorted_points = pointsa[self.sorted_indices]
        return sorted_points.tolist()


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
    noise: Any
    npoints: int = 10
    nlines: int = 100
    one_order: bool = False
    sorter: HilbertSorter | None = None
    curve: str = "hobby"

    def __post_init__(self):
        lines = [
            [self.noise.point(i, j) for j in range(self.npoints)]
            for i in range(self.nlines)
        ]

        self.lines = []
        self.curves = []

        if self.sorter is None:
            self.sorter = HilbertSorter()
            if self.one_order:
                self.sorter.choose_order(lines[0])

        for line in lines:
            if not self.one_order:
                self.sorter.choose_order(line)
            line = self.sorter.sort(line)
            self.lines.append(line)
            if self.curve == "hobby":
                ctrls = hobby_points(line)
                curve = []
                for i in range(len(line)):
                    curve.append(
                        (line[i], ctrls[2 * i], ctrls[2 * i + 1], line[(i + 1) % len(line)])
                    )
                self.curves.append(curve)
            else:
                self.curves.append(cubic_points(line))

    def tweak(self, **changes):
        return dataclasses.replace(self, **changes)

    def draw(
        self,
        *,
        line_color=None,
        curve_color=(0, 0, 0, 1),
        format="svg",
        size=(600, 600),
        ptcolor=None,
    ):
        sizew, sizeh = size
        with cairo_context(*size, format=format) as context:
            scale_x = sizew / 2
            scale_y = sizeh / 2
            scale = min(scale_x, scale_y)
            offset_x = (sizew - 2 * scale) / 2 + scale
            offset_y = (sizeh - 2 * scale) / 2 + scale
            context.translate(offset_x, offset_y)
            context.scale(scale, scale)
            context.set_source_rgba(*curve_color)
            context.set_line_width(0.25 / scale)
            draw_dlists(context, self.dlists())
            if ptcolor:
                context.set_source_rgba(*ptcolor)
                for line in self.lines:
                    for pt in line:
                        context.arc(*pt, 2/scale, 0, math.pi*2)
                        context.fill()
        return context

    def dlists(self):
        return [curve_dlist(c) for c in self.curves]

    def draw_points(self):
        with cairo_context(600, 600, format="svg") as context:
            context.set_line_width(0.5)
            for line in zip(*self.lines):
                draw_lines(context, line, closed=False)
        return context
