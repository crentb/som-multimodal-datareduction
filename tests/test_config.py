"""RunConfig defaults and the shared argparse -> RunConfig path."""

import argparse

from som_multimodal.config import (
    DEFAULT_FEATURES,
    RunConfig,
    add_common_cli_args,
    config_from_args,
)


def test_defaults():
    cfg = RunConfig()
    assert cfg.feature_columns == DEFAULT_FEATURES
    assert cfg.feature_columns is not DEFAULT_FEATURES  # independent copy, not the module list
    assert cfg.codebook_path.name == "som_codebook.h5"
    assert cfg.codebook_path.parent.name == "outputs"


def test_config_from_args_overrides():
    parser = argparse.ArgumentParser()
    add_common_cli_args(parser)
    args = parser.parse_args(
        ["--mapsize", "7", "7", "--n-clusters", "4", "--label-column", "position"]
    )
    cfg = config_from_args(args)
    assert cfg.mapsize == (7, 7)
    assert cfg.n_clusters == 4
    assert cfg.label_column == "position"
    # --features omitted -> falls back to the default enamel feature set
    assert cfg.feature_columns == DEFAULT_FEATURES


def test_config_from_args_custom_features():
    parser = argparse.ArgumentParser()
    add_common_cli_args(parser)
    args = parser.parse_args(["--features", "modulus", "hardness"])
    cfg = config_from_args(args)
    assert cfg.feature_columns == ["modulus", "hardness"]
