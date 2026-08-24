"""Boundary identification, Dirichlet conditions, and external loads."""

from dataclasses import dataclass
from typing import Any, Dict, List

from dolfin import *

from .config import SimulationConfig


@dataclass
class BoundaryData:
    subdomains: Dict[str, Any]
    facet_markers: Any
    boundary_measure: Any
    displacement_bcs: List[Any]
    body_force: Any
    traction: Any
    traction_marker: int


def create_subdomains(config: SimulationConfig) -> Dict[str, Any]:
    geometry = config.geometry
    return {
        "left": CompiledSubDomain("near(x[0], 0)"),
        "right": CompiledSubDomain("near(x[0], Lx)", Lx=geometry.Lx),
        "front": CompiledSubDomain("near(x[1], 0)"),
        "back": CompiledSubDomain("near(x[1], Ly)", Ly=geometry.Ly),
        "bottom": CompiledSubDomain("near(x[2], 0)"),
        "top": CompiledSubDomain("near(x[2], Lz)", Lz=geometry.Lz),
    }


def create_dirichlet_bcs(
    displacement_space,
    subdomains: Dict[str, Any],
    config: SimulationConfig,
) -> List[Any]:
    boundary_conditions: List[Any] = []

    for condition in config.boundary_conditions:
        boundary = subdomains[condition.boundary]
        if condition.component is None:
            target_space = displacement_space
        else:
            target_space = displacement_space.sub(condition.component)
        boundary_conditions.append(
            DirichletBC(target_space, Constant(condition.value), boundary)
        )

    return boundary_conditions


def create_facet_markers(
    mesh,
    subdomains: Dict[str, Any],
    config: SimulationConfig,
):
    facet_markers = MeshFunction(
        "size_t", mesh, mesh.topology().dim() - 1
    )
    facet_markers.set_all(0)

    if config.hydrostatic.enabled:
        subdomains[config.hydrostatic.boundary].mark(
            facet_markers, config.hydrostatic.marker
        )

    boundary_measure = Measure("ds", subdomain_data=facet_markers)
    return facet_markers, boundary_measure


def create_body_force(config: SimulationConfig):
    if not config.gravity.enabled:
        return Constant((0.0, 0.0, 0.0))

    scale = config.material.ice_density * config.gravity.acceleration
    values = tuple(scale * component for component in config.gravity.direction)
    return Constant(values)


def create_hydrostatic_traction(config: SimulationConfig):
    if not config.hydrostatic.enabled:
        return Constant((0.0, 0.0, 0.0))

    components = ["0.0", "0.0", "0.0"]
    components[config.hydrostatic.component] = (
        "(h - x[2] >= 0 ? sign * rho * grav * (h - x[2]) : 0.0)"
    )

    return Expression(
        tuple(components),
        h=config.water_height,
        sign=config.hydrostatic.sign,
        rho=config.hydrostatic_density,
        grav=config.gravity.acceleration,
        degree=config.hydrostatic.degree,
    )


def create_boundary_data(mesh, displacement_space, config: SimulationConfig) -> BoundaryData:
    subdomains = create_subdomains(config)
    facet_markers, boundary_measure = create_facet_markers(
        mesh, subdomains, config
    )

    return BoundaryData(
        subdomains=subdomains,
        facet_markers=facet_markers,
        boundary_measure=boundary_measure,
        displacement_bcs=create_dirichlet_bcs(
            displacement_space, subdomains, config
        ),
        body_force=create_body_force(config),
        traction=create_hydrostatic_traction(config),
        traction_marker=config.hydrostatic.marker,
    )
