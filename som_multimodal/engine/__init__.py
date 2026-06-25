"""
``som_multimodal.engine`` -- vendored, MODIFIED SOM visualization/clustering engine.

This subpackage carries a modified version of the ``tfprop_sompy`` visualization
layer (Kikugawa & Nishimura, Tohoku University) on top of the vendored SOMPY
library (Moosavi / sevamoo). Both upstreams are Apache-2.0. See
``ACKNOWLEDGMENTS.md`` (this directory) and the repository ``NOTICE`` for the full
provenance and the list of Cameron Renteria's modifications.

Only the symbols re-exported below are part of this package's public surface; the
rest of the upstream module is kept for fidelity but is not API-stable.
"""

from som_multimodal.engine.tfprop_vis import (
    UMATRIX_SIZE,
    KM_SEED,
    POSMAP_SIZE,
    UMatrixTFP,
    ViewTFP,
    clusteringmap_category,
    dataframe_to_coords,
    kmeans_clust,
    render_cluster_borders_to_axes,
    render_points_to_axes,
    render_posmap_to_axes,
    show_posmap,
)

__all__ = [
    "kmeans_clust",
    "ViewTFP",
    "UMatrixTFP",
    "clusteringmap_category",
    "render_cluster_borders_to_axes",
    "render_points_to_axes",
    "render_posmap_to_axes",
    "dataframe_to_coords",
    "show_posmap",
    "KM_SEED",
    "POSMAP_SIZE",
    "UMATRIX_SIZE",
]
