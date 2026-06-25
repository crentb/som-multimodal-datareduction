"""End-to-end train->visualize produces the expected non-empty figures."""

from pathlib import Path

from som_multimodal.analysis import cluster_diagnostics
from som_multimodal.pipeline import run_pipeline


def test_run_pipeline_writes_figures(tiny_cfg):
    result = run_pipeline(tiny_cfg)
    outputs = result["outputs"]

    # tiny_csv carries a "mammal" column, so all three figures are produced
    assert "component_planes" in outputs
    assert "umatrix" in outputs
    assert "cluster_map_by_mammal" in outputs

    for path in outputs.values():
        p = Path(path)
        assert p.exists(), f"missing figure: {p}"
        assert p.stat().st_size > 0


def test_cluster_diagnostics(tiny_cfg):
    # diagnostics read the codebook, so train first
    run_pipeline(tiny_cfg)
    result = cluster_diagnostics(tiny_cfg, k_min=2, k_max=6)

    assert result["k"] == [2, 3, 4, 5, 6]
    assert len(result["silhouette"]) == 5
    assert 2 <= result["suggested_k"] <= 6
    assert Path(result["figure"]).exists()
