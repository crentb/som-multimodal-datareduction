# som-multimodal-datareduction

> **Dataset & method paper — please cite:**
> C. Renteria, W. Yan, Y. L. Huang, D. D. Arola, *"Contributions to enamel durability
> with aging: An application of data science tools,"* **Journal of the Mechanical
> Behavior of Biomedical Materials** 129, 105147 (2022).
> doi:[10.1016/j.jmbbm.2022.105147](https://doi.org/10.1016/j.jmbbm.2022.105147)

A reproducible, command-line pipeline that applies **Self-Organizing Maps (SOMs)** plus
**k-means** to *multimodal* materials data — reducing high-dimensional, mixed-source
measurements to interpretable maps. It is the de-widgetized, packaged version of the
analysis behind the paper above, in which nanomechanical, Raman, and fracture
measurements of tooth enamel are fused to map structure–property relationships with
aging across species.

The shipped dataset (`data/general_main.csv`, 138 measurements) carries eight features —
modulus, hardness, carbonate, crystallinity, fluorescence, depth, fracture toughness
(`kc`), and a crack-resistance parameter (`b`) — plus tooth/mammal/position metadata.

## What it produces

| Figure | Description |
|--------|-------------|
| `component_planes.png` | One heat map per feature over the trained SOM grid, k-means cluster borders overlaid — shows how each property varies and which co-vary. |
| `cluster_map_by_<label>.png` | SOM nodes colored by k-means cluster, data points colored by a metadata column (e.g. `mammal`) — shows how groups distribute across the map. |
| `umatrix.png` | Unified distance matrix (inter-node distances) with projected samples — reveals cluster boundaries. |
| `cluster_diagnostics.png` | Elbow + silhouette vs. *k* to choose the cluster count. |

## Install

```bash
git clone https://github.com/crentb/som-multimodal-datareduction.git
cd som-multimodal-datareduction
pip install -e ".[dev]"      # core + test/lint tools; or drop [dev] for runtime only
```

No GPU or deep-learning stack is required — only the standard scientific-Python
libraries. The SOM core (SOMPY) is **vendored**, so nothing extra is fetched at install.

## Quickstart

End-to-end (train → figures) on the bundled data:

```bash
som-pipeline --data-csv data/general_main.csv --n-clusters 6 --output-dir outputs
```

Or step by step:

```bash
som-train     --data-csv data/general_main.csv --mapsize 25 25 --output-dir outputs
som-analysis  --output-dir outputs --k-min 2 --k-max 12      # pick k (elbow/silhouette)
som-visualize --output-dir outputs --n-clusters 6 --label-column mammal
```

Every entry point shares the same flags (`--features`, `--mapsize`, `--normalization`,
`--n-clusters`, `--label-column`, …); run any with `-h` for the full list. Use
`--features` to point the same pipeline at a different column set or dataset.

## How it works

```
CSV ──► train ──► som_codebook.h5 ──► visualize ──► PNG figures
        (SOMPY build+train,           (rebuild SOM, k-means
         topographic/quantization      over codebook, render)
         error, save codebook)
```

- **`config.RunConfig`** — one dataclass holding every parameter; shared by all CLIs.
- **`train.py`** — builds a SOMPY map (`var` normalization, PCA init), trains it,
  reports topographic + quantization error, and writes the codebook + data to HDF5.
- **`io.py`** — the HDF5 schema (codebook / data / mapsize / feature names / specimen
  ids), interchangeable with the original notebooks.
- **`visualize.py`** — reloads the codebook, clusters it with k-means, and renders the
  figures via the engine.
- **`analysis.py`** — elbow + silhouette diagnostics for choosing *k*.

## Repository layout

```
som_multimodal/
  config.py  train.py  visualize.py  analysis.py  pipeline.py  io.py
  engine/      MODIFIED tfprop_sompy visualization layer (credited)
  _vendor/sompy/   vendored SOMPY core (Apache-2.0, verbatim)
data/          general_main.csv + data dictionary
tests/         fast, synthetic, CPU tests
```

## Attribution

This project **builds on, and contains modified copies of, prior open-source work**;
only the overall pipeline, the HDF5 schema, the CLI, the enamel feature set, and the
dataset are original here.

- **SOMPY** — Vahid Moosavi (@sevamoo) et al., Apache-2.0 — the SOM core, vendored.
- **tfprop_sompy** — Gota Kikugawa & Yuta Nishimura (Tohoku University) — the
  visualization layer, used here in **modified** form.
- Notebook/template lineage: Tim Letz (UW SOM lab) and the Huang group (UW) MSESOM.

Full details and per-file modification notes: [`NOTICE`](NOTICE) and
[`som_multimodal/engine/ACKNOWLEDGMENTS.md`](som_multimodal/engine/ACKNOWLEDGMENTS.md).

## Citing

Please cite the **JMBBM 2022 paper** above (the dataset and method) and, optionally, this
software via [`CITATION.cff`](CITATION.cff).

## License

[Apache-2.0](LICENSE). Vendored/modified upstream code is redistributed under its
original Apache-2.0 terms with attribution preserved.
