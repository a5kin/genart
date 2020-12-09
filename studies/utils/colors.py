"""A collection of functions for color transformation."""
import colorsys


def make_palette(hex_palette):
    """Make RGB palette from hex colors."""
    rgb_palette = []
    for i, col in enumerate(hex_palette):
        rgb_palette.append((
            (col >> 16) / 255,
            ((col >> 8) & 0xff) / 255,
            (col & 0xff) / 255,
            1,
        ))
    return rgb_palette


def lighten(color, percent, light_effect=0.6):
    """Lighten a color, negative values darkens it."""
    r, g, b, a = color
    r1 = min(1, max(0, r * (1 + percent)))
    g1 = min(1, max(0, g * (1 + percent)))
    b1 = min(1, max(0, b * (1 + percent)))
    if percent > 0:
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        l = min(1, max(0, l * (1 + percent)))
        r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
        r1, g1, b1, a = blend((r1, g1, b1, a), (r2, g2, b2, a), light_effect)
    return (r1, g1, b1, a)


def opaque(color, percent):
    """Make color more opaque, negative values makes it more transparent."""
    r, g, b, a = color
    a = min(1, max(0, a * (1 + percent)))
    return (r, g, b, a)


def blend(color1, color2, ratio):
    """Blend a value between two colors."""
    r1, g1, b1, a1 = color1
    r2, g2, b2, a2 = color2
    r = r1 * (1 - ratio) + r2 * ratio
    g = g1 * (1 - ratio) + g2 * ratio
    b = b1 * (1 - ratio) + b2 * ratio
    a = a1 * (1 - ratio) + a2 * ratio
    return (r, g, b, a)


def rotate_hue(color, degree):
    """Rotate a hue to given direction."""
    r, g, b, a = color
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = (h * 360 + degree) % 360 / 360
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (r, g, b, a)


def saturate(color, percent):
    """Saturate (+) or desaturate (-) a color."""
    r, g, b, a = color
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    s = min(1, max(0, s * (1 + percent)))
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (r, g, b, a)
