"""
Run configuration for the multimodal SOM data-reduction pipeline.

A single immutable-ish ``RunConfig`` dataclass carries every knob the pipeline
needs (input data, feature set, SOM grid, clustering, output locations) so that
``train``, ``visualize`` and the end-to-end ``pipeline`` all agree on one source
of truth. The helpers at the bottom build a ``RunConfig`` from argparse so the
three command-line entry points share identical flags without duplication.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path

# The eight multimodal features the SOM is trained on in the JMBBM 2022 enamel
# study: two nanoindentation mechanics (modulus, hardness), three Raman markers
# (carb = carbonate, crys = crystallinity, fluo = fluorescence), depth from the
# surface, and two fracture metrics (kc = fracture toughness, b = a fitted
# crack-resistance parameter). Categorical/metadata columns are excluded.
DEFAULT_FEATURES = ["modulus", "hardness", "carb", "crys", "fluo", "depth", "kc", "b"]


@dataclass
class RunConfig:
    """All parameters for one train/visualize run."""

    # ---- input -------------------------------------------------------------
    data_csv: str = "data/general_main.csv"
    feature_columns: list[str] = field(default_factory=lambda: list(DEFAULT_FEATURES))
    id_column: str = "Row"  # per-row specimen id; carried through to the maps
    label_column: str = "mammal"  # categorical column used to colour the cluster map

    # ---- SOM training ------------------------------------------------------
    mapsize: tuple[int, int] = (25, 25)  # (rows, cols) of the SOM grid
    normalization: str = "var"  # SOMPY feature normalization ("var" = z-score)
    initialization: str = "pca"  # codebook seeding ("pca" or "random")
    rough_len: int = 0  # rough-training epochs; 0 -> SOMPY auto-computes
    finetune_len: int = 0  # fine-tuning epochs; 0 -> SOMPY auto-computes

    # ---- clustering / visualization ---------------------------------------
    n_clusters: int = 6  # k for k-means over the trained codebook
    seed: int = 555  # k-means RNG seed (parity with the 2022 study)
    heatmap_size: tuple[int, int] = (8, 20)  # component-plane figure size (in)
    umatrix_size: tuple[int, int] = (10, 10)  # U-matrix figure size (in)

    # ---- output ------------------------------------------------------------
    output_dir: str = "outputs"
    codebook_file: str = "som_codebook.h5"

    @property
    def codebook_path(self) -> Path:
        """Full path to the trained-codebook HDF5 file."""
        return Path(self.output_dir) / self.codebook_file


def add_common_cli_args(parser: argparse.ArgumentParser) -> None:
    """Register the flags shared by the train/visualize/pipeline CLIs."""
    d = RunConfig()  # defaults to advertise in --help
    parser.add_argument(
        "--data-csv", default=d.data_csv, help="input CSV of multimodal measurements"
    )
    parser.add_argument(
        "--features",
        nargs="+",
        default=None,
        metavar="COL",
        help="feature columns to train on (default: the 8 enamel features)",
    )
    parser.add_argument("--id-column", default=d.id_column, help="per-row specimen id column")
    parser.add_argument(
        "--label-column",
        default=d.label_column,
        help="categorical column to colour the cluster map",
    )
    parser.add_argument(
        "--mapsize",
        type=int,
        nargs=2,
        default=list(d.mapsize),
        metavar=("ROWS", "COLS"),
        help="SOM grid size",
    )
    parser.add_argument("--normalization", default=d.normalization, help="SOMPY normalization")
    parser.add_argument("--initialization", default=d.initialization, help="SOMPY codebook init")
    parser.add_argument(
        "--rough-len", type=int, default=d.rough_len, help="rough-training epochs (0=auto)"
    )
    parser.add_argument(
        "--finetune-len", type=int, default=d.finetune_len, help="fine-tuning epochs (0=auto)"
    )
    parser.add_argument(
        "--n-clusters", type=int, default=d.n_clusters, help="k for k-means over the codebook"
    )
    parser.add_argument("--seed", type=int, default=d.seed, help="k-means RNG seed")
    parser.add_argument(
        "--output-dir", default=d.output_dir, help="directory for the .h5 + figures"
    )
    parser.add_argument(
        "--codebook-file", default=d.codebook_file, help="trained-codebook HDF5 filename"
    )


def config_from_args(args: argparse.Namespace) -> RunConfig:
    """Build a ``RunConfig`` from parsed CLI args (see ``add_common_cli_args``)."""
    return RunConfig(
        data_csv=args.data_csv,
        feature_columns=list(args.features) if args.features else list(DEFAULT_FEATURES),
        id_column=args.id_column,
        label_column=args.label_column,
        mapsize=tuple(args.mapsize),
        normalization=args.normalization,
        initialization=args.initialization,
        rough_len=args.rough_len,
        finetune_len=args.finetune_len,
        n_clusters=args.n_clusters,
        seed=args.seed,
        output_dir=args.output_dir,
        codebook_file=args.codebook_file,
    )
