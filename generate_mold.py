#!/usr/bin/env python3
"""
GitHub Octocat Bath Bomb — Two-Piece Clamshell Mold Generator

Generates a 2-piece clamshell mold (halves A and B) for a cat-shaped bath bomb.
Trial 01 (see experiments/2026-05-04-trial-01/) showed that the previous
single-sided container mold made the bath bomb impossible to release.
The clamshell design solves this by splitting the mold along the parting plane,
so the two halves can be opened like a shell after drying.

Features:
  - Symmetric two-piece (left/right) design with mirrored cavities
  - 8° draft angle (steeper than v1 for powdery bath bomb material)
  - R3mm fillets on the cat outline
  - 4mm walls and floor on each half
  - 5mm outer flange around the parting plane (rubber-band clamping surface)
  - 4 alignment dowels (φ4mm pins on side A, matching holes on side B)
  - Target outer width ≈ 80mm (hand-friendly bath bomb size)

Outputs:
  mold_cat_clamshell_A.stl  — half with alignment pins
  mold_cat_clamshell_B.stl  — half with alignment holes
"""

import os
import math
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation, label
from skimage import measure
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.ops import unary_union
from shapely import affinity
import trimesh

# ── Dimensions (mm) ──────────────────────────────────────
WALL          =   4.0   # wall thickness around cavity
FLOOR         =   4.0   # floor thickness (back of each half)
DEPTH_HALF    =  20.0   # cavity depth per half (total bath bomb thickness ≈ 40mm)
DRAFT_DEG     =   8.0   # draft angle (top wider than bottom for easy release)
FILLET_R      =   3.0   # corner rounding radius on cat silhouette
TARGET_WIDTH  =  80.0   # target overall cat-silhouette width (mm)

FLANGE_W      =   5.0   # flange width extending outward from outer wall
FLANGE_T      =   4.0   # flange thickness (in Z direction)

PIN_DIA       =   4.0   # alignment dowel diameter
PIN_LEN       =   6.0   # dowel length protruding above flange
PIN_CLEARANCE =   0.3   # extra radius/depth for the matching hole on side B

NSEG          = 64


# ── Image → cat polygon ─────────────────────────────────

def extract_cat(img_path):
    """Extract the Octocat silhouette (cat only, no outer ring)."""
    print("📷  Extracting cat shape …")
    img = Image.open(img_path).convert("L")
    arr = np.array(img, dtype=float) / 255.0

    dark = arr < 0.5
    ys, xs = np.where(dark)
    cy, cx = ys.mean(), xs.mean()
    radius = np.sqrt((xs - cx)**2 + (ys - cy)**2).max()

    Y_grid, X_grid = np.mgrid[:arr.shape[0], :arr.shape[1]]
    dist = np.sqrt((X_grid - cx)**2 + (Y_grid - cy)**2)
    Y, X = np.ogrid[:arr.shape[0], :arr.shape[1]]
    filled = ((X - cx)**2 + (Y - cy)**2) <= radius**2
    octo_all = filled & ~dark

    # Step 1: distance seed (histogram dip at ~155px separates cat from ring)
    cat = octo_all & (dist <= 155)

    # Step 2: flood-fill grow bounded by dark pixels
    for _ in range(50):
        expanded = binary_dilation(cat, iterations=1)
        new_cat = expanded & octo_all & (dist <= radius - 10)
        if new_cat.sum() == cat.sum():
            break
        cat = new_cat

    # Step 3: add disconnected parts (e.g. tentacle)
    remaining = (dist <= radius - 5) & ~dark & ~cat
    labels, n = label(remaining)
    for lbl in range(1, n + 1):
        comp = labels == lbl
        if comp.sum() > 200 and dist[comp].mean() < 200:
            cat |= comp
            print(f"    + added disconnected part ({comp.sum()} px)")

    # Convert mask → shapely polygon
    contours = measure.find_contours(cat.astype(float), 0.5)
    polys = []
    for c in contours:
        if len(c) < 10:
            continue
        xy = np.column_stack([c[:, 1], c[:, 0]])
        p = Polygon(xy).buffer(0)
        if p.is_valid and p.area > 100:
            polys.append(p)
    poly = unary_union(polys)

    # Initial scale (centre, flip Y, normalise circle to 130mm so buffer
    # operations stay in a reasonable mm range), then re-scale to TARGET_WIDTH.
    bx = poly.bounds
    c_center = ((bx[0]+bx[2])/2, (bx[1]+bx[3])/2)
    scale = 130.0 / (radius * 2)
    poly = affinity.translate(poly, -c_center[0], -c_center[1])
    poly = affinity.scale(poly, scale, -scale, origin=(0, 0))
    poly = poly.simplify(0.3, preserve_topology=True)

    # Robustify: grow, round all corners with R fillet
    poly = poly.buffer(2.0)                              # +2mm min thickness
    poly = poly.buffer(FILLET_R).buffer(-FILLET_R)       # round outward corners
    poly = poly.buffer(-FILLET_R).buffer(FILLET_R)       # round inward corners
    if isinstance(poly, MultiPolygon):
        poly = max(poly.geoms, key=lambda g: g.area)
    poly = poly.simplify(0.3, preserve_topology=True)

    # Re-scale so the cat's largest dimension matches TARGET_WIDTH
    bx0, by0, bx1, by1 = poly.bounds
    w, h = bx1 - bx0, by1 - by0
    target_scale = TARGET_WIDTH / max(w, h)
    poly = affinity.scale(poly, target_scale, target_scale, origin=(0, 0))

    # Recentre at origin
    bx0, by0, bx1, by1 = poly.bounds
    poly = affinity.translate(poly, -(bx0+bx1)/2, -(by0+by1)/2)

    bx0, by0, bx1, by1 = poly.bounds
    w, h = bx1 - bx0, by1 - by0
    holes = len(list(poly.interiors))
    print(f"    Cat: {w:.0f}×{h:.0f} mm, {len(poly.exterior.coords)} verts, {holes} holes")
    return poly


# ── Pin / hole helpers ──────────────────────────────────

def pick_pin_positions(flange_outer, outer_top, n_samples=240):
    """Find 4 pin positions inside the flange ring (flange_outer − outer_top).

    Walks outward from the centroid in 4 cardinal directions and places each
    pin at the radial midpoint of the ring along that direction, so the pins
    sit on the flange and never on the cavity wall.
    """
    cx, cy = flange_outer.centroid.x, flange_outer.centroid.y
    bx0, by0, bx1, by1 = flange_outer.bounds
    max_r = max(bx1 - bx0, by1 - by0)

    positions = []
    for angle_deg in (0, 90, 180, 270):
        a = math.radians(angle_deg)
        cos_a, sin_a = math.cos(a), math.sin(a)
        ring_radii = []
        for i in range(1, n_samples + 1):
            r = max_r * (i / n_samples)
            x, y = cx + r * cos_a, cy + r * sin_a
            pt = Point(x, y)
            if flange_outer.contains(pt) and not outer_top.contains(pt):
                ring_radii.append(r)
        if ring_radii:
            r_mid = (min(ring_radii) + max(ring_radii)) / 2
            positions.append((cx + r_mid * cos_a, cy + r_mid * sin_a))
    return positions


# ── Mold half generation ────────────────────────────────

def build_half(cat_poly, side='A'):
    """Build one half of the clamshell mold.

    side='A' produces alignment pins on top of the flange.
    side='B' produces matching holes recessed into the flange.
    Both halves are otherwise identical (same outer profile, same cavity).
    """
    print(f"\n🐱  Building clamshell half {side} …")

    draft_offset = DEPTH_HALF * math.tan(math.radians(DRAFT_DEG))
    print(f"    Draft offset at parting plane: {draft_offset:.1f} mm")

    cavity_top = cat_poly.buffer(draft_offset)
    outer_top = cavity_top.buffer(WALL)
    flange_outer = outer_top.buffer(FLANGE_W)

    if isinstance(outer_top, MultiPolygon):
        outer_top = max(outer_top.geoms, key=lambda g: g.area)
    if isinstance(flange_outer, MultiPolygon):
        flange_outer = max(flange_outer.geoms, key=lambda g: g.area)

    H = FLOOR + DEPTH_HALF  # total height of the half (back face → parting plane)

    # Outer body (full height) extruded from outer_top profile
    outer = trimesh.creation.extrude_polygon(outer_top, H)

    # Flange ring at parting plane: extrude flange_outer profile to FLANGE_T,
    # then translate so its top surface is flush with the parting plane (z = H).
    flange = trimesh.creation.extrude_polygon(flange_outer, FLANGE_T)
    flange.apply_translation([0, 0, H - FLANGE_T])

    body = trimesh.boolean.union([outer, flange], engine="manifold")

    # Tapered cavity: stack slices from back (narrow) to parting plane (wide)
    n_slices = 10
    slice_h = DEPTH_HALF / n_slices
    slices = []
    for i in range(n_slices):
        t = i / max(n_slices - 1, 1)
        offset = draft_offset * t
        shape = cat_poly.buffer(offset)
        if isinstance(shape, MultiPolygon):
            shape = max(shape.geoms, key=lambda g: g.area)
        s = trimesh.creation.extrude_polygon(shape, slice_h + 0.1)
        s.apply_translation([0, 0, FLOOR + i * slice_h])
        slices.append(s)

    cavity = slices[0]
    for s in slices[1:]:
        cavity = trimesh.boolean.union([cavity, s], engine="manifold")

    half = trimesh.boolean.difference([body, cavity], engine="manifold")

    # Alignment pins / holes on the flange
    pin_positions = pick_pin_positions(flange_outer, outer_top)
    if len(pin_positions) < 4:
        print(f"    ⚠️  Only {len(pin_positions)} pin positions found")

    if side == 'A':
        for (x, y) in pin_positions:
            pin = trimesh.creation.cylinder(
                radius=PIN_DIA / 2, height=PIN_LEN, sections=24
            )
            pin.apply_translation([x, y, H + PIN_LEN / 2])
            half = trimesh.boolean.union([half, pin], engine="manifold")
    elif side == 'B':
        hole_r = PIN_DIA / 2 + PIN_CLEARANCE
        hole_depth = PIN_LEN + PIN_CLEARANCE
        for (x, y) in pin_positions:
            hole = trimesh.creation.cylinder(
                radius=hole_r, height=hole_depth + 0.2, sections=24
            )
            # Hole opens at the parting plane (z = H) and goes down into flange
            hole.apply_translation([x, y, H - (hole_depth + 0.2) / 2 + 0.1])
            half = trimesh.boolean.difference([half, hole], engine="manifold")
    else:
        raise ValueError(f"side must be 'A' or 'B', got {side!r}")

    half.fix_normals()

    b = half.bounds
    print(f"    Outer:  {b[1][0]-b[0][0]:.0f}×{b[1][1]-b[0][1]:.0f}×{b[1][2]-b[0][2]:.0f} mm")
    print(f"    Cavity: bottom {cat_poly.bounds[2]-cat_poly.bounds[0]:.0f}×"
          f"{cat_poly.bounds[3]-cat_poly.bounds[1]:.0f} mm → "
          f"top +{2*draft_offset:.1f} mm each axis")
    print(f"    Flange: {FLANGE_W:.0f} mm wide × {FLANGE_T:.0f} mm thick")
    print(f"    Pins:   {len(pin_positions)} × φ{PIN_DIA:.0f} mm "
          f"({'pegs ↑' if side == 'A' else 'holes ↓'})")
    print(f"    Watertight: {half.is_watertight}")
    return half


# ── Main ─────────────────────────────────────────────────

def main():
    print("=" * 56)
    print("  🛁  Octocat Bath Bomb — Clamshell Mold Generator")
    print("=" * 56)

    here = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(here, "GitHub-Mark-ea2971cee799.png")
    out_a = os.path.join(here, "mold_cat_clamshell_A.stl")
    out_b = os.path.join(here, "mold_cat_clamshell_B.stl")

    cat = extract_cat(img_path)
    half_a = build_half(cat, side='A')
    half_b = build_half(cat, side='B')

    half_a.export(out_a)
    half_b.export(out_b)

    print(f"\n    ✅ {os.path.basename(out_a)}  ({len(half_a.vertices)} verts, {len(half_a.faces)} faces)")
    print(f"    ✅ {os.path.basename(out_b)}  ({len(half_b.vertices)} verts, {len(half_b.faces)} faces)")
    print(f"\n{'='*56}")
    print("  ✨  Print both halves, line each cavity, fill, clamp,")
    print("      let dry, then unclamp and pop the bath bomb out!")
    print(f"{'='*56}")


if __name__ == "__main__":
    main()
