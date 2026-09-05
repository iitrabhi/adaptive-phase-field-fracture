# SPICE

Scalable Phase-field Implementation of Crack Evolution (SPICE) for Modeling Surface Crevasse Growth and Interaction in Glaciers.

```
export PATH="$CONDA_PREFIX/bin:$PATH"
```

```bash
mpirun -np 4 python3 main.py --input examples/4.5.parallel/17-22.toml
```

## Batch runs

`run.sh` at the project root lets you queue several studies in one command.
Each study runs sequentially — the next one starts only after the previous one
finishes.

**1. Open `run.sh` and set the flag to `1` for every study you want to run:**

```bash
RUN_4_1_04=1   # adaptive, hw=0.5H
RUN_4_1_05=1   # adaptive, hw=0.25H
RUN_4_3_01=1   # two-crevasse interaction, S=15 m
```

Leave everything else at `0`.

**2. Optionally set the number of MPI processes** (default `NP=4`):

```bash
NP=8
```

**3. Launch the batch:**

```bash
bash run.sh
```

To keep the output and come back to it later:

```bash
bash run.sh 2>&1 | tee run.log
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

