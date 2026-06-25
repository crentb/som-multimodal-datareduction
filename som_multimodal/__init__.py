"""
som-multimodal-datareduction
============================

A reproducible, command-line pipeline that applies Self-Organizing Maps (SOMs)
plus k-means to *multimodal* materials data -- reducing high-dimensional,
mixed-source measurements (here: nanomechanics + Raman + fracture metrics on tooth
enamel) to interpretable cluster maps and component planes.

The SOM core (SOMPY) and its visualization layer (tfprop_sompy) are vendored and
*modified* from prior open-source work; see ``som_multimodal/engine/ACKNOWLEDGMENTS.md``
and ``NOTICE``. The pipeline, HDF5 schema, feature set, and dataset are original to
this project.

Public API:
    RunConfig        -- one config object for the whole pipeline
    DEFAULT_FEATURES -- the eight enamel feature columns

Command-line entry points:
    python -m som_multimodal.train       (or: som-train)
    python -m som_multimodal.visualize   (or: som-visualize)
    python -m som_multimodal.analysis    (or: som-analysis)
    python -m som_multimodal.pipeline    (or: som-pipeline)
"""

from som_multimodal.config import DEFAULT_FEATURES, RunConfig

__version__ = "0.1.0"

__all__ = ["RunConfig", "DEFAULT_FEATURES", "__version__"]
