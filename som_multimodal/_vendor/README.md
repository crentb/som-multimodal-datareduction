# `som_multimodal/_vendor/`

Third-party code vendored verbatim (or near-verbatim) so the package is
self-contained and reproducible. **This code is not original to this project.**

## `sompy/` — SOMPY 1.1.1

A Python Self-Organizing-Map library by **Vahid Moosavi (@sevamoo)** and
contributors — https://github.com/sevamoo/SOMPY — licensed **Apache-2.0**
(see `sompy/LICENSE`).

Vendored verbatim except that three internal absolute imports
(`from sompy.visualization.plot_tools import plot_hex_map`) were rewritten to the
relative form `from .plot_tools import plot_hex_map`, so the library imports
correctly under the `som_multimodal._vendor.sompy` namespace.

It is vendored rather than installed from PyPI because the PyPI distribution named
`sompy` is an **unrelated** project; sevamoo's SOMPY is published only on GitHub.

See `../engine/ACKNOWLEDGMENTS.md` and the repository-root `NOTICE` for the full
attribution and citation guidance.
