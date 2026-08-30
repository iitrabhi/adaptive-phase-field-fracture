"""Read, normalize, and validate the problem TOML file."""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class ProblemMetadata:
    name: str
    model: str
  
    precrack_depth_ratio: float


@dataclass(frozen=True)
class MeshConfig:
    path: str


@dataclass(frozen=True)
class GeometryConfig:
    Lx: float
    Ly: float
    Lz: float


@dataclass(frozen=True)
class FiniteElementConfig:
    displacement_family: str
    displacement_degree: int
    damage_family: str
    damage_degree: int
    history_family: str
    history_degree: int


@dataclass(frozen=True)
class MaterialConfig:
    youngs_modulus: float
    poissons_ratio: float
    ice_density: float
    freshwater_density: float
    seawater_density: float

    @property
    def shear_modulus(self) -> float:
        return self.youngs_modulus / 2.0 / (1.0 + self.poissons_ratio)

    @property
    def bulk_modulus(self) -> float:
        return self.youngs_modulus / 3.0 / (1.0 - 2.0 * self.poissons_ratio)

    @property
    def lame_lambda(self) -> float:
        return self.bulk_modulus - (2.0 / 3.0) * self.shear_modulus


@dataclass(frozen=True)
class FractureConfig:
    length_scale: float
    critical_stress: float
    energy_threshold: float
    zeta: float
    residual_stiffness: float


@dataclass(frozen=True)
class GravityConfig:
    enabled: bool
    acceleration: float
    direction: Tuple[float, float, float]


@dataclass(frozen=True)
class HydrostaticConfig:
    enabled: bool
    boundary: str
    marker: int
    density_source: str
    water_height_ratio: float
    component: int
    sign: float
    degree: int


@dataclass(frozen=True)
class BoundaryConditionConfig:
    name: str
    boundary: str
    type: str
    component: Optional[int]
    value: Any


@dataclass(frozen=True)
class AdaptivityConfig:
    enabled: bool
    target_hmin: float
    damage_threshold: float


@dataclass(frozen=True)
class SolverConfig:
    linear_solver: str
    preconditioner: str
    projection_linear_solver: str
    projection_preconditioner: str
    outer_tolerance: float
    norm_zero_tolerance: float


@dataclass(frozen=True)
class OutputConfig:
    directory: str
    filename: str
    write_csv: bool
    csv_filename: str
    write_every: int
    write_damage: bool
    write_displacement: bool
    functions_share_mesh: bool
    rewrite_function_mesh: bool
    flush_output: bool


@dataclass(frozen=True)
class CheckpointConfig:
    enabled: bool
    filename: str


@dataclass(frozen=True)
class LoggingConfig:
    level: str
    print_initial_hmin: bool
    garbage_collect_every: int


@dataclass(frozen=True)
class SimulationConfig:
    source_path: Path
    root_directory: Path
    problem: ProblemMetadata
    mesh: MeshConfig
    geometry: GeometryConfig
    finite_element: FiniteElementConfig
    material: MaterialConfig
    fracture: FractureConfig
    gravity: GravityConfig
    hydrostatic: HydrostaticConfig
    boundary_conditions: Tuple[BoundaryConditionConfig, ...]
    adaptivity: AdaptivityConfig
    solver: SolverConfig
    output: OutputConfig
    write_checkpoint: CheckpointConfig
    restart_checkpoint: CheckpointConfig
    logging: LoggingConfig

    @property
    def mesh_path(self) -> Path:
        return self.resolve_path(self.mesh.path)

    @property
    def output_directory(self) -> Path:
        return self.resolve_path(self.output.directory)

    @property
    def output_path(self) -> Path:
        return self.output_directory / self.output.filename

    @property
    def csv_output_path(self) -> Path:
        return self.output_directory / self.output.csv_filename

    @property
    def write_checkpoint_path(self) -> Path:
        return self.resolve_path(self.write_checkpoint.filename)

    @property
    def restart_checkpoint_path(self) -> Path:
        return self.resolve_path(self.restart_checkpoint.filename)

    @property
    def water_height(self) -> float:
        return self.hydrostatic.water_height_ratio * self.geometry.Lz

    @property
    def hydrostatic_density(self) -> float:
        densities = {
            "ice": self.material.ice_density,
            "freshwater": self.material.freshwater_density,
            "seawater": self.material.seawater_density,
        }
        return densities[self.hydrostatic.density_source]

    def resolve_path(self, value: str) -> Path:
        candidate = Path(value).expanduser()
        if candidate.is_absolute():
            return candidate
        return (self.root_directory / candidate).resolve()


def _load_toml(path: Path) -> Dict[str, Any]:
    try:
        import tomllib  # type: ignore
    except ImportError:
        try:
            import toml  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "A TOML reader is required. Install it with 'pip install toml' "
                "when using Python 3.7 through 3.10."
            ) from exc
        return dict(toml.load(str(path)))

    with path.open("rb") as stream:
        return dict(tomllib.load(stream))


def _section(data: Dict[str, Any], name: str) -> Dict[str, Any]:
    value = data.get(name)
    if not isinstance(value, dict):
        raise ValueError("Missing or invalid TOML section [{}].".format(name))
    return value


def _tuple3(value: Sequence[Any], label: str) -> Tuple[float, float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError("{} must contain exactly three numbers.".format(label))
    return (float(value[0]), float(value[1]), float(value[2]))


def load_config(filename: str = "input.toml") -> SimulationConfig:
    source_path = Path(filename).expanduser().resolve()
    if not source_path.is_file():
        raise FileNotFoundError("Input file not found: {}".format(source_path))

    data = _load_toml(source_path)

    problem_data = _section(data, "problem")
    mesh_data = _section(data, "mesh")
    geometry_data = _section(data, "geometry")
    fe_data = _section(data, "finite_element")
    material_data = _section(data, "material")
    fracture_data = _section(data, "fracture")
    loads_data = _section(data, "loads")
    gravity_data = _section(loads_data, "gravity")
    hydrostatic_data = _section(loads_data, "hydrostatic")
    adaptivity_data = _section(data, "adaptivity")
    solver_data = _section(data, "solver")
    output_data = _section(data, "output")
    logging_data = _section(data, "logging")
    write_checkpoint_data = data.get("write_checkpoint", {})
    restart_checkpoint_data = data.get("restart_checkpoint", {})
    if not isinstance(write_checkpoint_data, dict):
        raise ValueError("[write_checkpoint] must be a TOML table.")
    if not isinstance(restart_checkpoint_data, dict):
        raise ValueError("[restart_checkpoint] must be a TOML table.")

    boundary_rows = data.get("boundary_conditions", [])
    if not isinstance(boundary_rows, list):
        raise ValueError("[[boundary_conditions]] must be a TOML array of tables.")

    boundary_conditions: List[BoundaryConditionConfig] = []
    for row in boundary_rows:
        if not isinstance(row, dict):
            raise ValueError("Each boundary condition must be a TOML table.")
        component = row.get("component")
        boundary_conditions.append(
            BoundaryConditionConfig(
                name=str(row["name"]),
                boundary=str(row["boundary"]),
                type=str(row.get("type", "dirichlet")).lower(),
                component=None if component is None else int(component),
                value=row["value"],
            )
        )

    config = SimulationConfig(
        source_path=source_path,
        root_directory=source_path.parent,
        problem=ProblemMetadata(
            name=str(problem_data.get("name", "phase-field problem")),
            model=str(problem_data.get("model", "stress_cdf")),
            precrack_depth_ratio=float(problem_data.get("precrack_depth_ratio", 0.0)),
        ),
        mesh=MeshConfig(path=str(mesh_data["path"])),
        geometry=GeometryConfig(
            Lx=float(geometry_data["Lx"]),
            Ly=float(geometry_data["Ly"]),
            Lz=float(geometry_data["Lz"]),
        ),
        finite_element=FiniteElementConfig(
            displacement_family=str(fe_data.get("displacement_family", "CG")),
            displacement_degree=int(fe_data.get("displacement_degree", 1)),
            damage_family=str(fe_data.get("damage_family", "CG")),
            damage_degree=int(fe_data.get("damage_degree", 1)),
            history_family=str(fe_data.get("history_family", "DG")),
            history_degree=int(fe_data.get("history_degree", 0)),
        ),
        material=MaterialConfig(
            youngs_modulus=float(material_data["youngs_modulus"]),
            poissons_ratio=float(material_data["poissons_ratio"]),
            ice_density=float(material_data["ice_density"]),
            freshwater_density=float(material_data["freshwater_density"]),
            seawater_density=float(material_data["seawater_density"]),
        ),
        fracture=FractureConfig(
            length_scale=float(fracture_data["length_scale"]),
            critical_stress=float(fracture_data["critical_stress"]),
            energy_threshold=float(fracture_data["energy_threshold"]),
            zeta=float(fracture_data.get("zeta", 1.0)),
            residual_stiffness=float(fracture_data.get("residual_stiffness", 1.0e-4)),
        ),
        gravity=GravityConfig(
            enabled=bool(gravity_data.get("enabled", True)),
            acceleration=float(gravity_data.get("acceleration", 9.81)),
            direction=_tuple3(gravity_data.get("direction", [0.0, 0.0, -1.0]), "loads.gravity.direction"),
        ),
        hydrostatic=HydrostaticConfig(
            enabled=bool(hydrostatic_data.get("enabled", True)),
            boundary=str(hydrostatic_data.get("boundary", "right")),
            marker=int(hydrostatic_data.get("marker", 1)),
            density_source=str(hydrostatic_data.get("density_source", "seawater")).lower(),
            water_height_ratio=float(hydrostatic_data.get("water_height_ratio", 0.5)),
            component=int(hydrostatic_data.get("component", 1)),
            sign=float(hydrostatic_data.get("sign", -1.0)),
            degree=int(hydrostatic_data.get("degree", 1)),
        ),
        boundary_conditions=tuple(boundary_conditions),
        adaptivity=AdaptivityConfig(
            enabled=bool(adaptivity_data.get("enabled", True)),
            target_hmin=float(adaptivity_data["target_hmin"]),
            damage_threshold=float(adaptivity_data["damage_threshold"]),
        ),
        solver=SolverConfig(
            linear_solver=str(solver_data.get("linear_solver", "gmres")),
            preconditioner=str(solver_data.get("preconditioner", "hypre_euclid")),
            projection_linear_solver=str(solver_data.get("projection_linear_solver", "gmres")),
            projection_preconditioner=str(solver_data.get("projection_preconditioner", "hypre_euclid")),
            outer_tolerance=float(solver_data.get("outer_tolerance", 1.0e-4)),
            norm_zero_tolerance=float(solver_data.get("norm_zero_tolerance", 1.0e-14)),
        ),
        output=OutputConfig(
            directory=str(output_data["directory"]),
            filename=str(output_data.get("filename", "output.xdmf")),
            write_csv=bool(output_data.get("write_csv", True)),
            csv_filename=str(output_data.get("csv_filename", "metrics.csv")),
            write_every=int(output_data.get("write_every", 1)),
            write_damage=bool(output_data.get("write_damage", True)),
            write_displacement=bool(output_data.get("write_displacement", False)),
            functions_share_mesh=bool(output_data.get("functions_share_mesh", True)),
            rewrite_function_mesh=bool(output_data.get("rewrite_function_mesh", True)),
            flush_output=bool(output_data.get("flush_output", True)),
        ),
        write_checkpoint=CheckpointConfig(
            enabled=bool(write_checkpoint_data.get("enabled", False)),
            filename=str(
                write_checkpoint_data.get(
                    "filename", str(Path(output_data["directory"]) / "checkpoint.h5")
                )
            ),
        ),
        restart_checkpoint=CheckpointConfig(
            enabled=bool(restart_checkpoint_data.get("enabled", False)),
            filename=str(restart_checkpoint_data.get("filename", "checkpoint.h5")),
        ),
        logging=LoggingConfig(
            level=str(logging_data.get("level", "ERROR")).upper(),
            print_initial_hmin=bool(logging_data.get("print_initial_hmin", True)),
            garbage_collect_every=int(logging_data.get("garbage_collect_every", 5)),
        ),
    )

    validate_config(config)
    return config


def validate_config(config: SimulationConfig) -> None:
    valid_boundaries = {"front", "back", "left", "right", "bottom", "top"}

    if min(config.geometry.Lx, config.geometry.Ly, config.geometry.Lz) <= 0.0:
        raise ValueError("All geometry dimensions must be positive.")
    if config.material.youngs_modulus <= 0.0:
        raise ValueError("material.youngs_modulus must be positive.")
    if not (-1.0 < config.material.poissons_ratio < 0.5):
        raise ValueError("material.poissons_ratio must lie between -1 and 0.5.")
    if config.problem.model != "stress_cdf":
        raise ValueError("Only problem.model = 'stress_cdf' is implemented in this validated refactor.")
    history_family = config.finite_element.history_family.upper()
    if history_family not in {"DG", "DISCONTINUOUS LAGRANGE"} or config.finite_element.history_degree != 0:
        raise ValueError(
            "The validated AMR implementation requires a DG0 history space."
        )
    if config.fracture.length_scale <= 0.0:
        raise ValueError("fracture.length_scale must be positive.")
    if config.fracture.critical_stress <= 0.0:
        raise ValueError("fracture.critical_stress must be positive.")
    if config.fracture.residual_stiffness < 0.0:
        raise ValueError("fracture.residual_stiffness cannot be negative.")
    if config.adaptivity.target_hmin <= 0.0:
        raise ValueError("adaptivity.target_hmin must be positive.")
    if not (0.0 <= config.adaptivity.damage_threshold <= 1.0):
        raise ValueError("adaptivity.damage_threshold must lie in [0, 1].")
    if config.hydrostatic.boundary not in valid_boundaries:
        raise ValueError("Unknown hydrostatic boundary: {}".format(config.hydrostatic.boundary))
    if config.hydrostatic.density_source not in {"ice", "freshwater", "seawater"}:
        raise ValueError("loads.hydrostatic.density_source must be ice, freshwater, or seawater.")
    if config.hydrostatic.water_height_ratio < 0.0:
        raise ValueError("loads.hydrostatic.water_height_ratio cannot be negative.")
    if config.hydrostatic.component not in (0, 1, 2):
        raise ValueError("loads.hydrostatic.component must be 0, 1, or 2.")
    if config.output.write_every < 1:
        raise ValueError("output.write_every must be at least 1.")
    if config.output.write_csv and not config.output.csv_filename:
        raise ValueError("output.csv_filename cannot be empty when CSV output is enabled.")
    if config.logging.garbage_collect_every < 0:
        raise ValueError("logging.garbage_collect_every cannot be negative.")
    if config.write_checkpoint.enabled and not config.write_checkpoint.filename:
        raise ValueError("write_checkpoint.filename cannot be empty when enabled.")
    if config.restart_checkpoint.enabled and not config.restart_checkpoint.filename:
        raise ValueError("restart_checkpoint.filename cannot be empty when enabled.")

    for condition in config.boundary_conditions:
        if condition.type != "dirichlet":
            raise ValueError("Unsupported boundary condition type: {}".format(condition.type))
        if condition.boundary not in valid_boundaries:
            raise ValueError("Unknown boundary '{}' in {}.".format(condition.boundary, condition.name))
        if condition.component is not None and condition.component not in (0, 1, 2):
            raise ValueError("Boundary component must be 0, 1, or 2 in {}.".format(condition.name))
        if condition.component is None:
            if not isinstance(condition.value, (list, tuple)) or len(condition.value) != 3:
                raise ValueError(
                    "A full-vector boundary condition requires three values in {}.".format(
                        condition.name
                    )
                )
