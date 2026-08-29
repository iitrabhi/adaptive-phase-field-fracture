"""Adaptive refinement, field transfer, output, and run orchestration."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from dolfin import *
from mpi4py import MPI as pyMPI
import gc
import os
import time

import numpy as np
import psutil

from .config import SimulationConfig
from .solver import FunctionSpaces, SolveResult, make_spaces, mproject, solve_problem


@dataclass
class RunResult:
    mesh: Any
    damage: Any
    history: Any
    displacement: Optional[Any]
    outer_iterations: int
    final_error: float


@dataclass
class CheckpointState:
    mesh: Any
    displacement: Any
    damage: Any
    history: Any
    time_index: int
    outer_iteration: int
    solve_error: float


def mprint(communicator, *values) -> None:
    if communicator.Get_rank() == 0:
        output = ""
        for value in values:
            output += str(value)
        print(output, flush=True)


def transfer_to_space(source_function, target_space):
    source_space = source_function.ufl_function_space()
    transfer_matrix = PETScDMCollection.create_transfer_matrix(
        source_space, target_space
    )
    target_function = Function(target_space)
    target_function.vector()[:] = transfer_matrix * source_function.vector()
    return target_function


def get_markers(
    damage,
    mesh,
    config: SimulationConfig,
    communicator,
):
    marker = MeshFunction("bool", mesh, mesh.topology().dim())
    marker.set_all(False)

    history_space = FunctionSpace(
        mesh,
        config.finite_element.history_family,
        config.finite_element.history_degree,
    )
    projected_damage = mproject(damage, history_space, config)
    marker.array()[projected_damage.vector()[:] > config.adaptivity.damage_threshold] = True

    cell_size = Circumradius(mesh)/2.0
    cell_size_values = mproject(cell_size, history_space, config).vector()[:]
    marker.array()[cell_size_values < config.adaptivity.target_hmin] = False

    local_converged = np.all(np.invert(marker.array()))
    adaptivity_converged = communicator.allreduce(local_converged, op=pyMPI.LAND)
    return marker, bool(adaptivity_converged)


def _make_state(spaces: FunctionSpaces):
    displacement = Function(spaces.displacement, name="displacement")
    damage = Function(spaces.damage, name="damage")
    history = Function(spaces.history, name="energy")
    return displacement, damage, history


def _prepare_output(config: SimulationConfig, communicator):
    if communicator.Get_rank() == 0:
        config.output_directory.mkdir(parents=True, exist_ok=True)
    MPI.barrier(communicator)

    output_file = XDMFFile(communicator, str(config.output_path))
    output_file.parameters["functions_share_mesh"] = (
        config.output.functions_share_mesh
    )
    output_file.parameters["rewrite_function_mesh"] = (
        config.output.rewrite_function_mesh
    )
    output_file.parameters["flush_output"] = config.output.flush_output
    return output_file


def write_checkpoint(
    mesh,
    displacement,
    damage,
    history,
    time_index: int,
    outer_iteration: int,
    solve_error: float,
    config: SimulationConfig,
    communicator,
) -> None:
    """Atomically replace the rolling checkpoint with the current state."""
    checkpoint_path = config.write_checkpoint_path
    temporary_path = checkpoint_path.with_name(checkpoint_path.name + ".tmp")

    if communicator.Get_rank() == 0:
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        if temporary_path.exists():
            temporary_path.unlink()
    MPI.barrier(communicator)

    with HDF5File(communicator, str(temporary_path), "w") as checkpoint_file:
        checkpoint_file.write(mesh, "/mesh")
        checkpoint_file.write(displacement, "/displacement")
        checkpoint_file.write(damage, "/damage")
        checkpoint_file.write(history, "/history")
        attributes = checkpoint_file.attributes("/")
        attributes["time_index"] = int(time_index)
        attributes["outer_iteration"] = int(outer_iteration)
        attributes["solve_error"] = float(solve_error)

    MPI.barrier(communicator)
    if communicator.Get_rank() == 0:
        os.replace(str(temporary_path), str(checkpoint_path))
    MPI.barrier(communicator)


def load_checkpoint(config: SimulationConfig, communicator) -> CheckpointState:
    """Load the adaptive mesh, fields, and iteration metadata from a checkpoint."""
    checkpoint_path = config.restart_checkpoint_path
    if not checkpoint_path.is_file():
        raise FileNotFoundError("Checkpoint file not found: {}".format(checkpoint_path))

    mesh = Mesh()
    with HDF5File(communicator, str(checkpoint_path), "r") as checkpoint_file:
        checkpoint_file.read(mesh, "/mesh", False)
        spaces = make_spaces(mesh, config)
        displacement, damage, history = _make_state(spaces)
        checkpoint_file.read(displacement, "/displacement")
        checkpoint_file.read(damage, "/damage")
        checkpoint_file.read(history, "/history")
        attributes = checkpoint_file.attributes("/")
        time_index = int(attributes["time_index"])
        outer_iteration = int(attributes["outer_iteration"])
        solve_error = float(attributes["solve_error"])

    return CheckpointState(
        mesh=mesh,
        displacement=displacement,
        damage=damage,
        history=history,
        time_index=time_index,
        outer_iteration=outer_iteration,
        solve_error=solve_error,
    )


def run_adaptive(mesh, config: SimulationConfig, communicator) -> RunResult:
    process = psutil.Process(os.getpid())
    start_time = time.time()

    if config.restart_checkpoint.enabled:
        checkpoint_state = load_checkpoint(config, communicator)
        mesh = checkpoint_state.mesh
        spaces = make_spaces(mesh, config)
        displacement_state = checkpoint_state.displacement
        damage_state = checkpoint_state.damage
        history_state = checkpoint_state.history
        time_index = checkpoint_state.time_index
        outer_iteration = checkpoint_state.outer_iteration
        solve_error = checkpoint_state.solve_error
        final_displacement = displacement_state
        mprint(
            communicator,
            "Restarted from checkpoint at step {}: {}".format(
                time_index, config.restart_checkpoint_path
            ),
        )
    else:
        spaces = make_spaces(mesh, config)
        displacement_state, damage_state, history_state = _make_state(spaces)
        time_index = 0
        outer_iteration = 0
        solve_error = 1.0
        final_displacement = None

    output_file = _prepare_output(config, communicator)
    while solve_error > config.solver.outer_tolerance:
        if config.adaptivity.enabled:
            adaptivity_converged = False
            refinement_iteration = 0
            last_result = None
            while not adaptivity_converged:
                last_result = solve_problem(mesh, config, damage_state, history_state)
                solve_error = last_result.error

                marker, adaptivity_converged = get_markers(last_result.damage, mesh, config, communicator)

                mesh_new = refine(mesh, marker)
                spaces_new = make_spaces(mesh_new, config)
                displacement_new, damage_new, history_new = _make_state(spaces_new)
                damage_new.assign(transfer_to_space(damage_state, spaces_new.damage))
                history_new.assign(transfer_to_space(history_state, spaces_new.history))

                mesh = mesh_new
                spaces = spaces_new
                displacement_state = displacement_new
                damage_state = damage_new
                history_state = history_new
                refinement_iteration += 1

            damage_state.assign(transfer_to_space(last_result.damage, spaces.damage))
            history_state.assign(transfer_to_space(last_result.history, spaces.history))

            if config.output.write_displacement:
                displacement_state.assign(transfer_to_space(last_result.displacement, spaces.displacement))
                final_displacement = displacement_state
        else:
            last_result = solve_problem( mesh, config, damage_state, history_state)
            solve_error = last_result.error
            damage_state.assign(transfer_to_space(last_result.damage, spaces.damage))
            history_state.assign(transfer_to_space(last_result.history, spaces.history))
            if config.output.write_displacement:
                displacement_state.assign(transfer_to_space(last_result.displacement, spaces.displacement))
                final_displacement = displacement_state

        damage_state.rename("damage", "damage")
        displacement_state.rename("displacement", "displacement")

        if time_index % config.output.write_every == 0:
            if config.output.write_damage:
                output_file.write(damage_state, time_index)
            if config.output.write_displacement:
                output_file.write(displacement_state, time_index)

        time_index += 1
        outer_iteration += 1

        if config.write_checkpoint.enabled:
            write_checkpoint(
                mesh,
                displacement_state,
                damage_state,
                history_state,
                time_index,
                outer_iteration,
                solve_error,
                config,
                communicator,
            )

        memory_gb = process.memory_info().rss / (1024 ** 3)
        total_memory_gb = MPI.sum(communicator, memory_gb)

        mprint(
            communicator,
            "step: {0:3}, ram: {1:6.2f} GB, hmin: {2:5.2f}, "
            "ndof: {5:6}, time: {3:6.0f}, ms_err: {4:6.2e}".format(
                time_index,
                total_memory_gb,
                MPI.min(communicator, mesh.hmin()),
                time.time() - start_time,
                solve_error,
                spaces.displacement.dim() + spaces.damage.dim(),
            ),
        )
    output_file.close()
    return RunResult(
        mesh=mesh,
        damage=damage_state,
        history=history_state,
        displacement=final_displacement,
        outer_iterations=outer_iteration,
        final_error=solve_error,
    )
