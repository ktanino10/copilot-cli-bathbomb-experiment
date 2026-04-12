#!/usr/bin/env python3
"""
GitHub Octocat Bath Bomb — Cat-shaped Container Mold Generator

Generates a single-sided cat-shaped container mold for 3D printing.
Features:
  - 5° draft angle for easy release
  - R3mm fillets on all corners
  - 4mm walls and floor
  - Sized to fit a 90×55mm photo inside
"""

import os
import math
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation, label
from skimage import measure
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity
import trimesh

# ── Dimensions (mm) ──────────────────────────────────────
WALL       =   4.0   # wall thickness
FLOOR      =   4.0   # floor thickness
DEPTH      =  25.0   # cavity depth
DRAFT_DEG  =   5.0   # draft angle (top wider than bottom)
FILLET_R   =   3.0   # corner rounding radius
PHOTO_LONG =  90.0   # photo long side (mm)
PHOTO_SHORT=  55.0   # photo short side (mm)
NSEG       = 128


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

    # Scale: circle diameter → 130mm, flip Y
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

    # Ensure photo fits (need ≥ PHOTO_LONG + 2mm in at least one axis)
    bx0, by0, bx1, by1 = poly.bounds
    w, h = bx1 - bx0, by1 - by0
    needed = PHOTO_LONG + 2
    if max(w, h) < needed:
        s = needed / max(w, h)
        poly = affinity.scale(poly, s, s, origin=(0, 0))
        bx0, by0, bx1, by1 = poly.bounds
        w, h = bx1 - bx0, by1 - by0
        print(f"    Scaled to {w:.0f}×{h:.0f} mm (photo fit)")

    holes = len(list(poly.interiors))
    print(f"    Cat: {w:.0f}×{h:.0f} mm, {len(poly.exterior.coords)} verts, {holes} holes")
    return poly


# ── Mold generation ─────────────────────────────────────

def build_mold(cat_poly):
    """Build a cat-shaped container mold with draft angle."""
    print("\n🐱  Building cat-shaped container mold …")

    draft_offset = DEPTH * math.tan(math.radians(DRAFT_DEG))
    print(f"    Draft offset at rim: {draft_offset:.1f} mm")

    # Outer shell uses the TOP (widest) cavity shape + WALL
    cavity_top = cat_poly.buffer(draft_offset)
    outer_top = cavity_top.buffer(WALL)
    for p in [cavity_top, outer_top]:
        if isinstance(p, MultiPolygon):
            p = max(p.geoms, key=lambda g: g.area)

    if isinstance(outer_top, MultiPolygon):
        outer_top = max(outer_top.geoms, key=lambda g: g.area)

    # Outer solid (full height)
    outer = trimesh.creation.extrude_polygon(outer_top, FLOOR + DEPTH)

    # Tapered cavity: stack slices from bottom (narrow) to top (wide)
    n_slices = 10
    slice_h = DEPTH / n_slices
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

    # Mold = outer − cavity
    mold = trimesh.boolean.difference([outer, cavity], engine="manifold")
    mold.fix_normals()

    b = mold.bounds
    cw = cat_poly.bounds
    print(f"    Outer: {b[1][0]-b[0][0]:.0f}×{b[1][1]-b[0][1]:.0f}×{b[1][2]-b[0][2]:.0f} mm")
    print(f"    Cavity bottom: {cw[2]-cw[0]:.0f}×{cw[3]-cw[1]:.0f} mm")
    print(f"    Cavity top:    {cw[2]-cw[0]+2*draft_offset:.0f}×{cw[3]-cw[1]+2*draft_offset:.0f} mm")
    print(f"    Wall: {WALL:.0f} mm, Floor: {FLOOR:.0f} mm")
    print(f"    Draft: {DRAFT_DEG:.0f}°, Fillet: R{FILLET_R:.0f} mm")
    print(f"    Watertight: {mold.is_watertight}")
    return mold


# ── Main ─────────────────────────────────────────────────

def main():
    print("=" * 52)
    print("  🛁  Octocat Bath Bomb — Mold Generator")
    print("=" * 52)

    here = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(here, "GitHub-Mark-ea2971cee799.png")
    out_path = os.path.join(here, "mold_cat_container.stl")

    cat = extract_cat(img_path)
    mold = build_mold(cat)
    mold.export(out_path)

    print(f"\n    ✅ {os.path.basename(out_path)}")
    print(f"       ({len(mold.vertices)} verts, {len(mold.faces)} faces)")
    print(f"\n{'='*52}")
    print("  ✨  Open in your slicer and print!")
    print(f"{'='*52}")


if __name__ == "__main__":
    main()
