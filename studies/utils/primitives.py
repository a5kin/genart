"""A collection of helpers for drawing primitives."""
import cairo

from utils.colors import lighten


def draw_path(ctx, coords, closed=True):
    """Draw a path."""
    ctx.move_to(*coords[0])
    for point in coords[1:]:
        ctx.line_to(*point)
    if closed:
        ctx.line_to(*coords[0])


def draw_poly(ctx, coords, color, line_width=1, outline_darken=0):
    """Draw a single brick."""
    ctx.set_source(cairo.SolidPattern(*color))
    draw_path(ctx, coords)
    ctx.fill()
    if not outline_darken:
        return
    ctx.set_line_width(line_width)
    ctx.set_source_rgba(*lighten(color, -outline_darken))
    draw_path(ctx, coords)
    ctx.stroke()


def rectangle(x, y, w, h):
    """Generate coords for rectangle."""
    return ((x, y), (x + w, y), (x + w, y + h), (x, y + h))
