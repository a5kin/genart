#!/usr/bin/env python3
"""
Generative study #1: Arcs of Verona.

Original image: https://colorpalettes.net/color-palette-4184/

"""
import math
import random

import cairo

from utils.colors import (
    make_palette, lighten, opaque, blend, rotate_hue, saturate,
)
from utils.transform import (
    polar2vec, perspective, perspective_point, translate,
)
from utils.primitives import draw_path, draw_poly, rectangle

BASE_COLORS = make_palette((0xbfcecd, 0x502920, 0xa7462d, 0xd07347, 0xe7c4a8))
WIDTH, HEIGHT = 1024, 1024

# set random seed to reproduce the exact result
SEED = 18757
random.seed(SEED)

# common values for perspective
persp_angle = math.pi / 2 / 1.1
focal_l = 2.5

# init main canvas
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)
# init context for floor (to imitate reflections)
surface_floor = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx_floor = cairo.Context(surface_floor)


def generate_arc_paths(x, y, width, height, num_straight,
                       num_round1, num_round2, brick_ratio=0.27):
    """Generate paths for an arc."""
    path_outer = []
    path_inner = []
    path_depth = []
    cam_y = -abs(height * 0.7)
    # straight path
    for i in range(num_straight + 1):
        xp = width
        yp = i * height / num_straight
        yp += (random.random() - 0.5) * width * brick_ratio * 0.05
        path_outer.append((xp + x, yp + y))
        xp -= width * brick_ratio
        path_inner.append((xp + x, yp + y))
        xp, yp = perspective_point(xp, yp - cam_y, 0, focal_l * width,
                                   width * brick_ratio * 0.5)
        path_depth.append((-xp + x, -yp + y + cam_y))
    # round path with R=width, ~45 degrees
    for i in range(1, num_round1 + 1):
        phi = i / num_round1 * math.pi * 0.29
        phi = math.pi - phi if width < 0 else phi
        phi = [phi, -phi][bool(height > 0)]
        cx, cy = polar2vec(abs(width), phi)
        path_outer.append((cx + x, cy + y + height))
        cx, cy = polar2vec(abs(width) * (1 - brick_ratio), phi)
        path_inner.append((cx + x, cy + y + height))
        xp, yp = perspective_point(cx, cy + height - cam_y, 0, focal_l * width,
                                   width * brick_ratio * 0.5)
        path_depth.append((-xp + x, -yp + y + cam_y))
    # round path with R=width*2, ~27.5 degrees
    nx, ny = polar2vec(abs(width), phi + math.pi)
    for i in range(1, num_round2 + 1):
        phi = i / num_round2 * math.pi * 0.112 + math.pi * 0.29
        phi = math.pi - phi if width < 0 else phi
        phi = [phi, -phi][bool(height > 0)]
        cx, cy = polar2vec(abs(width) * 2, phi)
        path_outer.append((cx + nx + x, cy + ny + y + height))
        cx, cy = polar2vec(abs(width) * 2 * (1 - 0.5 * brick_ratio), phi)
        path_inner.append((cx + nx + x, cy + ny + y + height))
        xp, yp = perspective_point(cx + nx, cy + ny + height - cam_y,
                                   0, focal_l * width,
                                   width * brick_ratio * 0.5)
        path_depth.append((-xp + x, -yp + y + cam_y))

    return path_outer, path_inner, path_depth


def draw_ceiling(color_main, color_dark, paths_l, paths_r,
                 prev_paths_l, prev_paths_r):
    """Draw a ceiling linking the current and the previous arc."""
    if prev_paths_l is None:
        return
    # ceiling lighting
    path = [path[0] for path in paths_l]
    path += [path[0] for path in paths_r[::-1]]
    path += [path[0] for path in prev_paths_r]
    path += [path[0] for path in prev_paths_l[::-1]]
    width = paths_l[0][0][0] - paths_r[0][0][0]
    # main gradient
    pattern = cairo.RadialGradient(paths_r[8][0][0] + width / 2,
                                   paths_r[8][0][1], width / 4.1,
                                   paths_r[6][0][0] + width / 2,
                                   paths_r[6][0][1], width / 1.6)
    pattern.add_color_stop_rgba(0, *color_dark)
    pattern.add_color_stop_rgba(0.6, *color_main)
    pattern.add_color_stop_rgba(1, *color_dark)
    ctx.set_source(pattern)
    draw_path(ctx, path)
    ctx.fill()
    # shadow gradient
    pattern = cairo.RadialGradient(paths_r[9][0][0] + width / 2,
                                   paths_r[9][0][1], width / 8,
                                   paths_r[9][0][0] + width / 2,
                                   paths_r[9][0][1], width / 4)
    pattern.add_color_stop_rgba(0, 0, 0, 0, 0.3)
    pattern.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(pattern)
    draw_path(ctx, path)
    ctx.fill()
    # ceiling bricks
    for i, _ in enumerate(paths_l):
        ctx.move_to(*paths_r[i][0])
        ctx.line_to(*prev_paths_r[i][0])
        ctx.stroke()
        if i > 0:
            ctx.set_source_rgba(*opaque(lighten(color_main, -0.5), -0.7))
            ctx.move_to(*paths_l[i - 1][0])
            ctx.line_to(*prev_paths_l[i - 1][0])
            ctx.stroke()


def draw_lamp(x, y, width, height, color_main, color_dark):
    """Draw a lamp from the ceiling."""
    if color_main is None:
        return
    wireframe_color = saturate(lighten(color_dark, -0.5), -0.3)
    glass_color = opaque(lighten(color_main, 0), -0.7)
    light_color = lighten(color_main, 0.5)
    # light
    yl = y + height * 3 / 4
    r = width * 0.8
    pattern = cairo.RadialGradient(x, yl, 0, x, yl, r)
    pattern.add_color_stop_rgba(0, *lighten(light_color, 1))
    pattern.add_color_stop_rgba(0.2, *light_color)
    pattern.add_color_stop_rgba(1, *opaque(light_color, -1))
    ctx.set_source(pattern)
    ctx.rectangle(x - r, yl - r, r * 2, r * 2)
    ctx.fill()
    # mount
    ctx.set_source(cairo.SolidPattern(*wireframe_color))
    draw_path(ctx, (
        (x - width / 8, y),
        (x + width / 8, y),
        (x, y - r),
    ))
    ctx.fill()
    ctx.rectangle(x - width / 16, y, width / 8, height / 2)
    ctx.fill()
    # top
    r = abs(width / 2)
    ctx.arc(x, y + height / 2 + r, r, math.pi, 0)
    ctx.fill()
    # body
    pattern = cairo.LinearGradient(x - r, y, x + r, y)
    pattern.add_color_stop_rgba(0.03, *wireframe_color)
    pattern.add_color_stop_rgba(0.125, *glass_color)
    pattern.add_color_stop_rgba(0.27, *wireframe_color)
    pattern.add_color_stop_rgba(0.5, *glass_color)
    pattern.add_color_stop_rgba(0.73, *wireframe_color)
    pattern.add_color_stop_rgba(0.855, *glass_color)
    pattern.add_color_stop_rgba(0.97, *wireframe_color)
    ctx.set_source(pattern)
    ctx.rectangle(x - r, y + height / 2 + r, r * 2, height / 2 - r * 2)
    ctx.fill()
    # bottom
    ctx.set_source(cairo.SolidPattern(*wireframe_color))
    draw_path(ctx, (
        (x - r, y + height - r),
        (x + r, y + height - r),
        (x, y + height + r * 0.4),
    ))
    ctx.fill()


def draw_verona_arc(x, y, width, height, color_main, color_dark,
                    rand_amount=0.25, grad_main=(0, 0),
                    grad_depth=(-0.18, -0.18),
                    brick_ratio=0.27, brick_depth=0.5,
                    prev_paths=(None, None), prev_colors=(None, None)):
    """Draw a single arc in Verona style."""
    paths_r = list(zip(*generate_arc_paths(x, y, width / 2, height,
                                           8, 4, 3, brick_ratio)))
    paths_l = list(zip(*generate_arc_paths(x, y, -width / 2, height,
                                           8, 4, 3, brick_ratio)))
    # ceiling to the previous arc
    prev_color_main, prev_color_dark = prev_colors
    draw_ceiling(
        prev_color_main, prev_color_dark,
        paths_l, paths_r, *prev_paths
    )
    # a lamp
    draw_lamp(x, y + height * 1.56, width / 16, -height * 0.5,
              prev_color_main, prev_color_dark)
    for paths in (paths_r, paths_l):
        # left and right half-arcs
        for i, coords in enumerate(zip(paths[:-2], paths[1:-1])):
            (((x1o, y1o), (x1i, y1i), (x1d, y1d)),
             ((x2o, y2o), (x2i, y2i), (x2d, y2d))) = coords
            coords = [(x1o, y1o), (x2o, y2o), (x2i, y2i),
                      (x2d, y2d), (x1d, y1d), (x1i, y1i)]
            if brick_depth == 0:
                del coords[3:5]
            grad_ratio = (grad_main[1] - grad_main[0]) * i / (len(paths) - 2) + grad_main[0]
            rand_ratio = random.gauss(grad_ratio, rand_amount)
            blend_ratio = max(0, min(1, (rand_ratio)))
            cur_color = blend(color_main, color_dark, blend_ratio)
            draw_poly(ctx, coords, cur_color, outline_darken=0.29)
            # brick depth
            if brick_depth > 0:
                coords = ((x1i, y1i), (x2i, y2i),
                          (x2d, y2d), (x1d, y1d))
                shadow_ratio = (grad_depth[1] - grad_depth[0]) * i / (len(paths) - 2) + grad_depth[0]
                cur_color = lighten(cur_color, shadow_ratio)
                draw_poly(ctx, coords, cur_color, outline_darken=0.5)
    # top brick
    coords = (
        paths_r[-1][0], paths_r[-2][0], paths_r[-2][1], paths_r[-2][2],
        (paths_r[-1][0][0],
         paths_r[-2][2][1] + (paths_r[-2][2][1] - paths_r[0][2][1]) * 0.02),
        paths_l[-2][2], paths_l[-2][1], paths_l[-2][0],
    )
    cur_color = blend(color_main, color_dark, grad_main[1])
    draw_poly(ctx, coords, cur_color, outline_darken=0.29)
    # top brick depth
    coords = (
        (paths_r[-1][0][0],
         paths_r[-2][1][1] + (paths_r[-2][1][1] - paths_r[0][1][1]) * 0.02),
        paths_r[-2][1], paths_r[-2][2],
        (paths_r[-1][0][0],
         paths_r[-2][2][1] + (paths_r[-2][2][1] - paths_r[0][2][1]) * 0.02),
        paths_l[-2][2], paths_l[-2][1],
    )
    if brick_depth > 0:
        draw_poly(ctx, coords, lighten(cur_color, grad_depth[1]),
                  outline_darken=0.29)
    return paths_l, paths_r


def draw_street():
    """Draw street plane."""
    # main plane
    draw_poly(ctx, rectangle(0, HEIGHT * 0.93, WIDTH, HEIGHT * 0.07),
              lighten(BASE_COLORS[0], -1.85))
    # texture with perspective
    color = lighten(saturate(opaque(BASE_COLORS[0], -0.91), 1.), 0.01, 0.5)
    ctx.set_source_rgba(*color)
    ctx.set_line_width(4)
    num_stripes, num_segments = 3528, 23
    for i in range(num_stripes):
        dx1 = WIDTH * 0.0042 * (random.random() - 0.5)
        x1, y1 = perspective_point((i / num_stripes - 0.5) * WIDTH + dx1, 0,
                                   persp_angle, focal_l * WIDTH * 0.75)
        ctx.move_to(x1 + WIDTH / 2, y1 + HEIGHT * 0.93)
        for j in range(num_segments):
            dev = abs(j - num_segments / 3.8) ** 1.42 / num_segments * 1.6
            dx2 = WIDTH * 0.02 * dev * (random.random() - 0.5)
            x2, y2 = perspective_point((i / num_stripes - 0.5) * WIDTH + dx2,
                                       -HEIGHT * 0.5 * j / (num_segments - 1),
                                       persp_angle, focal_l * WIDTH * 0.75)
            ctx.line_to(x2 + WIDTH / 2, y2 + HEIGHT * 0.93)
        ctx.stroke()


def draw_floor(x, y, width, length):
    """Draw a floor with ornament."""
    # change main context to floor
    global ctx
    ctx_old = ctx
    ctx = ctx_floor
    ctx.set_operator(cairo.Operator.SOURCE)
    # floor plane
    coords = rectangle(-width / 2, 0, width, length)
    coords = perspective(coords, persp_angle, focal_l * width)
    coords = translate(coords, x, y)
    draw_poly(ctx, coords, opaque(BASE_COLORS[0], -0.5))
    # floor tiles pattern
    tiles_x_base, tiles_y = 4, 5
    margin_x = width / tiles_x_base / 3
    for i in range(5):
        # a single pattern tile
        for yi in range(tiles_y):
            # in-between tiles are 6 in row, instead of 4
            tiles_x = [tiles_x_base, tiles_x_base + tiles_x_base // 2][yi == 4]
            # regular square grid of tiles
            for xi in range(tiles_x):
                if xi in (1, 2) and yi in (1, 2):
                    # place for center tiles
                    continue
                coords = rectangle(
                    width * xi / tiles_x + margin_x / 2 - width / 2,
                    width * yi / tiles_x_base + margin_x / 2 + width * i * 5 / 4 + width / 3,
                    width / tiles_x - margin_x,
                    width / tiles_x_base - margin_x,
                )
                coords = perspective(coords, persp_angle, focal_l * width)
                coords = translate(coords, x, y)
                draw_poly(ctx, coords, opaque(lighten(BASE_COLORS[1], -1), -0.5))
        # center square tile
        coords = rectangle(
            width / tiles_x_base + margin_x / 2 - width / 2,
            width / tiles_x_base + margin_x / 2 + width * i * 5 / 4 + width / 3,
            2 * width / tiles_x_base - margin_x,
            2 * width / tiles_x_base - margin_x,
        )
        coords = perspective(coords, persp_angle, focal_l * width)
        coords = translate(coords, x, y)
        draw_poly(ctx, coords, opaque(lighten(BASE_COLORS[1], -1), -0.5))
        # carve hole in the central tile
        coords = rectangle(
            width / tiles_x_base + margin_x * 1.5 - width / 2,
            width / tiles_x_base + margin_x * 1.5 + width * i * 5 / 4 + width / 3,
            2 * width / tiles_x_base - margin_x * 3,
            2 * width / tiles_x_base - margin_x * 3,
        )
        coords = perspective(coords, persp_angle, focal_l * width)
        coords = translate(coords, x, y)
        draw_poly(ctx, coords, opaque(BASE_COLORS[0], -0.5))
    # glare from windows
    height = width * 5 / 4
    ctx.set_operator(cairo.Operator.OVER)
    for i in range(2):
        coords = (
            (-width / 2, height * (1.3 + i)), (-width / 2, height * (1.7 + i)),
            (width / 2, height * (2.85 + i * 0.8)), (width / 2, height * (2.45 + i)),
        )
        coords = perspective(coords, persp_angle, focal_l * width)
        coords = translate(coords, x, y)
        draw_poly(ctx, coords, opaque(lighten(BASE_COLORS[-1], 0.5), -0.3))
    # restore main context
    ctx = ctx_old
    # blit floor over the main surface
    ctx.set_source_surface(surface_floor)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.fill()
    # street plane
    draw_street()


def draw_wall(x, y, width, height, num_horiz, num_vert,
              color_main, color_dark=None):
    """Draw a wall of bricks."""
    color_dark = color_dark or color_main
    # build a grid
    brick_width = width / num_horiz / 2
    brick_height = height / num_vert
    x_coords = [
        x + i * brick_width + (random.random() - 0.5) * brick_width * 0.2
        for i in range(num_horiz * 2 + 2)
    ]
    y_coords = [
        y + i * brick_height + (random.random() - 0.5) * brick_height * 0.01
        for i in range(num_vert + 1)
    ]

    # draw bricks
    for i, (y1, y2) in enumerate(zip(y_coords[:-1], y_coords[1:])):
        for j in range(num_horiz):
            x1, x2 = x_coords[j * 2 + i % 2], x_coords[(j + 1) * 2 + i % 2]
            coords = ((x1, y1), (x2 - 1, y1), (x2 - 1, y2 - 1), (x1, y2 - 1))
            blend_ratio = abs(random.gauss(0.5, 0.2) - 0.5)
            cur_color = blend(color_main, color_dark, blend_ratio)
            draw_poly(ctx, coords, cur_color, outline_darken=0.2)


def draw_altar(x_p, y_p, w_p, h_p):
    """Draw far wall with an "altar". """
    # inner arc
    color = lighten(saturate(BASE_COLORS[1], -0.1), 0.1)
    ctx.set_source_rgba(*color)
    ctx.rectangle(x_p + w_p / 2, y_p + h_p * 2, -w_p, -h_p)
    ctx.fill()
    # top brick rays
    rev_ang = (h_p > 0) * math.pi
    rev_blend = 1 + (h_p > 0) * 1.5
    rays_color = blend(BASE_COLORS[1], BASE_COLORS[3], 0.5 / rev_blend)
    ctx.set_source_rgba(*rays_color)
    ctx.set_line_width(1.5)
    ctx.arc(x_p, y_p + h_p, abs(w_p) / 32, -math.pi + rev_ang, 0 - rev_ang)
    ctx.stroke()
    for i in range(13):
        phi = i / 12 * math.pi
        x1, y1 = polar2vec(-w_p / 20, phi + rev_ang)
        x2, y2 = polar2vec(-w_p / 4, phi + rev_ang)
        ctx.move_to(x1 + x_p, y1 + y_p + h_p)
        ctx.line_to(x2 + x_p, y2 + y_p + h_p)
        ctx.set_line_width(1)
        ctx.stroke()
    # top altar shadow
    pattern = cairo.RadialGradient(x_p, y_p + h_p, w_p * 0.13,
                                   x_p, y_p + h_p, w_p / 4)
    pattern.add_color_stop_rgba(0, 0, 0, 0, 0)
    pattern.add_color_stop_rgba(1, 0, 0, 0, 0.9)
    pattern.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(pattern)
    ctx.rectangle(x_p + w_p / 2, y_p + h_p * 2, -w_p, -h_p)
    ctx.fill()
    br = 0.405
    # outer arc
    color = lighten(BASE_COLORS[2], 0)
    prev_paths_l, prev_paths_r = draw_verona_arc(
        x_p, y_p, w_p, h_p,
        saturate(lighten(color, 0.12), -0.1),
        saturate(lighten(color, -0.5), -0.1),
        0.042, (0, 1), (0.23, 1.78),
        brick_ratio=1 - br, brick_depth=0,
    )
    # far wall
    draw_wall(
        x_p - w_p / 2, y_p - max(0, -h_p), w_p, abs(h_p),
        7, 8,
        lighten(saturate(BASE_COLORS[2], -0.42), -0.08),
        BASE_COLORS[1],
    )
    # bottom brick
    color = lighten(saturate(BASE_COLORS[1], -0.1), 0.1)
    ctx.set_source_rgba(*color)
    ctx.rectangle(x_p + w_p * br / 2, y_p + h_p - h_p / 2, -w_p * br, -h_p / 8)
    ctx.fill()
    # side altar shadows
    pattern = cairo.LinearGradient(x_p - w_p * br / 2, y_p,
                                   x_p + w_p * br / 2, y_p)
    pattern.add_color_stop_rgba(0, 0, 0, 0, 0)
    pattern.add_color_stop_rgba(0, 0, 0, 0, 0.7)
    pattern.add_color_stop_rgba(0.2, 0, 0, 0, 0)
    pattern.add_color_stop_rgba(0.8, 0, 0, 0, 0)
    pattern.add_color_stop_rgba(1, 0, 0, 0, 0.7)
    pattern.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(pattern)
    ctx.rectangle(x_p + w_p / 2, y_p + h_p * 1.005, -w_p, -h_p * 0.63)
    ctx.fill()


def draw_arcade(x, y, width, height):
    """Draw a series of arcs with perspective, specific to the scene."""
    colors = BASE_COLORS[:4] + [BASE_COLORS[2], lighten(BASE_COLORS[2], -0.3)]
    prev_paths_l, prev_paths_r = None, None
    prev_color_main, prev_color_dark = None, None
    for i, color in list(enumerate(colors))[::-1]:
        coords = (
            (0, width * i * 5 / 4),
            (width, width * i * 5 / 4),
        )
        coords = perspective(coords, persp_angle, focal_l * width)
        ratio = coords[1][0] / width
        coords = translate(coords, x, y)
        x_p, y_p = coords[0]
        w_p, h_p = width * ratio, height * ratio
        if i == len(colors) - 1:
            # far wall with "altar"
            draw_altar(x_p, y_p, w_p, h_p)
            continue
        # regular arc
        prev_paths_l, prev_paths_r = draw_verona_arc(
            x_p, y_p, w_p, h_p,
            saturate(lighten(color, 0.12 if i else 0.01), -0.3 if i else 0),
            lighten(rotate_hue(color, 0 if i else 30), -0.37 if i else -0.12),
            0.042 if i else 0.23, (0, 1) if i else (0, 0),
            (0.23, 1.78) if i else (-0.18, -0.32),
            prev_paths=(prev_paths_l, prev_paths_r),
            prev_colors=(prev_color_main, prev_color_dark),
        )
        # colors for ceiling
        prev_color_main = saturate(lighten(color, 0.75), -0.10)
        prev_color_dark = saturate(lighten(color, -0.26), -0.27)


def draw_study():
    """Draw the whole study."""
    # main wall
    draw_wall(
        -90, -10, WIDTH + 100, HEIGHT + 40, 7, 18,
        BASE_COLORS[0], lighten(rotate_hue(BASE_COLORS[0], 30), -0.12)
    )
    # reflections
    draw_arcade(WIDTH / 2, HEIGHT * 0.95, WIDTH * 0.72, -HEIGHT * 0.485)
    # floor
    draw_floor(WIDTH / 2, HEIGHT * 0.95, WIDTH * 0.72, HEIGHT * 4.5)
    # arcade
    draw_arcade(WIDTH / 2, HEIGHT * 0.95, WIDTH * 0.72, HEIGHT * 0.485)


if __name__ == "__main__":
    draw_study()
    surface.write_to_png("./study01-arcs_of_verona.png")
