"""
Benchmark SOM training cost vs. map size on the bundled enamel dataset.

Self-organizing-map training time is dominated by the number of map nodes
(grid rows x cols), so this script sweeps a few grid sizes, times ``train_som``
for each, and reports wall-clock time alongside the topographic and quantization
errors. Use it to pick a map size that balances resolution against runtime, and
to regenerate ``docs/PERF.md``.

Usage:
    python scripts/profile_som.py                      # print a table to stdout
    python scripts/profile_som.py --out docs/PERF.md   # also write the Markdown report
    python scripts/profile_som.py --repeats 3          # best-of-3 timing per size

Note: on macOS, prefix with ``KMP_DUPLICATE_LIB_OK=TRUE`` if importing the
scientific stack segfaults on duplicate OpenMP runtimes.
"""

from __future__ import annotations

import argparse
import platform
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from som_multimodal.config import RunConfig
from som_multimodal.train import train_som

# Square grids spanning small/fast to large/high-resolution maps.
DEFAULT_SIZES = [(10, 10), (15, 15), (20, 20), (25, 25), (30, 30)]


def profile(data_csv: str, sizes: list[tuple[int, int]], repeats: int = 1) -> list[dict]:
    """Time ``train_som`` for each grid size; return one result row per size."""
    rows = []
    for rows_cols in sizes:
        r, c = rows_cols
        metrics: dict = {}
        best = None
        # Train into a throwaway dir so the benchmark never litters the repo.
        with TemporaryDirectory() as tmp:
            for _ in range(repeats):
                cfg = RunConfig(data_csv=data_csv, mapsize=(r, c), output_dir=tmp)
                start = time.perf_counter()
                _sm, metrics = train_som(cfg)
                elapsed = time.perf_counter() - start
                best = elapsed if best is None else min(best, elapsed)
        rows.append(
            {
                "mapsize": f"{r}x{c}",
                "nodes": r * c,
                "seconds": round(best, 3),
                "topographic_error": round(metrics["topographic_error"], 4),
                "quantization_error": round(metrics["quantization_error"], 4),
            }
        )
    return rows


def to_markdown(rows: list[dict], data_csv: str) -> str:
    """Render the benchmark rows as a self-contained Markdown report."""
    lines = [
        "# Performance",
        "",
        f"SOM training cost vs. map size on `{data_csv}`, measured with",
        "`scripts/profile_som.py`. Training time grows with the node count",
        "(rows x cols); the errors are listed for reference (lower is better).",
        "",
        f"- Machine: {platform.platform()}",
        f"- Python: {platform.python_version()}",
        "",
        "| mapsize | nodes | train time (s) | topographic err | quantization err |",
        "|--------:|------:|---------------:|----------------:|-----------------:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['mapsize']} | {row['nodes']} | {row['seconds']} | "
            f"{row['topographic_error']} | {row['quantization_error']} |"
        )
    lines += [
        "",
        "Times are the best of the configured repeats and are single-threaded",
        "(`n_job=1`); expect run-to-run variation and machine dependence.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Benchmark SOM training vs. map size.")
    parser.add_argument("--data-csv", default="data/general_main.csv", help="input dataset")
    parser.add_argument("--repeats", type=int, default=1, help="timed repeats per size (best kept)")
    parser.add_argument(
        "--out", default=None, help="optional Markdown report path (e.g. docs/PERF.md)"
    )
    args = parser.parse_args(argv)

    rows = profile(args.data_csv, DEFAULT_SIZES, repeats=args.repeats)

    print(f"{'mapsize':>8} {'nodes':>6} {'time(s)':>8} {'topo_err':>9} {'quant_err':>10}")
    for row in rows:
        print(
            f"{row['mapsize']:>8} {row['nodes']:>6} {row['seconds']:>8} "
            f"{row['topographic_error']:>9} {row['quantization_error']:>10}"
        )

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(to_markdown(rows, args.data_csv))
        print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
