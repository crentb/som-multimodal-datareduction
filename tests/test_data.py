"""The shipped enamel dataset matches the documented schema."""

from pathlib import Path

import pandas as pd
import pytest

from som_multimodal.config import DEFAULT_FEATURES, RunConfig
from som_multimodal.pipeline import run_pipeline

DATA = Path(__file__).resolve().parents[1] / "data" / "general_main.csv"


def test_shipped_dataset_schema():
    assert DATA.exists()
    df = pd.read_csv(DATA)
    assert len(df) == 138
    for col in DEFAULT_FEATURES:
        assert col in df.columns, f"missing feature column: {col}"
    for meta in ("Row", "mammal", "position"):
        assert meta in df.columns


@pytest.mark.slow
def test_real_data_full_pipeline(tmp_path):
    """Full-size SOM on the real dataset (skipped in default CI; run with -m slow)."""
    cfg = RunConfig(
        data_csv=str(DATA),
        mapsize=(25, 25),
        n_clusters=6,
        output_dir=str(tmp_path),
    )
    result = run_pipeline(cfg)
    assert result["metrics"]["n_samples"] == 138
    assert result["metrics"]["n_nodes"] == 625
