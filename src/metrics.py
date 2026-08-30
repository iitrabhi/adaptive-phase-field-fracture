"""MPI-safe output for the global metrics printed during a run."""

import csv


class MetricsCsvWriter:
    """Write one global metrics stream without concurrent MPI file access."""

    fieldnames = (
        "step",
        "ram_gb",
        "hmin",
        "ndof",
        "elapsed_seconds",
        "ms_error",
    )

    def __init__(self, config, communicator):
        self._stream = None
        self._writer = None
        if not config.output.write_csv or communicator.Get_rank() != 0:
            return

        # A restarted run continues the existing metrics history. A fresh run
        # replaces it, matching the behavior of the primary simulation output.
        append = config.restart_checkpoint.enabled and config.csv_output_path.is_file()
        mode = "a" if append else "w"
        self._stream = config.csv_output_path.open(mode, newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._stream, fieldnames=self.fieldnames)
        if not append or config.csv_output_path.stat().st_size == 0:
            self._writer.writeheader()
            self._stream.flush()

    def write(self, **metrics) -> None:
        if self._writer is None:
            return
        self._writer.writerow(metrics)
        self._stream.flush()

    def close(self) -> None:
        if self._stream is not None:
            self._stream.close()
            self._stream = None
            self._writer = None
