import dataclasses
from typing import Any

from drawing import cairo_context, _CairoBoundingBox

import super_simplex
import numpy as np
from hilbertcurve.hilbertcurve import HilbertCurve
from hobby import HobbyCurve


def hobby_points(points):
    curve = HobbyCurve(points, cyclic=True)
    return curve.get_ctrl_points()


def draw_lines(ctx, points, *, closed):
    ctx.move_to(*points[0])
    for pt in points[1:]:
        ctx.line_to(*pt)
    if closed:
        ctx.close_path()
    ctx.stroke()


def draw_hobby(ctx, points, ctrls):
    numpt = len(points)
    ctx.move_to(*points[0])
    for i in range(numpt):
        ctx.curve_to(*ctrls[2 * i], *ctrls[2 * i + 1], *points[(i + 1) % numpt])
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
class LinearNoise:
    seed: int = 1
    # Incremental changes: change of 1 makes very small change in output.
    istart: float = 0.001
    istep: float = 0.002
    # Jump changes: change of 1 makes uncorrelated change in output.
    jstart: float = 1.0
    jstep: float = 17.0

    def __post_init__(self):
        self.gen_simplex = super_simplex.Gener([self.seed])

    def _simplex(self, x, y):
        return self.gen_simplex.noise_2d(x, y)[0]

    def point(self, i, j):
        # i changes a little, j changes a lot
        return (
            self._simplex(
                i * self.istep + self.istart,
                j * self.jstep + self.jstart,
            ),
            self._simplex(
                i * self.istep + self.istart + 1,
                j * self.jstep + self.jstart,
            ),
        )


@dataclasses.dataclass
class Fluidity:
    noise: Any
    npoints: int = 10
    nlines: int = 100
    one_order: bool = False

    def __post_init__(self):
        lines = [
            [self.noise.point(i, j) for j in range(self.npoints)]
            for i in range(self.nlines)
        ]

        self.lines = []
        self.ctrls = []
        sorter = HilbertSorter()
        if self.one_order:
            sorter.choose_order(lines[0])
        for line in lines:
            if not self.one_order:
                sorter.choose_order(line)
            line = sorter.sort(line)
            self.lines.append(line)
            self.ctrls.append(hobby_points(line))

    def tweak(self, **changes):
        return dataclasses.replace(self, **changes)

    def draw(
        self,
        *,
        line_color=None,
        curve_color=(0, 0, 0, 0.3),
        format="svg",
        size=(600, 600),
    ):
        sizew, sizeh = size
        x1, y1, x2, y2 = self.bbox()
        extra = 1
        x1 -= extra
        y1 -= extra
        x2 += extra
        y2 += extra
        with cairo_context(*size, format=format) as context:
            content_width = x2 - x1
            content_height = y2 - y1
    
            scale_x = sizew / content_width
            scale_y = sizeh / content_height
            scale = min(scale_x, scale_y)
    
            offset_x = (sizew - content_width * scale) / 2 - x1 * scale
            offset_y = (sizeh - content_height * scale) / 2 - y1 * scale
            context.translate(offset_x, offset_y)
    
            context.scale(scale, scale)

            context.set_source_rgba(0, 0, 0, 0.993)
            context.set_line_width(0.25 / scale)
            self._draw_raw_curves(context)
            context.rectangle(-1, -1, 2, 2)
            context.move_to(0, -1)
            context.line_to(0, 1)
            context.move_to(-1, 0)
            context.line_to(1, 0)
            context.rectangle(x1+extra, y1+extra, x2-x1-(2*extra), y2-y1-(2*extra))
            context.stroke()
        return context

    def _draw_raw(self, context, line_color=None, curve_color=None):
        # scale = min(sizew / 2, sizeh / 2)
        # context.translate(sizew / 2, sizeh / 2)
        # context.scale(scale, scale)
        for line, ctrl in zip(self.lines, self.ctrls):
            if line_color is not None:
                context.set_source_rgba(*line_color)
                context.set_line_width(0.05 / scale)
                draw_lines(context, line, closed=True)
            if curve_color is not None:
                context.set_source_rgba(*curve_color)
                context.set_line_width(0.25 / scale)
                draw_hobby(context, line, ctrl)

    def _draw_raw_curves(self, context):
        for line, ctrl in zip(self.lines, self.ctrls):
            draw_hobby(context, line, ctrl)

    def draw_points(self):
        with cairo_context(600, 600, format="svg") as context:
            context.set_line_width(0.5)
            for line in zip(*self.lines):
                draw_lines(context, line, closed=False)
        return context

    def bbox(self):
        with _CairoBoundingBox(1000, 1000) as context:
            context.translate(500, 500)
            context.scale(500, 500)
            context.set_line_width(1)
            self._draw_raw_curves(context)
        return [v/1000.0 for v in context.bbox]
