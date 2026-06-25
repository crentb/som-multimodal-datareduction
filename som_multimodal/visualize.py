"""
Render the standard SOM figures from a trained-codebook HDF5 file.

Headless replacement for the original ``SOM_Visualization_CR`` notebook (which
drove plotting through ipywidgets). Given a codebook written by ``train``, it
rebuilds the SOM, clusters the codebook with k-means, and writes three figures:

  1. component-plane heat maps   -- one panel per feature, k-means borders overlaid
  2. cluster-category map        -- nodes coloured by cluster, points by a metadata
                                    column (e.g. ``mammal``)
  3. U-matrix                    -- unified distance matrix with data points

Usage:
    python -m som_multimodal.visualize --output-dir outputs --n-clusters 6
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: render straight to image files, never open a GUI window

import matplotlib.pyplot as plt  # noqa: E402  (must follow matplotlib.use)

from som_multimodal._vendor.sompy.sompy import SOMFactory  # noqa: E402
from som_multimodal.config import RunConfig, add_common_cli_args, config_from_args  # noqa: E402
from som_multimodal.engine import (  # noqa: E402
    UMatrixTFP,
    ViewTFP,
    clusteringmap_category,
    kmeans_clust,
)
from som_multimodal.io import load_som_h5  # noqa: E402


def _rebuild_som(codebook, mapsize, data_df, columns, normalization, initialization):
    """Reconstruct a SOMPY map and inject the saved (already-trained) codebook.

    SOMPY has no "load" path, so we rebuild the map over the same data + grid and
    overwrite its codebook with the stored matrix -- this reproduces the original
    notebook's load step exactly.
    """
    sm = SOMFactory.build(
        data_df[columns].to_numpy(dtype=float),
        mapsize=tuple(mapsize),
        normalization=normalization,
        initialization=initialization,
        component_names=columns,
    )
    sm.codebook.matrix = codebook.values
    return sm


def visualize_som(cfg: RunConfig) -> dict[str, str]:
    """Render the three standard figures for the codebook at ``cfg.codebook_path``.

    Returns a mapping of figure-name -> written file path.
    """
    codebook, mapsize, data_df, columns, specimen_ids = load_som_h5(cfg.codebook_path)
    data_df = data_df.copy()
    data_df[cfg.id_column] = specimen_ids

    sm = _rebuild_som(codebook, mapsize, data_df, columns, cfg.normalization, cfg.initialization)
    cl_labels = kmeans_clust(sm, cfg.n_clusters, seed=cfg.seed)

    out = Path(cfg.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    cmap = plt.get_cmap("RdYlBu_r")
    outputs: dict[str, str] = {}

    # 1) component-plane heat maps (one panel per feature) with cluster borders
    planes_png = out / "component_planes.png"
    view = ViewTFP(*cfg.heatmap_size, "", stdev_colorscale_coeff=1.0, text_size=14)
    view.knee_value = 0.0
    view.show(
        sm,
        cl_labels,
        col_sz=1,
        which_dim="all",
        desnormalize=True,
        col_norm="mean",
        cmap=cmap,
        savepath=str(planes_png),
        isOutHtmap=True,
    )
    outputs["component_planes"] = str(planes_png)

    # 2) cluster-category map: nodes coloured by k-means cluster, points by metadata
    if cfg.label_column in data_df.columns:
        catmap_png = out / f"cluster_map_by_{cfg.label_column}.png"
        clusteringmap_category(
            None,  # engine signature keeps a leading axis arg; it makes its own figure
            sm,
            cfg.n_clusters,
            data_df,
            cfg.label_column,
            data_df[cfg.id_column],
            str(catmap_png),
        )
        outputs[f"cluster_map_by_{cfg.label_column}"] = str(catmap_png)

    # 3) U-matrix (unified distance matrix) with projected data points
    umat_png = out / "umatrix.png"
    umat_view = UMatrixTFP(*cfg.umatrix_size, "U-matrix")
    umat_view.show(
        sm,
        data_df,
        data_df,
        str(umat_png),
        cmap=cmap,
        show_data=True,
        contooor=True,
        labels=False,
        isOutUmat=True,
    )
    outputs["umatrix"] = str(umat_png)

    plt.close("all")
    return outputs


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Render SOM figures from a trained codebook .h5.")
    add_common_cli_args(parser)
    args = parser.parse_args(argv)
    cfg = config_from_args(args)

    outputs = visualize_som(cfg)
    print("Figures written:")
    for name, path in outputs.items():
        print(f"  {name:24s} -> {path}")


if __name__ == "__main__":
    main()
