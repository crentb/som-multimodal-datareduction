"""HDF5 codebook save/load round-trips the schema the notebooks used."""

import numpy as np
import pandas as pd

from som_multimodal._vendor.sompy.sompy import SOMFactory
from som_multimodal.config import DEFAULT_FEATURES
from som_multimodal.io import load_som_h5, save_som_h5


def _tiny_trained_som(n=20, mapsize=(4, 4)):
    rng = np.random.default_rng(1)
    df = pd.DataFrame({"Row": list(range(n))})
    for col in DEFAULT_FEATURES:
        df[col] = rng.normal(size=n)
    df["mammal"] = ["h"] * n
    sm = SOMFactory.build(
        df[DEFAULT_FEATURES].to_numpy(dtype=float),
        mapsize=mapsize,
        normalization="var",
        initialization="pca",
        component_names=DEFAULT_FEATURES,
    )
    sm.train(n_job=1, verbose=None, train_rough_len=2, train_finetune_len=2)
    return sm, df


def test_h5_roundtrip(tmp_path):
    sm, df = _tiny_trained_som()
    path = tmp_path / "cb.h5"

    returned = save_som_h5(path, sm, df, DEFAULT_FEATURES, (4, 4), id_column="Row")
    assert returned == path
    assert path.exists()

    codebook, mapsize, data_df, columns, specimen_ids = load_som_h5(path)
    assert codebook.shape == (16, 8)  # 4x4 nodes, 8 features
    assert mapsize == (4, 4)
    assert columns == DEFAULT_FEATURES
    assert "Row" not in data_df.columns  # id column is stored separately, not in the body
    assert list(specimen_ids) == list(range(20))
