#!/usr/bin/env python3
"""
Generative study #2: Sunset in the City.

Original image: https://unsplash.com/photos/OrwkD-iWgqg

"""
import math
import random
import itertools

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
SEED = "Sunset in the City 10"  # 10, 12
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


def generate_ground_points(w, h, num_x, num_y, cam_y):
    """Generate terrain points with calculated perspective."""
    # coordinates grid
    coords = list(itertools.product(np.linspace(-w / 2, w / 2, num_x),
                                    np.linspace(0, h, num_y)))
    # a hill, generated by z = sin(x) * sin(y)
    z_indexes = (
        0.08 * h * math.sin(x / w * math.pi) * math.sin((y - h * 0.2) / h * math.pi)
        if x > 0 and y > 0 else
        0.03 * h * math.sin(x / w * math.pi) * math.sin(-y / h * math.pi * 1.2)
        for x, y in coords
    )
    # sort points from far to closer
    points = sorted(zip(coords, z_indexes),
                    key=lambda coord: coord[0][::-1], reverse=True)
    # calculate perspective
    points = (
        perspective_point(
            -x, z - cam_y, 0, focal_l * w, y
        )
        for (x, y), z in points
    )
    # translate points back
    points = translate(points, WIDTH / 2, HEIGHT - cam_y)
    return points


def draw_house(x, y, w, h, color):
    """Draw a single house."""
    coords = (
        (x - w / 2, y), (x + w / 2, y),
        (x + w / 2, y - h), (x - w / 2, y - h),
    )
    draw_poly(ctx, coords, color)


def draw_ground():
    """Draw the ground with buildings on it."""
    draw_ground_gradient()
    cam_y = HEIGHT * 0.5
    num_x, num_y = 50, 50
    density = 0.8
    points = generate_ground_points(WIDTH * 1.5, HEIGHT * 3,
                                    num_x, num_y, cam_y)
    color_magic = lighten(saturate(BASE_COLORS[0], 0.1), 0.8)
    for i, (x, y) in enumerate(points):
        # calculate colors from x, y coordinate
        blend_x = (i // num_x) / num_x
        blend_y = (i % num_y) / num_y * 2 - 1
        blend_y = min(0.5, max(-0.5, blend_y)) + 0.5
        color_l = blend(color_magic, BASE_COLORS[0], blend_x)
        color_r = (
            blend(BASE_COLORS[2], BASE_COLORS[1], blend_x / 0.6)
            if blend_x < 0.6 else
            blend(BASE_COLORS[1], BASE_COLORS[0], blend_x / 0.6 - 1)
        )
        color = blend(color_r, color_l, blend_y)
        color = opaque(color, (blend_x - 1) * 0.8 + 0.2)
        if i // num_y < num_y - 2 and i % num_x < num_x - 2:
            # draw solid ground
            face_coords = (
                points[i], points[i + 1],
                points[i + num_x + 1], points[i + num_x]
            )
            draw_poly(ctx, face_coords, color, outline_darken=-0.1)
            random_height = abs(random.gauss(0.5, 0.2) - 0.5)
            random_width = abs(random.gauss(0.5, 0.1))
            # draw a building
            if random.random() < density * max(0.3, 1 - blend_x):
                w, h = perspective_point(
                    -WIDTH * random_width / 7, -HEIGHT * random_height * 0.8,
                    0, focal_l * WIDTH * 1.5, (1 - blend_x) * HEIGHT * 15
                )
                draw_house(*points[i], w, h, color)
        # grid points (debug)
        # ctx.set_source(cairo.SolidPattern(1, 1, 1, 1))
        # ctx.arc(x, y, 2, 0, 2 * math.pi)
        # ctx.fill()


def draw_study():
    """Draw the whole study."""
    # the sky
    draw_sky()
    # the ground
    draw_ground()


if __name__ == "__main__":
    draw_study()
    surface.write_to_png("./assets/pics/study02-sunset_in_the_city.png")
