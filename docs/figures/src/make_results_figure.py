"""Render the README results figure for som-multimodal-datareduction.

Purpose
    One panel figure of what the pipeline produces on the bundled enamel dataset
    (data/general_main.csv: 138 measurements, 8 features):

      (a) component planes -- one map per property over the trained 25 x 25 SOM grid,
          with the k-means cluster borders drawn in gold;
      (b) U-matrix -- the mean distance from each node to its neighbours (high values mark
          cluster boundaries), with every measurement placed on its best-matching node;
      (c) cluster map -- the k-means clusters of the codebook, with the measurements marked
          by species group (human versus other mammals).

    It reuses the package's own loading, SOM-rebuild and k-means calls, so the clusters are
    identical to those in the CLI's component_planes.png and cluster_map_by_mammal.png; only
    the styling differs (the palette of the README overview, docs/figures/src/som_pipeline.tex).
    Every map is drawn in the CLI's orientation (x = SOM row, y = SOM column, origin at the
    bottom), so the panels line up with the figures `som-pipeline` writes.

Inputs
    --output-dir   directory holding som_codebook.h5 from a prior run of
                   `som-pipeline --data-csv data/general_main.csv --n-clusters 6`
    --n-clusters   k for k-means over the codebook (default 6, as in the quick start)
    --out          PNG path (default: docs/figures/som_results.png)

Output
    A 300 dpi PNG, 12 in x 5.35 in (3600 x 1605 px), sized so that GitHub's ~1000 px README column
    shows its smallest labels at roughly 10-11 px.

Usage (from the repository root)
    som-pipeline --data-csv data/general_main.csv --n-clusters 6 --output-dir outputs
    python docs/figures/src/make_results_figure.py --output-dir outputs
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: render straight to a file, never open a window

import matplotlib.pyplot as plt  # noqa: E402  (must follow matplotlib.use)
import numpy as np  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, ListedColormap  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from som_multimodal._vendor.sompy.visualization.umatrix import UMatrixView  # noqa: E402
from som_multimodal.config import RunConfig  # noqa: E402
from som_multimodal.engine import kmeans_clust  # noqa: E402
from som_multimodal.io import load_som_h5  # noqa: E402
from som_multimodal.visualize import _rebuild_som  # noqa: E402

# ---- palette: the same hex values as the README overview (som_pipeline.tex) --------------------
NAVY, GOLD, INK, RULE = "#1E3252", "#B8894A", "#222222", "#8C8C8C"
# Sequential ramps from light paper: navy for property values, gold-brown for the U-matrix, so
# the two kinds of map cannot be confused at a glance.
PLANE_CMAP = LinearSegmentedColormap.from_list("planes", ["#F6F3EC", "#C9CED6", "#7586A2", NAVY])
UMAT_CMAP = LinearSegmentedColormap.from_list("umat", ["#F6F3EC", "#E6D5B5", "#C99B5C", "#7A5426"])
# Light cluster fills (navy, slate and gold tints): distinct from one another, yet pale enough
# that the species markers in panel (c) stay readable on top of them.
CLUSTER_FILLS = ["#D5DDEA", "#EADCC3", "#B9C3D3", "#F3EBDC", "#DADDE2", "#E2CDA5", "#C8D0C0"]

# Display names for the eight feature columns (data/README.md documents each one). Two-line
# names keep every title inside its 1.3 in panel.
FEATURE_NAMES = {
    "modulus": "Elastic\nmodulus",
    "hardness": "Hardness",
    "carb": "Carbonate\n(Raman)",
    "crys": "Crystallinity\n(Raman)",
    "fluo": "Fluorescence\n(Raman)",
    "depth": "Depth from\nsurface",
    "kc": "Fracture\ntoughness",
    "b": "R-curve\nparameter b",
}
# Species groups of the `mammal` column: display label, marker colour, marker shape.
SPECIES = {"h": ("Human", NAVY, "o"), "o": ("Other mammals", GOLD, "D")}

FIG_W, FIG_H = 12.0, 5.35  # figure size in inches; every axes position below is in inches


def axes_at(fig, left, bottom, width, height):
    """Add an axes at an absolute position given in inches (converted to figure fractions)."""
    return fig.add_axes([left / FIG_W, bottom / FIG_H, width / FIG_W, height / FIG_H])


def range_label(value, span):
    """Format a range-bar end: 3 significant figures, with near-zero values printed as 0."""
    return "0" if abs(value) < 1e-3 * max(span, 1e-12) else f"{value:.3g}"


def cluster_borders(labels_grid):
    """Line segments separating neighbouring SOM nodes that belong to different clusters.

    `labels_grid` is the array exactly as displayed: imshow draws element [i, j] as a unit cell
    centred on (x = j, y = i), so a border between horizontal neighbours is the vertical edge
    at x = j + 0.5, and a border between vertical neighbours is the horizontal edge at
    y = i + 0.5.
    """
    rows, cols = labels_grid.shape
    segments = []
    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols and labels_grid[r, c] != labels_grid[r, c + 1]:
                segments.append([(c + 0.5, r - 0.5), (c + 0.5, r + 0.5)])
            if r + 1 < rows and labels_grid[r, c] != labels_grid[r + 1, c]:
                segments.append([(c - 0.5, r + 0.5), (c + 0.5, r + 0.5)])
    return segments


def style_map_axes(ax):
    """Strip ticks from a map panel and give it a thin grey frame."""
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor(RULE)
        spine.set_linewidth(0.6)


def main(argv=None) -> None:
    # ---- command line ------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--output-dir", default="outputs", help="directory with som_codebook.h5")
    parser.add_argument("--n-clusters", type=int, default=6, help="k for k-means (default 6)")
    parser.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parents[1] / "som_results.png"),
        help="PNG to write (default: docs/figures/som_results.png)",
    )
    args = parser.parse_args(argv)
    cfg = RunConfig(output_dir=args.output_dir, n_clusters=args.n_clusters)

    # ---- load the trained map exactly as the package's visualize step does ---------------------
    codebook, mapsize, data_df, columns, _ids = load_som_h5(cfg.codebook_path)
    sm = _rebuild_som(codebook, mapsize, data_df, columns, cfg.normalization, cfg.initialization)
    rows, cols = mapsize
    # k-means over the codebook with the package's seed (555, parity with the 2022 study).
    labels_grid = np.asarray(kmeans_clust(sm, cfg.n_clusters, seed=cfg.seed)).reshape(rows, cols)
    # Displayed grids are transposed (x = SOM row, y = SOM column), as in visualize.py.
    borders = cluster_borders(labels_grid.T)

    # Codebook back in the measurement units: SOMPY trains on z-scored ("var") features.
    planes = sm._normalizer.denormalize_by(sm.data_raw, sm.codebook.matrix)
    # U-matrix: mean distance from each node to its immediate neighbours.
    umatrix = np.asarray(UMatrixView(0, 0, "").build_u_matrix(sm, distance=1)).reshape(rows, cols)
    # Best-matching node of every measurement (in the normalised space the map was trained in).
    bmu_nodes = np.asarray(sm.find_bmu(sm._data, njb=1))[0].astype(int)
    bmu_row, bmu_col = bmu_nodes // cols, bmu_nodes % cols
    # Fixed-seed jitter inside each node, so measurements sharing a node stay visible.
    rng = np.random.default_rng(0)
    jx, jy = rng.uniform(-0.3, 0.3, (2, len(bmu_nodes)))
    species = data_df[cfg.label_column].astype(str).to_numpy()

    # ---- figure ------------------------------------------------------------------------------
    plt.rcParams.update(
        {
            "font.family": ["Helvetica", "Arial", "DejaVu Sans"],
            "font.size": 10,
            "text.color": INK,
            "axes.labelcolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
        }
    )
    fig = plt.figure(figsize=(FIG_W, FIG_H), facecolor="white")

    # (a) component planes: 2 rows x 4 columns of 1.3 in maps, each with a range bar beneath.
    fig.text(
        0.3 / FIG_W,
        5.07 / FIG_H,
        "(a) Component planes: one map per property",
        fontsize=12.5,
        va="baseline",
    )
    size, gap_x = 1.3, 0.28
    for j, name in enumerate(columns):
        r, c = divmod(j, 4)
        left = 0.3 + c * (size + gap_x)
        bottom = 3.17 if r == 0 else 0.67
        ax = axes_at(fig, left, bottom, size, size)
        values = planes[:, j].reshape(rows, cols)
        image = ax.imshow(values.T, cmap=PLANE_CMAP, interpolation="nearest", origin="lower")
        ax.add_collection(LineCollection(borders, colors=GOLD, linewidths=0.9))
        style_map_axes(ax)
        ax.set_title(FEATURE_NAMES.get(name, name), fontsize=10, pad=4, linespacing=1.05)
        # Range bar: only the minimum and maximum codebook values, to show each property's span.
        cax = axes_at(fig, left + 0.08, bottom - 0.2, size - 0.16, 0.07)
        bar = fig.colorbar(image, cax=cax, orientation="horizontal")
        lo, hi = float(values.min()), float(values.max())
        bar.set_ticks([lo, hi])
        bar.set_ticklabels([range_label(lo, hi - lo), range_label(hi, hi - lo)])
        bar.ax.tick_params(labelsize=8.5, length=2, pad=1.5, width=0.6)
        bar.outline.set_linewidth(0.5)
        bar.outline.set_edgecolor(RULE)

    # (b) U-matrix with every measurement on its best-matching node.
    fig.text(6.95 / FIG_W, 5.07 / FIG_H, "(b) U-matrix", fontsize=12.5, va="baseline")
    ax_u = axes_at(fig, 6.95, 2.4, 2.3, 2.3)
    image_u = ax_u.imshow(umatrix.T, cmap=UMAT_CMAP, interpolation="nearest", origin="lower")
    ax_u.scatter(bmu_row + jx, bmu_col + jy, s=7, color=INK, edgecolors="white", linewidths=0.3)
    style_map_axes(ax_u)
    cax_u = axes_at(fig, 6.95 + 0.15, 2.15, 2.0, 0.07)
    bar_u = fig.colorbar(image_u, cax=cax_u, orientation="horizontal")
    bar_u.ax.tick_params(labelsize=8.5, length=2, pad=1.5, width=0.6)
    bar_u.outline.set_linewidth(0.5)
    bar_u.outline.set_edgecolor(RULE)
    bar_u.set_label("mean distance to neighbouring nodes", fontsize=9, labelpad=2)

    # (c) cluster map: k-means clusters as pale fills, measurements marked by species group.
    fig.text(
        9.55 / FIG_W,
        5.07 / FIG_H,
        f"(c) Clusters (k = {cfg.n_clusters}) by species",
        fontsize=12.5,
        va="baseline",
    )
    ax_c = axes_at(fig, 9.55, 2.4, 2.3, 2.3)
    ax_c.imshow(
        labels_grid.T,
        cmap=ListedColormap(CLUSTER_FILLS[: cfg.n_clusters]),
        interpolation="nearest",
        origin="lower",
    )
    ax_c.add_collection(LineCollection(borders, colors=GOLD, linewidths=1.3))
    for code, (label, colour, marker) in SPECIES.items():
        hit = species == code
        ax_c.scatter(
            bmu_row[hit] + jx[hit],
            bmu_col[hit] + jy[hit],
            s=13 if marker == "o" else 11,
            marker=marker,
            color=colour,
            edgecolors="white",
            linewidths=0.35,
        )
    style_map_axes(ax_c)

    # Legend and dataset facts under panels (b) and (c).
    handles = [
        Line2D(
            [],
            [],
            ls="none",
            marker=SPECIES[code][2],
            color=SPECIES[code][1],
            markeredgecolor="white",
            markersize=6.5,
            label=f"{SPECIES[code][0]} ({int((species == code).sum())})",
        )
        for code in SPECIES
    ]
    handles.append(Line2D([], [], color=GOLD, lw=1.8, label="k-means cluster border"))
    fig.legend(
        handles=handles,
        loc="upper left",
        bbox_to_anchor=(9.5 / FIG_W, 2.2 / FIG_H),
        frameon=False,
        fontsize=9.5,
        handlelength=1.6,
        borderaxespad=0,
        labelspacing=0.45,
    )
    facts = (
        f"{len(species)} measurements · {len(columns)} features\n"
        f"{rows} × {cols} SOM, z-scored features\n"
        f"k-means on the codebook, seed {cfg.seed}"
    )
    fig.text(6.95 / FIG_W, 1.05 / FIG_H, facts, fontsize=9.5, va="top", linespacing=1.45, color=INK)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300, facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
