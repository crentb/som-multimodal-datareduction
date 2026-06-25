"""Training builds a SOM, reports finite errors, and writes a codebook."""

import math
from pathlib import Path

from som_multimodal.train import train_som


def test_train_som(tiny_cfg):
    sm, metrics = train_som(tiny_cfg)

    assert {"topographic_error", "quantization_error", "codebook_file", "n_nodes"} <= set(metrics)
    assert metrics["n_nodes"] == 25  # 5x5 grid
    assert metrics["n_samples"] == 30
    assert metrics["n_features"] == 8
    assert math.isfinite(metrics["topographic_error"])
    assert math.isfinite(metrics["quantization_error"])
    assert metrics["quantization_error"] >= 0.0

    assert Path(metrics["codebook_file"]).exists()
    assert sm.codebook.matrix.shape == (25, 8)
