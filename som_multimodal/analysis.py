"""
Cluster-count diagnostics for the trained SOM codebook.

Choosing ``k`` for the k-means step over the SOM nodes is the one subjective knob
in the workflow. This module provides the two standard, label-free criteria --
the elbow (within-cluster sum of squares vs. k) and the silhouette score vs. k --
computed directly on the trained codebook vectors, and writes a two-panel figure
plus a suggested k (the silhouette maximizer).

Usage:
    python -m som_multimodal.analysis --output-dir outputs --k-min 2 --k-max 12
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.cluster import KMeans  # noqa: E402
from sklearn.metrics import silhouette_score  # noqa: E402

from som_multimodal.config import RunConfig, add_common_cli_args, config_from_args  # noqa: E402
from som_multimodal.io import load_som_h5  # noqa: E402


def cluster_diagnostics(cfg: RunConfig, k_min: int = 2, k_max: int = 12) -> dict:
    """Compute elbow + silhouette over k for the codebook; write a figure.

    Returns a dict with the per-k inertias/silhouettes, the suggested k, and the
    output figure path.
    """
    codebook, _mapsize, _data_df, _columns, _ids = load_som_h5(cfg.codebook_path)
    nodes = codebook.values

    ks = list(range(k_min, k_max + 1))
    inertias: list[float] = []
    silhouettes: list[float] = []
    for k in ks:
        labels = KMeans(n_clusters=k, n_init=10, random_state=cfg.seed).fit_predict(nodes)
        inertias.append(
            float(KMeans(n_clusters=k, n_init=10, random_state=cfg.seed).fit(nodes).inertia_)
        )
        # silhouette is undefined for k=1; ks starts at 2 so this is always valid
        silhouettes.append(float(silhouette_score(nodes, labels)))

    suggested_k = int(ks[int(np.argmax(silhouettes))])

    out = Path(cfg.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    fig_path = out / "cluster_diagnostics.png"

    fig, (ax_elbow, ax_sil) = plt.subplots(1, 2, figsize=(11, 4))
    ax_elbow.plot(ks, inertias, "o-")
    ax_elbow.set_xlabel("number of clusters k")
    ax_elbow.set_ylabel("within-cluster SSE (inertia)")
    ax_elbow.set_title("Elbow")
    ax_sil.plot(ks, silhouettes, "o-")
    ax_sil.axvline(suggested_k, color="r", ls="--", lw=1, label=f"max @ k={suggested_k}")
    ax_sil.set_xlabel("number of clusters k")
    ax_sil.set_ylabel("mean silhouette score")
    ax_sil.set_title("Silhouette")
    ax_sil.legend()
    fig.tight_layout()
    fig.savefig(fig_path, dpi=150)
    plt.close(fig)

    return {
        "k": ks,
        "inertia": inertias,
        "silhouette": silhouettes,
        "suggested_k": suggested_k,
        "figure": str(fig_path),
    }


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="Elbow + silhouette diagnostics for the SOM codebook."
    )
    add_common_cli_args(parser)
    parser.add_argument("--k-min", type=int, default=2, help="smallest k to evaluate")
    parser.add_argument("--k-max", type=int, default=12, help="largest k to evaluate")
    args = parser.parse_args(argv)
    cfg = config_from_args(args)

    result = cluster_diagnostics(cfg, k_min=args.k_min, k_max=args.k_max)
    print("Cluster diagnostics:")
    for k, ss in zip(result["k"], result["silhouette"]):
        print(f"  k={k:2d}  silhouette={ss:.3f}")
    print(f"Suggested k (max silhouette): {result['suggested_k']}")
    print(f"Figure written: {result['figure']}")


if __name__ == "__main__":
    main()
