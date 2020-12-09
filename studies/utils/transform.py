"""A collection of functions for coords transformation."""

import math

import numpy as np


def polar2vec(r, phi):
    """Calculate Cartesian vector from polar coords."""
    x = r * math.cos(phi)
    y = -r * math.sin(phi)
    return x, y


def line_plane_collision(plane_normal, plane_point,
                         ray_direction, ray_point,
                         epsilon=1e-6):
    """Calculate a point of line-plane intersection."""
    n_dot_u = plane_normal.dot(ray_direction)
    if abs(n_dot_u) < epsilon:
        raise ValueError("Line and plane does not intersects.")

    w = ray_point - plane_point
    si = -plane_normal.dot(w) / n_dot_u
    psi = w + si * ray_direction + plane_point
    return psi


def perspective_point(x, y, phi, focal_length=1, dz=0, dx=0):
    """Calculate simple perspective for a point."""
    # TODO: use Z coordinate for original point
    plane_normal = np.asarray([0, 0, 1], dtype=np.float64)
    plane_point = np.asarray([0, 0, 0], dtype=np.float64)
    focal_point = np.asarray([0, 0, focal_length],
                             dtype=np.float64)
    y, z = polar2vec(y, -phi)
    ray_point = np.asarray([x + dx, y, z + focal_length * 2 + dz],
                           dtype=np.float64)
    ray_direction = ray_point - focal_point
    x, y, _ = line_plane_collision(plane_normal, plane_point,
                                   ray_direction, ray_point)
    return x, y


def perspective(coords, phi, focal_length=1):
    """Calculate simple perspective for a path."""
    return [perspective_point(*coord, phi, focal_length) for coord in coords]


def translate(coords, dx, dy):
    """Translate path by a delta."""
    return [(x + dx, y + dy) for x, y in coords]
