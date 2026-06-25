"""Shared pytest fixtures + headless Matplotlib setup for the test suite."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # force a non-interactive backend before any test imports pyplot

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402

from som_multimodal.config import DEFAULT_FEATURES, RunConfig  # noqa: E402


@pytest.fixture
def tiny_csv(tmp_path):
    """A small synthetic CSV with the real schema (8 features + id + metadata)."""
    rng = np.random.default_rng(0)
    n = 30
    data = {"Row": list(range(1, n + 1))}
    for col in DEFAULT_FEATURES:
        data[col] = rng.normal(size=n)
    data["mammal"] = ["h"] * (n // 2) + ["o"] * (n - n // 2)
    data["position"] = ["outer", "middle", "inner"] * (n // 3)
    path = tmp_path / "tiny.csv"
    pd.DataFrame(data).to_csv(path, index=False)
    return str(path)


@pytest.fixture
def tiny_cfg(tiny_csv, tmp_path):
    """A fast RunConfig: small map + few epochs, writing into a temp output dir."""
    return RunConfig(
        data_csv=tiny_csv,
        mapsize=(5, 5),
        n_clusters=3,
        rough_len=2,
        finetune_len=2,
        output_dir=str(tmp_path / "out"),
        heatmap_size=(4, 8),
        umatrix_size=(4, 4),
    )
