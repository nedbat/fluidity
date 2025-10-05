"""Draw a square with circles and squares arranged around a circle."""

import math
from drawing import cairo_context


def generate_circle_squares(N, R, size):
    """
    Generate N squares positioned around a circle of radius R.

    Arguments:
        N: Number of points around the circle
        R: Radius of the circle
        size: Size of the canvas

    Yields:
        Tuples of (center_x, center_y, square_size) for each small square
    """
    center = size / 2

    for i in range(N):
        angle = 2 * math.pi * i / N
        px = center + R * math.cos(angle)
        py = center + R * math.sin(angle)

        dist_to_left = px
        dist_to_right = size - px
        dist_to_top = py
        dist_to_bottom = size - py

        distance_to_edge = min(dist_to_left, dist_to_right, dist_to_top, dist_to_bottom)
        small_square_size = 2 * distance_to_edge

        yield (px, py, small_square_size)


def draw_circle_squares(N, R, size=800):
    """
    Draw a square with a circle of radius R centered inside it.
    Place N points around the circle. Each point is the center of a square
    that is large enough to just touch the edge of the larger square.

    Arguments:
        N: Number of points around the circle
        R: Radius of the circle
        size: Size of the canvas (default 800)

    Returns:
        A cairo context for display in Jupyter
    """
    with cairo_context(size, size) as ctx:
    
        center = size / 2
    
        ctx.set_source_rgb(1, 1, 1)
        ctx.paint()
    
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(2)
    
        ctx.rectangle(0, 0, size, size)
        ctx.stroke()
    
        ctx.circle(center, center, R)
        ctx.set_line_width(1)
        ctx.stroke()

        for px, py, square_size in generate_circle_squares(N, R, size):
            ctx.rectangle(
                px - square_size / 2,
                py - square_size / 2,
                square_size,
                square_size
            )
            ctx.set_source_rgba(0, 0, 0, 0.1)
            ctx.fill()
            ctx.set_source_rgba(0, 0, 0, 1)
            ctx.circle(px, py, 3)
            ctx.fill()

    return ctx
