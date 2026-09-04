"""FEniCS spaces, projections, and the validated staggered solve step."""

from dataclasses import dataclass
from typing import Any

import math

from dolfin import *
import numpy as np

from .boundary import create_boundary_data
from .config import SimulationConfig
from .model import displacement_forms, get_energy, phase_field_forms


@dataclass
class FunctionSpaces:
    damage: Any
    history: Any
    displacement: Any



@dataclass
class SolveResult:
    displacement: Any
    damage: Any
    history: Any
    error: float


def load_mesh(config: SimulationConfig, communicator):
    mesh = Mesh()
    with XDMFFile(communicator, str(config.mesh_path)) as input_file:
        input_file.read(mesh)
    return mesh


def make_spaces(mesh, config: SimulationConfig) -> FunctionSpaces:
    finite_element = config.finite_element
    damage_space = FunctionSpace(
        mesh,
        finite_element.damage_family,
        finite_element.damage_degree,
    )
    history_space = FunctionSpace(
        mesh,
        finite_element.history_family,
        finite_element.history_degree,
    )
    displacement_space = VectorFunctionSpace(
        mesh,
        finite_element.displacement_family,
        finite_element.displacement_degree,
    )
    return FunctionSpaces(
        damage=damage_space,
        history=history_space,
        displacement=displacement_space,
    )


def mproject(function, function_space, config: SimulationConfig):
    solver_type = config.solver.projection_linear_solver
    preconditioner = config.solver.projection_preconditioner
    if preconditioner:
        return project(
            function,
            function_space,
            solver_type=solver_type,
            preconditioner_type=preconditioner,
        )
    return project(function, function_space, solver_type=solver_type)


def _configure_linear_solver(linear_solver, config: SimulationConfig) -> None:
    parameters = linear_solver.parameters
    parameters["linear_solver"] = config.solver.linear_solver
    if config.solver.preconditioner:
        parameters["preconditioner"] = config.solver.preconditioner


def solve_problem(
    mesh,
    config: SimulationConfig,
    damage_adaptive=None,
    history_adaptive=None,
) -> SolveResult:
    """Perform one displacement-history-damage solve in the validated order."""

    spaces = make_spaces(mesh, config)

    trial_displacement = TrialFunction(spaces.displacement)
    test_displacement = TestFunction(spaces.displacement)
    displacement_new = Function(spaces.displacement, name="disp")

    trial_damage = TrialFunction(spaces.damage)
    test_damage = TestFunction(spaces.damage)
    damage_new = Function(spaces.damage, name="damage")
    damage_old = Function(spaces.damage, name="damage")
    history = Function(spaces.history, name="cdf")

    if damage_adaptive is not None:
        damage_old.assign(mproject(damage_adaptive, spaces.damage, config))

    if history_adaptive is not None:
        history.assign(mproject(history_adaptive, spaces.history, config))

    boundary_data = create_boundary_data(mesh, spaces.displacement, config)

    displacement_bilinear, displacement_linear = displacement_forms(
        trial_displacement,
        test_displacement,
        damage_old,
        boundary_data.body_force,
        boundary_data.traction,
        boundary_data.boundary_measure,
        boundary_data.traction_marker,
        config,
    )
    damage_bilinear, damage_linear = phase_field_forms(
        trial_damage,
        test_damage,
        history,
        config,
    )

    displacement_problem = LinearVariationalProblem(
        displacement_bilinear,
        displacement_linear,
        displacement_new,
        boundary_data.displacement_bcs,
    )
    displacement_solver = LinearVariationalSolver(displacement_problem)
    _configure_linear_solver(displacement_solver, config)

    damage_problem = LinearVariationalProblem(damage_bilinear, damage_linear, damage_new)
    damage_solver = LinearVariationalSolver(damage_problem)
    _configure_linear_solver(damage_solver, config)

    displacement_solver.solve()
    projected_energy = mproject(get_energy(displacement_new, damage_new, spaces.history, config),spaces.history,config)
    # history.vector()[:] = np.maximum(projected_energy.vector()[:],history.vector()[:])
    history.vector()[:] = projected_energy.vector()[:]
    damage_solver.solve()
    damage_new.vector()[:] = np.clip(damage_new.vector()[:], 0.0, 1.0)

    damage_norm = assemble(damage_new ** 2 * dx)
    if damage_norm > config.solver.norm_zero_tolerance:
        damage_error = math.sqrt(assemble((damage_new - damage_old) ** 2 * dx) / damage_norm)
    else:
        damage_error = 0.0

    error = float(damage_error)
    return SolveResult(
        displacement=displacement_new,
        damage=damage_new,
        history=history,
        error=error,
    )

