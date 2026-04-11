#!/usr/bin/env python3
"""
GitHub Octocat Bath Bomb — Mold STL Generator

3 types of 3D-printable molds (top + bottom each):
  A: Octocat silhouette shape
  B: Disc + Octocat embossed relief
  C: Disc + Octocat indent/cutout (most faithful to logo)
"""

import os
import math
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import measure
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity
import trimesh

# ── Dimensions (mm) ──────────────────────────────────────
DISC_DIAMETER  = 130.0
CAVITY_DEPTH   =  20.0   # per half → total bath bomb = 40 mm
WALL_THICK     =   3.0
FLANGE         =  10.0
RELIEF_DEPTH   =   5.0   # emboss / indent depth
FILLET         =   2.0
DOWEL_D        =   5.0
DOWEL_H        =   5.0
NSEG           = 128


# ── helpers ──────────────────────────────────────────────

def _poly(geom):
    """Ensure single valid Polygon."""
    if isinstance(geom, MultiPolygon):
        geom = max(geom.geoms, key=lambda g: g.area)
    if not geom.is_valid:
        geom = geom.buffer(0)
    return geom


def _extrude(poly, h):
    return trimesh.creation.extrude_polygon(_poly(poly), h)


def _bool(a, b, op="difference"):
    fn = getattr(trimesh.boolean, op)
    try:
        return fn([a, b], engine="manifold")
    except Exception as e:
        print(f"    ⚠ {op} failed: {e}")
        return a


def _box(w, d, h):
    b = trimesh.creation.box(extents=[w, d, h])
    b.apply_translation([0, 0, h / 2])
    return b


def _cyl(r, h, z_base):
    c = trimesh.creation.cylinder(radius=r, height=h, sections=NSEG)
    c.apply_translation([0, 0, z_base + h / 2])
    return c


def _add_dowels(mesh, positions, z, bottom=True):
    for x, y in positions:
        if bottom:
            pin = _cyl(DOWEL_D / 2, DOWEL_H, z)
            pin.apply_translation([x, y, 0])
            mesh = _bool(mesh, pin, "union")
        else:
            hole = _cyl(DOWEL_D / 2 + 0.15, DOWEL_H + 0.5, z - 0.25)
            hole.apply_translation([x, y, 0])
            mesh = _bool(mesh, hole, "difference")
    return mesh


def _dowel_pos(half_span):
    s = half_span
    return [(s, s), (s, -s), (-s, s), (-s, -s)]


# ── image → polygons ────────────────────────────────────

def extract_shapes(img_path):
    print("📷  Extracting shapes …")
    img = Image.open(img_path).convert("L")
    arr = np.array(img, dtype=float) / 255.0

    # Dark pixels = the circle body (ring around the Octocat)
    dark = arr < 0.5

    # Detect circle center & radius from dark pixel distribution
    ys, xs = np.where(dark)
    cy, cx = ys.mean(), xs.mean()
    radius = np.sqrt((xs - cx)**2 + (ys - cy)**2).max()

    # Create filled circle mask mathematically
    Y, X = np.ogrid[:arr.shape[0], :arr.shape[1]]
    filled = ((X - cx)**2 + (Y - cy)**2) <= radius**2

    # Octocat = inside the circle AND not dark
    octo = filled & ~dark

    def to_polys(mask, min_area=100):
        cs = measure.find_contours(mask.astype(float), 0.5)
        ps = []
        for c in cs:
            xy = np.column_stack([c[:, 1], c[:, 0]])
            p  = Polygon(xy).buffer(0)
            if p.is_valid and p.area > min_area:
                ps.append(p)
        return ps

    circle_ps  = to_polys(filled)
    octocat_ps = to_polys(octo)

    if not circle_ps:
        raise RuntimeError("Circle not found")
    if not octocat_ps:
        raise RuntimeError("Octocat not found")

    circle  = max(circle_ps,  key=lambda p: p.area)
    octocat = unary_union(octocat_ps)

    # scale: circle → DISC_DIAMETER mm, flip Y
    bx0, by0, bx1, by1 = circle.bounds
    cx, cy = (bx0+bx1)/2, (by0+by1)/2
    d_px   = max(bx1-bx0, by1-by0)
    s      = DISC_DIAMETER / d_px

    def xform(p):
        p = affinity.translate(p, -cx, -cy)
        p = affinity.scale(p, s, -s, origin=(0,0))
        return p.simplify(0.3, preserve_topology=True)

    circle  = xform(circle)
    octocat = xform(octocat)

    ca = circle.area
    oa = octocat.area if isinstance(octocat, Polygon) else sum(g.area for g in octocat.geoms)
    print(f"    Circle  ≈ ø{math.sqrt(ca/math.pi)*2:.0f} mm  ({ca:.0f} mm²)")
    print(f"    Octocat   {oa:.0f} mm²")
    return circle, octocat


# ── Type A: silhouette ──────────────────────────────────

def gen_A(circle, octocat):
    print("\n🐱  Type A — Silhouette")
    shape = _poly(octocat)
    # robust-ify: grow, close, open, round
    shape = shape.buffer(2.0)
    shape = shape.buffer(FILLET).buffer(-FILLET)
    shape = shape.buffer(-1.0).buffer(1.0)
    shape = _poly(shape).simplify(0.4, preserve_topology=True)

    bx0, by0, bx1, by1 = shape.bounds
    w, h = bx1-bx0, by1-by0
    mold_h = CAVITY_DEPTH + WALL_THICK
    bw = w + 2*(WALL_THICK+FLANGE)
    bh = h + 2*(WALL_THICK+FLANGE)

    cavity = _extrude(shape, CAVITY_DEPTH)
    cavity.apply_translation([0, 0, WALL_THICK])

    dp = _dowel_pos(max(bw, bh)/2 - FLANGE/2)

    bottom = _bool(_box(bw, bh, mold_h), cavity, "difference")
    bottom = _add_dowels(bottom, dp, mold_h, True)

    top = _bool(_box(bw, bh, mold_h), cavity.copy(), "difference")
    top = _add_dowels(top, dp, mold_h, False)

    print(f"    Cavity {w:.0f}×{h:.0f} mm → Mold {bw:.0f}×{bh:.0f}×{mold_h:.0f} mm")
    return bottom, top


# ── Type B: disc + relief ───────────────────────────────

def gen_B(circle, octocat):
    print("\n🔵  Type B — Disc + Relief")
    r  = DISC_DIAMETER / 2
    # bottom floor needs extra depth for the Octocat recess
    floor_h = WALL_THICK + RELIEF_DEPTH          # 8 mm
    mold_h  = floor_h + CAVITY_DEPTH              # 28 mm
    bs = DISC_DIAMETER + 2*(WALL_THICK+FLANGE)
    dp = _dowel_pos(bs/2 - FLANGE/2)

    # ---- bottom ----
    body = _box(bs, bs, mold_h)
    cav  = _cyl(r, CAVITY_DEPTH, floor_h)
    bottom = _bool(body, cav, "difference")

    oct_s  = _poly(octocat.simplify(0.5, preserve_topology=True))
    recess = _extrude(oct_s, RELIEF_DEPTH)
    recess.apply_translation([0, 0, WALL_THICK])
    bottom = _bool(bottom, recess, "difference")

    bottom = _add_dowels(bottom, dp, mold_h, True)

    # ---- top (flat, standard height) ----
    top_h = WALL_THICK + CAVITY_DEPTH
    top = _bool(_box(bs, bs, top_h), _cyl(r, CAVITY_DEPTH, WALL_THICK), "difference")
    top = _add_dowels(top, dp, top_h, False)

    print(f"    Disc ø{DISC_DIAMETER:.0f} mm → Bottom {bs:.0f}² × {mold_h:.0f}, Top ×{top_h:.0f} mm")
    return bottom, top


# ── Type C: disc + cutout ───────────────────────────────

def gen_C(circle, octocat):
    print("\n⭕  Type C — Disc + Cutout")
    r  = DISC_DIAMETER / 2
    mold_h = WALL_THICK + CAVITY_DEPTH
    bs = DISC_DIAMETER + 2*(WALL_THICK+FLANGE)
    dp = _dowel_pos(bs/2 - FLANGE/2)

    # ---- bottom: cavity + Octocat bump on floor ----
    body = _box(bs, bs, mold_h)
    cav  = _cyl(r, CAVITY_DEPTH, WALL_THICK)
    bottom = _bool(body, cav, "difference")

    oct_s = _poly(octocat.simplify(0.5, preserve_topology=True))
    bump  = _extrude(oct_s, RELIEF_DEPTH)
    bump.apply_translation([0, 0, WALL_THICK])
    bottom = _bool(bottom, bump, "union")

    bottom = _add_dowels(bottom, dp, mold_h, True)

    # ---- top (flat) ----
    top = _bool(_box(bs, bs, mold_h), _cyl(r, CAVITY_DEPTH, WALL_THICK), "difference")
    top = _add_dowels(top, dp, mold_h, False)

    print(f"    Disc ø{DISC_DIAMETER:.0f} mm → Mold {bs:.0f}² × {mold_h:.0f} mm")
    return bottom, top


# ── main ─────────────────────────────────────────────────

def main():
    print("=" * 56)
    print("  🛁  GitHub Octocat Bath Bomb — Mold Generator")
    print("=" * 56)

    here     = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(here, "GitHub-Mark-ea2971cee799.png")

    circle, octocat = extract_shapes(img_path)

    for tag, fn in [("A_silhouette", gen_A),
                    ("B_relief",     gen_B),
                    ("C_cutout",     gen_C)]:
        try:
            bot, top = fn(circle, octocat)
            for half, mesh in [("bottom", bot), ("top", top)]:
                p = os.path.join(here, f"mold_{tag}_{half}.stl")
                mesh.export(p)
                print(f"    ✅ {os.path.basename(p)}  "
                      f"({len(mesh.vertices)} verts, {len(mesh.faces)} faces)")
        except Exception as e:
            print(f"    ❌ {tag}: {e}")
            import traceback; traceback.print_exc()

    print(f"\n{'='*56}")
    print("  ✨  Complete — open STL files in your slicer!")
    print(f"{'='*56}")


if __name__ == "__main__":
    main()
