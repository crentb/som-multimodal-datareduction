"""The vendored/modified engine imports and clusters a trained SOM codebook."""

import numpy as np

from som_multimodal._vendor.sompy.sompy import SOMFactory
from som_multimodal.engine import (
    UMatrixTFP,
    ViewTFP,
    clusteringmap_category,
    kmeans_clust,
)


def test_engine_exports():
    # smoke: the public engine symbols are importable and callable/constructable
    assert callable(kmeans_clust)
    assert callable(clusteringmap_category)
    assert ViewTFP is not None
    assert UMatrixTFP is not None


def test_kmeans_clust_labels_codebook():
    rng = np.random.default_rng(2)
    sm = SOMFactory.build(
        rng.normal(size=(20, 5)), mapsize=(4, 4), normalization="var", initialization="pca"
    )
    sm.train(n_job=1, verbose=None, train_rough_len=2, train_finetune_len=2)

    labels = kmeans_clust(sm, n_clusters=3, seed=0)
    assert len(labels) == 16  # one label per SOM node (4x4)
    assert set(np.unique(labels)) <= {0, 1, 2}
