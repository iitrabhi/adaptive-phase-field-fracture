"""Command-line entry point for the TOML-driven phase-field solver."""

import argparse

from dolfin import *

from src.adaptivity import mprint, run_adaptive
from src.config import load_config
from src.solver import load_mesh


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="input.toml",
        help="Path to the problem TOML file (default: input.toml).",
    )
    return parser.parse_args()


def _configure_logging(level_name: str) -> None:
    level = getattr(LogLevel, level_name.upper(), None)
    if level is None:
        raise ValueError("Unknown DOLFIN log level: {}".format(level_name))
    set_log_level(level)


def main() -> None:
    arguments = _parse_arguments()
    config = load_config(arguments.input)
    _configure_logging(config.logging.level)

    communicator = MPI.comm_world
    mesh = load_mesh(config, communicator)

    print("Running adaptive phase-field solver with configuration:")
    run_adaptive(mesh, config, communicator)


if __name__ == "__main__":
    main()
