#!/usr/bin/env python3
"""
Generative study #2: Sunset in the City.

Original image: https://unsplash.com/photos/OrwkD-iWgqg

"""
import math
import random

import numpy as np
import cairo

from utils.colors import (
    make_palette, lighten, opaque, blend, rotate_hue, saturate,
)
from utils.transform import (
    polar2vec, perspective, perspective_point, translate,
)
from utils.primitives import draw_path, draw_poly, rectangle

BASE_COLORS = make_palette((0x6a4162, 0xd46a92, 0xf39db6, 0xf6d2d6, 0xfefafa))
WIDTH, HEIGHT = 1620, 1080

# set random seed to reproduce the exact result
SEED = "Sunset in the City"
random.seed(SEED)

# common values for perspective
persp_angle = math.pi / 2 / 1.1
focal_l = 2.5

# init main canvas
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)
# init context for ground (debug)
surface_ground = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx_ground = cairo.Context(surface_ground)


def draw_sky():
    """Draw the sky background with the sun."""
    # horizon gradient
    pattern = cairo.LinearGradient(0, 0, 0, HEIGHT)
    pattern.add_color_stop_rgba(0, *lighten(BASE_COLORS[3], 0.05, 1))
    pattern.add_color_stop_rgba(0.4, *BASE_COLORS[3])
    pattern.add_color_stop_rgba(1, *lighten(BASE_COLORS[2], 0))
    ctx.set_source(pattern)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.fill()

    # right side gradient
    color_from = blend(BASE_COLORS[0], BASE_COLORS[1], 0.5)
    pattern = cairo.LinearGradient(0, HEIGHT, WIDTH * (2 / 3), 0)
    pattern.add_color_stop_rgba(0, *opaque(color_from, -0.2))
    pattern.add_color_stop_rgba(1, *opaque(color_from, -1))
    ctx.set_source(pattern)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.fill()

    # the sun
    sun_x, sun_y = WIDTH * 0.5, HEIGHT * 0.33
    sun_color = lighten(BASE_COLORS[4], 0.5)
    r = HEIGHT
    pattern = cairo.RadialGradient(sun_x, sun_y, 0, sun_x, sun_y, r)
    pattern.add_color_stop_rgba(0, *lighten(BASE_COLORS[4], 0.5))
    for stop, dark in np.linspace((0, 0), (1, -1)):
        stop = stop ** (stop * 4.6 + 1)
        pattern.add_color_stop_rgba(stop, *opaque(sun_color, dark))
    ctx.set_source(pattern)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.fill()


def draw_ground_gradient():
    """Base ground gradient (debug, would be removed lately)."""
    global ctx
    ctx_old = ctx
    ctx = ctx_ground
    ctx.set_operator(cairo.Operator.SOURCE)
    pattern = cairo.LinearGradient(0, 0, WIDTH, 0)
    pattern.add_color_stop_rgba(0, *BASE_COLORS[0])
    pattern.add_color_stop_rgba(0.6, *blend(BASE_COLORS[0],
                                            BASE_COLORS[1], 0.3))
    pattern.add_color_stop_rgba(1, *BASE_COLORS[1])
    ctx.set_source(pattern)
    ctx.rectangle(0, HEIGHT * 0.8, WIDTH, HEIGHT)
    ctx.fill()
    ctx.set_operator(cairo.Operator.DEST_IN)
    pattern = cairo.LinearGradient(0, HEIGHT * 0.8, 0, HEIGHT)
    pattern.add_color_stop_rgba(0, 0, 0, 0, 0)
    pattern.add_color_stop_rgba(0.5, 1, 1, 1, 0.3)
    pattern.add_color_stop_rgba(1, 1, 1, 1, 1)
    ctx.set_source(pattern)
    ctx.rectangle(0, HEIGHT * 0.8, WIDTH, HEIGHT)
    ctx.fill()
    ctx = ctx_old
    ctx.set_source_surface(surface_ground)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.fill()


def draw_ground():
    """Draw the ground with buildings on it."""
    draw_ground_gradient()


def draw_study():
    """Draw the whole study."""
    # the sky
    draw_sky()
    # the ground
    draw_ground()


if __name__ == "__main__":
    draw_study()
    surface.write_to_png("./assets/pics/study02-sunset_in_the_city.png")
