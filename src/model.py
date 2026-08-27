"""Constitutive relations, stress split, history driver, and weak forms."""

from dolfin import *

try:
    import ufl_legacy as ufl
except ImportError:  
    import ufl

shape = ufl.shape

from .config import SimulationConfig


def epsilon(displacement):
    return 0.5 * (grad(displacement) + grad(displacement).T)


def sigma(displacement, config: SimulationConfig):
    mu = config.material.shear_modulus
    lame_lambda = config.material.lame_lambda
    return (
        2.0 * mu * epsilon(displacement)
        + lame_lambda * tr(epsilon(displacement)) * Identity(len(displacement))
    )


def invariants_principal(tensor):
    """Principal invariants of a real-valued tensor."""
    i1 = ufl.tr(tensor)
    i2 = (ufl.tr(tensor) ** 2 - ufl.tr(tensor * tensor)) / 2
    i3 = ufl.det(tensor)
    return i1, i2, i3


def invariants_main(tensor):
    """Main invariants of a real-valued tensor."""
    j1 = ufl.tr(tensor)
    j2 = ufl.tr(tensor * tensor)
    j3 = ufl.tr(tensor * tensor * tensor)
    return j1, j2, j3


def get_eigenstate(tensor):
    """Return the ordered principal values of a real 3x3 tensor."""
    if ufl.shape(tensor) != (3, 3):
        raise RuntimeError(
            "Tensor A of shape {} != (3, 3) is not supported!".format(ufl.shape(tensor))
        )

    eps = 1.0e-10
    tensor = ufl.variable(tensor)

    q = ufl.tr(tensor) / 3
    deviator = tensor - q * ufl.Identity(3)
    j = ufl.tr(deviator * deviator) / 2
    b = ufl.tr(deviator * deviator * deviator) / 3

    p = 2 / ufl.sqrt(3) * ufl.sqrt(j + eps ** 2)
    r = 4 * b / p ** 3
    r = ufl.Max(ufl.Min(r, +1 - eps), -1 + eps)
    phi = ufl.acos(r) / 3

    lambda_0 = q + p * ufl.cos(phi + 2 / 3 * ufl.pi)
    lambda_1 = q + p * ufl.cos(phi + 4 / 3 * ufl.pi)
    lambda_2 = q + p * ufl.cos(phi)

    return as_tensor(
        [[lambda_2, 0, 0], [0, lambda_1, 0], [0, 0, lambda_0]]
    )


def apply_elementwise(function, tensor):
    tensor_shape = shape(tensor)
    if len(tensor_shape) == 0:
        return function(tensor)

    diagonal = []
    for index in range(0, tensor_shape[0]):
        diagonal += [apply_elementwise(function, tensor[index, index])]

    return as_tensor(
        [[diagonal[0], 0, 0], [0, diagonal[1], 0], [0, 0, diagonal[2]]]
    )


def split_plus_minus(tensor):
    positive = apply_elementwise(lambda value: 0.5 * (abs(value) + value), tensor)
    negative = apply_elementwise(lambda value: 0.5 * (abs(value) - value), tensor)
    return positive, negative


def safe_sqrt(value):
    return sqrt(value + DOLFIN_EPS)


def get_energy(displacement, damage, history_space, config: SimulationConfig):
    """Stress-based crack-driving field from the validated implementation."""

    stress_plus, _ = split_plus_minus(
        get_eigenstate(sigma(displacement, config))
    )

    critical_stress = config.fracture.critical_stress
    energy_expression =  (
        (stress_plus[0, 0] / critical_stress) ** 2
        + (stress_plus[1, 1] / critical_stress) ** 2
        + (stress_plus[2, 2] / critical_stress) ** 2
        - 1
    )
    energy_expression = ufl.Max(energy_expression, 0)
    energy_expression = ufl.conditional(
        ufl.le(energy_expression, config.fracture.energy_threshold),
        0,
        energy_expression,
    )
    return config.fracture.zeta * energy_expression


def displacement_forms(
    trial_displacement,
    test_displacement,
    old_damage,
    body_force,
    traction,
    boundary_measure,
    traction_marker: int,
    config: SimulationConfig,
):
    bilinear_form = inner(
        (
            (1 - old_damage) ** 2
            + config.fracture.residual_stiffness
        )
        * sigma(trial_displacement, config),
        epsilon(test_displacement),
    ) * dx

    load_switch = conditional(
        gt(old_damage, 0.6),
        0.0,
        1.0,
    )
    linear_form = (
        load_switch * dot(body_force, test_displacement) * dx
        + dot(traction, test_displacement) * boundary_measure(traction_marker)
    )
    return bilinear_form, linear_form


def phase_field_forms(
    trial_damage,
    test_damage,
    history,
    config: SimulationConfig,
):
    length_scale = config.fracture.length_scale
    bilinear_form = (
        length_scale ** 2 * inner(grad(trial_damage), grad(test_damage))
        + inner(trial_damage, test_damage)
        + history * inner(trial_damage, test_damage)
    ) * dx
    linear_form = inner(history, test_damage) * dx
    return bilinear_form, linear_form
