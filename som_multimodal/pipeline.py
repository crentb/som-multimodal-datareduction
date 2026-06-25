"""
End-to-end driver: train the SOM, then render its figures, in one command.

This stitches :func:`som_multimodal.train.train_som` and
:func:`som_multimodal.visualize.visualize_som` into the single reproducible step
that turns a raw multimodal CSV into a clustered SOM and its standard figures.

Usage:
    python -m som_multimodal.pipeline --data-csv data/general_main.csv --n-clusters 6
"""

from __future__ import annotations

import argparse

from som_multimodal.config import RunConfig, add_common_cli_args, config_from_args
from som_multimodal.train import train_som
from som_multimodal.visualize import visualize_som


def run_pipeline(cfg: RunConfig) -> dict:
    """Train then visualize. Returns ``{"metrics": ..., "outputs": ...}``."""
    _sm, metrics = train_som(cfg)
    outputs = visualize_som(cfg)
    return {"metrics": metrics, "outputs": outputs}


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Train a SOM and render its figures end-to-end.")
    add_common_cli_args(parser)
    args = parser.parse_args(argv)
    cfg = config_from_args(args)

    result = run_pipeline(cfg)
    m = result["metrics"]
    print("Pipeline complete.")
    print(f"  topographic error  : {m['topographic_error']:.4f}")
    print(f"  quantization error : {m['quantization_error']:.4f}")
    print(f"  codebook           : {m['codebook_file']}")
    print("  figures:")
    for name, path in result["outputs"].items():
        print(f"    {name:24s} -> {path}")


if __name__ == "__main__":
    main()
