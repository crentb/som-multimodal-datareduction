"""
HDF5 persistence for trained SOMs (codebook + source data + metadata).

The on-disk schema mirrors the one Cameron used in the JMBBM 2022 enamel
notebooks, so codebooks remain interchangeable between this package and the
original analysis:

    /sm_codebook_matrix    pandas DataFrame  (n_nodes x n_features) trained codebook
    /sm_data               pandas DataFrame  the source rows (id column dropped)
    /sm_codebook_mapsize   pandas Series     (rows, cols) of the SOM grid
    /sm_codebook_columns/property_names          PyTables array  feature names
    /sm_codebook_matfamilies/material_families   PyTables array  per-row specimen ids

The two leaf arrays are written through the raw PyTables handle (exactly as in the
original notebooks) because pandas does not round-trip those object/string columns
cleanly out of an HDF5 file.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import tables  # PyTables: backs pandas HDF5 + the raw reader/writer for the leaf arrays


def save_som_h5(path, sm, data_df, feature_columns, mapsize, id_column="Row"):
    """Persist a trained SOMPY map plus its source data to ``path`` (HDF5).

    Parameters
    ----------
    path : path-like         destination .h5 (parent dirs are created)
    sm : sompy SOM           a trained map (uses ``sm.codebook.matrix``)
    data_df : pandas.DataFrame   the full source table
    feature_columns : list[str]  the columns the SOM was trained on
    mapsize : tuple[int, int]    the SOM grid (rows, cols)
    id_column : str          per-row id column to store separately (default "Row")

    Returns ``Path`` to the written file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    has_id = id_column in data_df.columns
    body = data_df.drop(columns=[id_column]) if has_id else data_df
    ids = list(data_df[id_column]) if has_id else list(range(len(data_df)))

    with pd.HDFStore(str(path), mode="w") as store:
        store["sm_codebook_matrix"] = pd.DataFrame(
            sm.codebook.matrix, columns=list(feature_columns)
        )
        store["sm_data"] = body
        store["sm_codebook_mapsize"] = pd.Series(tuple(mapsize))

        # Raw PyTables leaf arrays for the string/object metadata.
        handle = store._handle
        cols_group = handle.create_group(handle.root, "sm_codebook_columns")
        handle.create_array(
            cols_group, "property_names", list(feature_columns), "Feature/property names"
        )
        fam_group = handle.create_group(handle.root, "sm_codebook_matfamilies")
        handle.create_array(fam_group, "material_families", ids, "Per-row specimen identifiers")

    return path


def load_som_h5(path):
    """Read back a codebook saved by :func:`save_som_h5`.

    Returns ``(codebook_df, mapsize, data_df, feature_columns, specimen_ids)``.
    """
    path = str(path)
    codebook = pd.read_hdf(path, "sm_codebook_matrix")
    mapsize = tuple(int(v) for v in pd.read_hdf(path, "sm_codebook_mapsize").values)
    data_df = pd.read_hdf(path, "sm_data")

    # PyTables stores Python strings as bytes; decode the feature names back to str.
    with tables.open_file(path, "r") as store:
        columns = [
            c.decode("utf-8") if isinstance(c, bytes) else str(c)
            for c in store.root.sm_codebook_columns.property_names.read()
        ]
        specimen_ids = list(store.root.sm_codebook_matfamilies.material_families.read())

    return codebook, mapsize, data_df, columns, specimen_ids
