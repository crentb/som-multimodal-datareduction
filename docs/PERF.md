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
