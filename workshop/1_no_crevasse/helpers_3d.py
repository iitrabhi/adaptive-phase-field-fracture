from dolfin import *
import ufl as ufl


class MaterialModel:
    def __init__(self, E0=9500e6, nu=0.35, rho=917, stress_c=0.1185e6):
        # Initialize material parameters
        self.E0 = E0
        self.nu = nu
        self.rho = rho
        self.critical_stress = stress_c
        self.mu = self.E0 / (2 * (1 + self.nu))
        self.lmbda = self.E0 * self.nu / ((1 + self.nu) * (1 - 2 * self.nu))

    def strain(self, u):
        return 0.5 * (grad(u) + grad(u).T)

    def stress(self, u):
        return 2.0 * self.mu * self.strain(u) + self.lmbda * tr(
            self.strain(u)
        ) * Identity(len(u))

    def get_strain_energy(self, u):
        return self.lmbda / 2 * (tr(self.strain(u)) ** 2) + self.mu * tr(
            self.strain(u) * self.strain(u)
        )

    def get_principal_strain(self, u):
        return principal_tensor(self.strain(u))

    def get_principal_stress(self, u):
        return principal_tensor(self.stress(u))

    def get_crack_driving_force(self, u, ci=1):
        stress_plus, _ = split_plus_minus(get_eigenstate(self.stress(u)))
        energy_expr = ci * (
            (stress_plus[0, 0] / self.critical_stress) ** 2
            + (stress_plus[1, 1] / self.critical_stress) ** 2
            + (stress_plus[2, 2] / self.critical_stress) ** 2
            - 1
        )
        energy_expr = ufl.Max(energy_expr, 0)
        return energy_expr


# Helper functions -------------------------------------------------
def applyElementwise(f, T):
    tensor_shape = ufl.shape(T)

    if len(tensor_shape) == 0:
        return f(T)

    diagonal = []

    for index in range(0, tensor_shape[0]):
        diagonal += [applyElementwise(f, T[index, index])]

    return as_tensor(
        [[diagonal[0], 0, 0], [0, diagonal[1], 0], [0, 0, diagonal[2]]]
    )


def split_plus_minus(T):
    positive = applyElementwise(lambda value: 0.5 * (abs(value) + value), T)

    negative = applyElementwise(lambda value: 0.5 * (abs(value) - value), T)

    return positive, negative


def get_eigenstate(t):
    if ufl.shape(t) != (3, 3):
        raise RuntimeError(
            "Tensor A of shape {} != (3, 3) is not supported!".format(ufl.shape(t))
        )

    eps = 1.0e-10

    t = ufl.variable(t)

    q = ufl.tr(t) / 3

    deviator = t - q * ufl.Identity(3)

    j = ufl.tr(deviator * deviator) / 2

    b = ufl.tr(deviator * deviator * deviator) / 3

    p = 2 / ufl.sqrt(3) * ufl.sqrt(j + eps**2)

    r = 4 * b / p**3

    r = ufl.Max(
        ufl.Min(r, 1 - eps),
        -1 + eps,
    )

    phi = ufl.acos(r) / 3

    eig1 = q + p * ufl.cos(phi)

    eig2 = q + p * ufl.cos(phi + 4 / 3 * ufl.pi)

    eig3 = q + p * ufl.cos(phi + 2 / 3 * ufl.pi)

    return as_tensor(
        [
            [eig1, 0, 0],
            [0, eig2, 0],
            [0, 0, eig3],
        ]
    )


def safePower(x, pw):
    # return pow(x + DOLFIN_EPS, pw)
    return pow(x, pw)


def safeSqrt(x):
    return sqrt(x + DOLFIN_EPS)
