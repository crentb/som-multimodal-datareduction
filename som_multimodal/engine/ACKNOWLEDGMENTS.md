# Acknowledgments - `som_multimodal.engine` and `som_multimodal._vendor`

The self-organizing-map machinery in this package is **built on, and contains
modified copies of, prior open-source work**. None of the SOM core or its
visualization layer is claimed as original; only Cameron Renteria's
*modifications* and the *overall multimodal data-reduction pipeline* around them
are. All upstreams are redistributed under their original Apache-2.0 terms.

## 1. SOMPY - the SOM core (vendored, in `som_multimodal/_vendor/sompy/`)

> **SOMPY: A Python Library for Self Organizing Map (SOM)**
> Vahid Moosavi (@sevamoo) and contributors.
> https://github.com/sevamoo/SOMPY - Apache License 2.0.

Vendored from SOMPY 1.1.1, **verbatim** except for three internal imports
(`from sompy.visualization.plot_tools import ...`) rewritten to package-relative
form so the library is importable under the `som_multimodal._vendor.sompy`
namespace. The original `LICENSE` is preserved at
`som_multimodal/_vendor/sompy/LICENSE`. SOMPY is vendored (rather than pulled from
PyPI) because the PyPI package named `sompy` is a *different, unrelated* project;
the implementation used here is only distributed via sevamoo's GitHub.

## 2. tfprop_sompy - the SOM visualization layer (modified, in `engine/`)

> **tfprop_sompy: Self-Organizing Map Data-Mining for Thermo-Fluid Properties**
> Gota Kikugawa and Yuta Nishimura, Tohoku University, Japan.

`engine/tfprop_vis.py` and `engine/strings.py` are **modified versions** of that
project's visualization helpers. Cameron Renteria's modifications ((c) 2026,
Apache-2.0) are summarized in each file's header and include: decoupling the code
from a global configuration module, repointing all imports at the vendored SOMPY,
fixing several modern-Matplotlib/NumPy incompatibilities so the code actually
runs today, and removing unused code paths. The plotting algorithms themselves
(component-plane heat maps, U-matrix, cluster-category overlays) are upstream.

## 3. Notebook & template lineage

The original Jupyter notebooks this pipeline was distilled from descend from
teaching templates by **Tim Letz** (UW materials-data-science SOM lab,
https://github.com/timletz/materials_datascience_uw_somlab) and from the
**MSESOM** consolidation in the **Huang group** at the University of Washington.
The thermo-fluid-to-enamel adaptation, the multimodal feature set, the HDF5
codebook schema, the de-widgetized command-line pipeline, and the
`general_main.csv` dataset are Cameron Renteria's contribution.

## How to cite

If you use this software, please cite the dataset/method paper:

> C. B. Renteria et al., "Contributions to enamel durability with aging: An
> application of data science tools," *Journal of the Mechanical Behavior of
> Biomedical Materials*, 2022. doi:10.1016/j.jmbbm.2022.105147

and acknowledge SOMPY (sevamoo) and tfprop_sompy (Kikugawa & Nishimura) above.
