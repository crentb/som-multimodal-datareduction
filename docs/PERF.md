# Performance

SOM training cost vs. map size on `data/general_main.csv`, measured with
`scripts/profile_som.py`. Training time grows with the node count
(rows x cols); the errors are listed for reference (lower is better).

- Machine: macOS-26.5.1-arm64-arm-64bit-Mach-O
- Python: 3.13.5

| mapsize | nodes | train time (s) | topographic err | quantization err |
|--------:|------:|---------------:|----------------:|-----------------:|
| 10x10 | 100 | 0.056 | 0.9058 | 0.9681 |
| 15x15 | 225 | 0.086 | 0.1522 | 0.7271 |
| 20x20 | 400 | 0.221 | 0.0072 | 0.5233 |
| 25x25 | 625 | 0.635 | 0.0145 | 0.3193 |
| 30x30 | 900 | 1.677 | 0.1304 | 0.1732 |

Times are the best of the configured repeats and are single-threaded
(`n_job=1`); expect run-to-run variation and machine dependence.

## Flame-graph profile — end-to-end pipeline

The full pipeline run (`train_som` → `visualize_som`) on the shipped
dataset (`data/general_main.csv`, 138 measurements × 8 enamel features),
attributed with cProfile (2026-07-15); the committed flame graph is
rendered from that same profile (classic bottom-up layout; the SVG
scales to fit the browser window with click-to-zoom intact).
Apple-Silicon macOS, Python 3.13.

| Phase | Cost | Reading |
|---|---|---|
| `train_som` | 0.77 s (39%) | Largest single function: vendored `sompy/neighborhood.py::calculate` (0.34 s over 318 per-epoch calls) — the Gaussian neighborhood update, i.e. the SOM algorithm itself, already-vectorized numpy |
| figure rendering | ~1.2 s (~60%) | Spread thinly across matplotlib/PIL internals (image draw, resample, PNG encode, text layout) — no dominant fixable hotspot |
| **Total** | **1.98 s** | 3.2 M function calls |

The engineering call: **profiled, and deliberately not optimized.** At
2 s end-to-end on real data, with the time split between the core
algorithm and diffuse rendering overhead, optimization would add risk
and complexity for no user-visible benefit — so the documented outcome
is a no-change decision. Equivalence fingerprint for any future work:
topographic_error 0.014492754 · quantization_error 0.319285544 ·
3 figures.

Tooling note: stock flameprof cannot render this call graph — its
inverted-flame pass divides by zero on zero-cumulative-time call groups
the vendored sompy graph produces. The committed graph therefore uses
flameprof's collapsed-stack export (with that division guarded) rendered
by flamegraph.pl; a py-spy sampling capture (root required on macOS,
unprivileged on Linux CI runners) independently reproduces the same
shape.

- [`profiling/flame_som_pipeline.svg`](profiling/flame_som_pipeline.svg)
  (open in a browser; box width is time on-stack, click to zoom)

The matching `flame_som_pipeline.collapsed.txt` imports directly into
[speedscope](https://www.speedscope.app/) for interactive exploration
(fully client-side; nothing is uploaded).
