#!/usr/bin/env python3
"""Generate top-down PNG preview images of each mold STL.

These are embedded in the README so visitors can see the mold geometry
without relying on GitHub's (currently flaky) inline STL 3D viewer.
"""
from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


STL_FILES = [
    ("mold_cat_clamshell_A.stl", "Clamshell — Half A (with pegs)",   "#7AA8FF"),
    ("mold_cat_clamshell_B.stl", "Clamshell — Half B (with holes)",  "#FFB37A"),
    ("mold_cat_container.stl",          "v1 Container",          "#9CD89C"),
    ("mold_cat_container_mirrored.stl", "v1 Container (mirror)", "#D89C9C"),
]


def render_preview(stl_path: str, out_path: str, title: str, color: str) -> None:
    print(f"  rendering {stl_path} → {out_path}")
    mesh = trimesh.load(stl_path)
    verts = mesh.vertices
    faces = mesh.faces

    fig = plt.figure(figsize=(6, 6), dpi=120)
    ax = fig.add_subplot(111, projection="3d")

    triangles = verts[faces]
    poly = Poly3DCollection(
        triangles,
        facecolor=color,
        edgecolor=(0, 0, 0, 0.15),
        linewidths=0.2,
    )
    ax.add_collection3d(poly)

    mins = verts.min(axis=0)
    maxs = verts.max(axis=0)
    spans = maxs - mins
    max_span = max(spans) * 0.55
    centers = (maxs + mins) / 2.0
    ax.set_xlim(centers[0] - max_span, centers[0] + max_span)
    ax.set_ylim(centers[1] - max_span, centers[1] + max_span)
    ax.set_zlim(centers[2] - max_span, centers[2] + max_span)

    try:
        ax.set_box_aspect((1, 1, 1))
    except Exception:
        pass

    ax.view_init(elev=35, azim=-60)
    ax.set_title(f"{title}\n{spans[0]:.1f} × {spans[1]:.1f} × {spans[2]:.1f} mm",
                 fontsize=11)
    ax.set_xlabel("X (mm)", fontsize=8)
    ax.set_ylabel("Y (mm)", fontsize=8)
    ax.set_zlabel("Z (mm)", fontsize=8)
    ax.tick_params(labelsize=7)

    plt.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    out_dir = "previews"
    os.makedirs(out_dir, exist_ok=True)
    print(f"Writing previews to ./{out_dir}/")
    for stl_path, title, color in STL_FILES:
        if not os.path.exists(stl_path):
            print(f"  ⚠️  skip (missing): {stl_path}")
            continue
        out_path = os.path.join(out_dir, stl_path.replace(".stl", ".png"))
        render_preview(stl_path, out_path, title, color)
    print("Done.")


if __name__ == "__main__":
    main()
