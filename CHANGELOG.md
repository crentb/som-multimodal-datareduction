# Changelog

All notable changes to this project are documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-07-16

### Added
- **Continuous delivery** (`.github/workflows/release.yml`): pushing a `v*` tag re-runs the
  full CI gate on the tagged commit, then publishes the sdist + wheel to PyPI via Trusted
  Publishing (OIDC — no stored API token) and a signed container image to GHCR carrying a
  SLSA build-provenance attestation. `ci.yml` is now `workflow_call`-able so the release
  re-uses the exact same gates instead of a copy that could drift.
- **DevSecOps stages in CI**, all gating: full-history secret detection (gitleaks), SAST
  (bandit, medium+, scoped to the authored package so the vendored SOMPY tree is tracked
  upstream rather than gated here), and dependency-CVE audit (pip-audit); plus container
  vulnerability scanning (trivy, CRITICAL/HIGH) and an SPDX SBOM (syft) signed keylessly
  with cosign via GitHub OIDC.

### Security
- Patched the 3 fixable HIGH-severity CVEs that trivy found in the container image.

### Fixed
- Corrected the trivy-action pin (`0.24.0`, which does not exist → `v0.36.0`), and scoped
  the trivy gate to *fixable* CRITICAL/HIGH so an unpatchable upstream CVE cannot
  permanently block releases.

## [0.1.0] - 2026-07-03

### Added
- Initial version of a multimodal SOM data-reduction pipeline, distilled from the
  `SOM_Analysis_CR` / `SOM_Visualization_CR` Jupyter notebooks into a headless,
  single-command package (no ipywidgets).
- `som_multimodal.train` - build + train a SOMPY map over chosen feature columns and
  save the trained codebook (plus source data + metadata) to an HDF5 file.
- `som_multimodal.visualize` - render component-plane heat maps, a cluster-category
  map (nodes by k-means cluster, points by a metadata column), and a U-matrix.
- `som_multimodal.analysis` - elbow + silhouette diagnostics to choose the cluster count.
- `som_multimodal.pipeline` - end-to-end train->visualize driver.
- `RunConfig` single source of truth for all parameters; shared argparse CLIs
  (`som-train`, `som-visualize`, `som-analysis`, `som-pipeline`).
- Vendored SOMPY core (`som_multimodal/_vendor/sompy`, Apache-2.0, verbatim except 3
  relative-import fixes) so the package is self-contained on modern Python.
- Modified `tfprop_sompy` visualization engine (`som_multimodal/engine`): decoupled
  from a global config, repointed at the vendored SOMPY, and fixed for modern
  Matplotlib/NumPy. Upstream credit preserved (see `engine/ACKNOWLEDGMENTS.md`, `NOTICE`).
- The real multimodal enamel dataset (`data/general_main.csv`, 138 measurements) with a
  data dictionary, cited to JMBBM 2022 (doi:10.1016/j.jmbbm.2022.105147).
- pip-installable PEP 621 package (Apache-2.0); pytest suite (synthetic, CPU, fast);
  GitHub Actions CI (ruff + black + mypy + pytest on Python 3.10-3.12) plus a Docker
  image build/smoke-test; pre-commit hooks. The vendored/modified SOM code is excluded
  from the style gates.
