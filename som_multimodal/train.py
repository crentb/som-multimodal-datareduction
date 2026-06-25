"""
Train a self-organizing map on the multimodal CSV and save its codebook.

This is the headless, single-command replacement for the original
``SOM_Analysis_CR`` Jupyter notebook (whose training was driven by ipywidgets
buttons). It builds a SOMPY map over the chosen feature columns, trains it,
reports the topographic and quantization errors, and writes the trained codebook
(plus the source data) to an HDF5 file that ``visualize`` consumes.

Usage:
    python -m som_multimodal.train --data-csv data/general_main.csv
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from som_multimodal._vendor.sompy.sompy import SOMFactory
from som_multimodal.config import RunConfig, add_common_cli_args, config_from_args
from som_multimodal.io import save_som_h5


def train_som(cfg: RunConfig):
    """Build + train a SOM per ``cfg`` and persist it. Returns ``(sm, metrics)``."""
    df = pd.read_csv(cfg.data_csv)

    missing = [c for c in cfg.feature_columns if c not in df.columns]
    if missing:
        raise ValueError(f"feature columns not found in {cfg.data_csv}: {missing}")

    # SOM is trained only on the numeric feature matrix; metadata rides along in the .h5.
    features = df[cfg.feature_columns].to_numpy(dtype=float)

    sm = SOMFactory.build(
        features,
        mapsize=cfg.mapsize,
        normalization=cfg.normalization,
        initialization=cfg.initialization,
        component_names=cfg.feature_columns,
    )
    sm.train(
        n_job=1,
        verbose=None,
        train_rough_len=cfg.rough_len,
        train_finetune_len=cfg.finetune_len,
    )

    # Standard SOM quality metrics: topographic error (neighbour preservation) and
    # quantization error (mean distance from each sample to its best-matching unit).
    # Mixed value types (floats, ints, and a path string), so annotate explicitly.
    metrics: dict[str, float | str] = {
        "topographic_error": float(sm.calculate_topographic_error()),
        "quantization_error": float(np.mean(sm._bmu[1])),
        "n_nodes": int(sm.codebook.matrix.shape[0]),
        "n_samples": int(features.shape[0]),
        "n_features": int(features.shape[1]),
    }

    path = save_som_h5(cfg.codebook_path, sm, df, cfg.feature_columns, cfg.mapsize, cfg.id_column)
    metrics["codebook_file"] = str(path)
    return sm, metrics


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="Train a SOM on a multimodal CSV and save its codebook."
    )
    add_common_cli_args(parser)
    args = parser.parse_args(argv)
    cfg = config_from_args(args)

    _, metrics = train_som(cfg)
    print("SOM trained.")
    print(f"  samples x features : {metrics['n_samples']} x {metrics['n_features']}")
    print(f"  map nodes          : {metrics['n_nodes']}  (mapsize {cfg.mapsize})")
    print(f"  topographic error  : {metrics['topographic_error']:.4f}")
    print(f"  quantization error : {metrics['quantization_error']:.4f}")
    print(f"  codebook written   : {metrics['codebook_file']}")


if __name__ == "__main__":
    main()
