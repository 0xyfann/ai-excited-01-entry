#!/usr/bin/env python3
"""ai-excited-01: a tiny glowing sailboat crossing a huge low moon."""
import os
import math
import struct
import zlib

W = 960
H = 960

# Moon geometry
MX = 480.0
MY = 468.0
MR = 352.0
HORIZON = 618


def clamp(v):
    if v < 0.0:
        return 0.0
    if v > 255.0:
        return 255.0
    return v


def render():
    # RGB buffer
    buf = bytearray(W * H * 3)

    # Precompute aurora center lines per column
    aur1 = [0.0] * W
    aur2 = [0.0] * W
    for x in range(W):
        fx = x / W
        aur1[x] = 118.0 + 46.0 * math.sin(fx * 5.1 + 0.6) + 18.0 * math.sin(fx * 11.0 + 2.0)
        aur2[x] = 196.0 + 38.0 * math.sin(fx * 4.2 + 2.4) + 14.0 * math.sin(fx * 9.0 + 0.4)

    mr2 = MR * MR
    glow_r = MR * 1.55
    glow_r2 = glow_r * glow_r

    for y in range(H):
        fy = y / H
        # Base vertical gradient
        if y < HORIZON:
            t = y / HORIZON
            # deep indigo -> teal
            br = 8.0 + 10.0 * t
            bg = 10.0 + 52.0 * t
            bb = 42.0 + 58.0 * t
            in_sea = False
        else:
            t = (y - HORIZON) / (H - HORIZON)
            br = 6.0 + 4.0 * t
            bg = 34.0 - 10.0 * t
            bb = 52.0 - 6.0 * t
            in_sea = True

        dy = y - MY
        dy2 = dy * dy
        a1c = aur1
        a2c = aur2
        row_off = y * W * 3
        for x in range(W):
            r = br
            g = bg
            b = bb

            # Aurora ribbons (sky only)
            if y < 330:
                d1 = y - a1c[x]
                if -70.0 < d1 < 70.0:
                    fall = math.exp(-(d1 * d1) / 1250.0)
                    # fade ribbon ends horizontally a bit
                    edge = 0.55 + 0.45 * math.sin((x / W) * math.pi)
                    r += 18.0 * fall * edge
                    g += 95.0 * fall * edge
                    b += 72.0 * fall * edge
                d2 = y - a2c[x]
                if -55.0 < d2 < 55.0:
                    fall2 = math.exp(-(d2 * d2) / 800.0)
                    edge2 = 0.45 + 0.55 * math.sin((x / W) * math.pi)
                    r += 42.0 * fall2 * edge2
                    g += 52.0 * fall2 * edge2
                    b += 88.0 * fall2 * edge2

            dx = x - MX
            d2 = dx * dx + dy2

            # Moon glow
            if d2 < glow_r2 and not in_sea:
                dist = math.sqrt(d2)
                if dist > MR:
                    gf = (1.0 - (dist - MR) / (glow_r - MR))
                    gf = gf * gf * 0.55
                    r += 235.0 * gf
                    g += 195.0 * gf
                    b += 120.0 * gf
                else:
                    # Moon disc: pale gold with very subtle radial shading
                    # and a few soft crater tints (analytic circles)
                    shade = 1.0 - 0.10 * (d2 / mr2)
                    r = 242.0 * shade
                    g = 208.0 * shade
                    b = 148.0 * shade
                    # subtle craters (very soft tints, varied sizes)
                    cx = x - 380.0
                    cy = y - 380.0
                    if cx * cx + cy * cy < 2025.0:
                        r *= 0.972; g *= 0.972; b *= 0.982
                    cx = x - 590.0
                    cy = y - 520.0
                    if cx * cx + cy * cy < 3249.0:
                        r *= 0.978; g *= 0.978; b *= 0.986
                    cx = x - 520.0
                    cy = y - 300.0
                    if cx * cx + cy * cy < 1225.0:
                        r *= 0.982; g *= 0.982; b *= 0.988
                    cx = x - 300.0
                    cy = y - 520.0
                    if cx * cx + cy * cy < 676.0:
                        r *= 0.98; g *= 0.98; b *= 0.988
                    cx = x - 640.0
                    cy = y - 350.0
                    if cx * cx + cy * cy < 900.0:
                        r *= 0.98; g *= 0.98; b *= 0.988

            # Sea: moon reflection path
            if in_sea:
                # vertical shimmering path under the moon
                depth = (y - HORIZON) / (H - HORIZON)
                path_half = 52.0 + 150.0 * depth
                wob = 16.0 * math.sin(y * 0.11) + 9.0 * math.sin(y * 0.031 + 1.7)
                cxp = MX + wob
                adx = abs(x - cxp)
                if adx < path_half:
                    # broken shimmer: long horizontal glints, sparse in x
                    band = math.sin(y * 0.85 + math.sin(x * 0.02) * 1.2)
                    dash = math.sin(x * 0.045 + y * 0.22 + math.sin(y * 0.05) * 2.0)
                    s = band * 0.6 + dash * 0.4
                    if s > 0.18:
                        core = 1.0 - adx / path_half
                        inten = core * core * (s - 0.18) * 1.15 * (1.0 - depth * 0.55)
                        r += 225.0 * inten
                        g += 180.0 * inten
                        b += 105.0 * inten
                # gentle horizontal wave lightening (sparse, broken dashes)
                wv = math.sin(x * 0.045 + y * 0.35) * math.sin(y * 0.09)
                dash2 = math.sin(x * 0.013 + y * 0.11)
                if wv > 0.86 and dash2 > -0.2:
                    r += 6.0; g += 10.0; b += 9.0
                # darken moon part below horizon (sea covers it) already handled
                # horizon line highlight
                if y - HORIZON < 2:
                    r += 30.0; g += 34.0; b += 26.0

            i = row_off + x * 3
            buf[i] = int(clamp(r))
            buf[i + 1] = int(clamp(g))
            buf[i + 2] = int(clamp(b))

    # ---- Stars: deterministic splat (LCG) ----
    seed = 123456789
    def rnd():
        nonlocal seed
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        return seed / 0x7FFFFFFF

    for _ in range(210):
        sx = int(rnd() * W)
        sy = int(rnd() * (HORIZON - 40) * 0.92)
        # keep stars off the moon disc (with small margin)
        ddx = sx - MX
        ddy = sy - MY
        if ddx * ddx + ddy * ddy < (MR + 8) * (MR + 8):
            continue
        bright = 130 + int(rnd() * 125)
        big = rnd() > 0.86
        # dim stars near horizon slightly
        idx = (sy * W + sx) * 3
        buf[idx] = min(255, buf[idx] + bright)
        buf[idx + 1] = min(255, buf[idx + 1] + bright)
        buf[idx + 2] = min(255, buf[idx + 2] + bright)
        if big:
            for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = sx + ox, sy + oy
                if 0 <= nx < W and 0 <= ny < H:
                    j = (ny * W + nx) * 3
                    add = bright // 2
                    buf[j] = min(255, buf[j] + add)
                    buf[j + 1] = min(255, buf[j + 1] + add)
                    buf[j + 2] = min(255, buf[j + 2] + add)

    # ---- Boat: rasterize inside bounding box ----
    # Boat sits on the horizon, centred on the moon.
    # Coordinates (x, y):
    # mast top ~ (486, 408); hull around y 596-632.
    def inside_tri(px, py, ax, ay, bx, by, cx, cy):
        d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if d == 0:
            return False
        a = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / d
        b_ = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / d
        c_ = 1.0 - a - b_
        return a >= 0 and b_ >= 0 and c_ >= 0

    bx0, bx1, by0, by1 = 330, 640, 390, 650
    for y in range(by0, by1):
        for x in range(bx0, bx1):
            i = (y * W + x) * 3
            # Sail glow halo: distance to sail centre
            gdx = x - 488.0
            gdy = y - 500.0
            gd = math.sqrt(gdx * gdx + gdy * gdy)
            if gd < 130.0:
                gf = (1.0 - gd / 130.0) ** 2 * 0.20
                buf[i] = int(clamp(buf[i] + 200.0 * gf))
                buf[i + 1] = int(clamp(buf[i + 1] + 130.0 * gf))
                buf[i + 2] = int(clamp(buf[i + 2] + 40.0 * gf))
            # Main sail (right of mast): bright cream-gold, clearly
            # lighter than the moon so the boat pops at small sizes
            if inside_tri(x, y, 494, 420, 494, 594, 606, 594):
                t = (y - 420) / 174.0
                buf[i] = int(clamp(255.0 - 10.0 * t))
                buf[i + 1] = int(clamp(228.0 - 26.0 * t))
                buf[i + 2] = int(clamp(158.0 - 34.0 * t))
                continue
            # Jib sail (left of mast): warm amber, a step deeper
            if inside_tri(x, y, 478, 438, 478, 594, 392, 594):
                t = (y - 438) / 156.0
                buf[i] = int(clamp(253.0 - 16.0 * t))
                buf[i + 1] = int(clamp(204.0 - 28.0 * t))
                buf[i + 2] = int(clamp(122.0 - 30.0 * t))
                continue
            # Mast
            if 484 <= x <= 489 and 408 <= y <= 596:
                buf[i] = 22; buf[i + 1] = 18; buf[i + 2] = 26
                continue
            # Small flag triangle at mast top
            if inside_tri(x, y, 489, 408, 489, 424, 516, 416):
                buf[i] = 232; buf[i + 1] = 84; buf[i + 2] = 64
                continue
            # Hull: dark silhouette polygon meeting the sails directly
            if inside_tri(x, y, 386, 594, 600, 594, 560, 632) or \
               inside_tri(x, y, 386, 594, 560, 632, 420, 632):
                buf[i] = 16; buf[i + 1] = 14; buf[i + 2] = 24
                continue

    # Small warm reflection of sails just below hull
    for y in range(634, 684):
        depth = (y - 634) / 50.0
        half = 56.0 * (1.0 - depth * 0.4)
        wob = 8.0 * math.sin(y * 0.3)
        for x in range(int(480 - half), int(480 + half)):
            s = math.sin(x * 0.07 + y * 0.6)
            if s > 0.2:
                i = (y * W + x) * 3
                inten = (1.0 - depth) * 0.28 * s
                buf[i] = int(clamp(buf[i] + 200.0 * inten))
                buf[i + 1] = int(clamp(buf[i + 1] + 120.0 * inten))
                buf[i + 2] = int(clamp(buf[i + 2] + 40.0 * inten))

    return buf


def write_png(path, buf):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw.extend(buf[y * stride:(y + 1) * stride])
    comp = zlib.compress(bytes(raw), level=9)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return c

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    buf = render()
    write_png(os.path.join(out_dir, "entry.png"), buf)


if __name__ == "__main__":
    main()
