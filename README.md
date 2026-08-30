# SPICE

Scalable Phase-field Implementation of Crack Evolution (SPICE) for Modeling Surface Crevasse Growth and Interaction in Glaciers.

```
export PATH="$CONDA_PREFIX/bin:$PATH"
```

```bash
mpirun -np 4 python3 main.py --input examples/4.5.parallel/17-22.toml
```

The metrics printed after every solve are also written by MPI rank 0 to
`metrics.csv` in the configured output directory. The CSV contains `step`,
`ram_gb`, `hmin`, `ndof`, `elapsed_seconds`, and `ms_error`. Its output can be
customized or disabled in the input file:

```toml
[output]
write_csv = true
csv_filename = "metrics.csv"
```

