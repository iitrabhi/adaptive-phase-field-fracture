from dolfin import *
import ufl as ufl


class MaterialModel:
    def __init__(self, E0=9500e6, nu=0.35, rho=917 * 9.81, stress_c=0.1185e6, ci=1):
        # Initialize material parameters
        self.E0 = E0
        self.nu = nu
        self.rho = rho
        self.critical_stress = stress_c
        self.critical_energy = 0.5 * stress_c**2 / (2 * E0)

        self.mu = self.E0 / (2 * (1 + self.nu))
        self.lmbda = self.E0 * self.nu / ((1 + self.nu) * (1 - 2 * self.nu))
        self.ci = ci

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
        return get_eigenstate(self.strain(u))

    def get_principal_stress(self, u):
        return get_eigenstate(self.stress(u))

    def get_crack_driving_force(self, u):
        stress_plus, _ = split_plus_minus(self.get_principal_stress(u))
        cdf_expr = self.ci * (
            (stress_plus[0, 0] / self.critical_stress) ** 2
            + (stress_plus[1, 1] / self.critical_stress) ** 2
            - 1
        )
        cdf_expr = ufl.Max(cdf_expr, 0)
        # Apply the threshold condition
        threshold = 15  # Set the threshold value
        cdf_expr = ufl.conditional(ufl.le(cdf_expr, threshold), 0, cdf_expr)

        return cdf_expr


# Helper functions -------------------------------------------------
def applyElementwise(f, T):
    sh = ufl.shape(T)
    if len(sh) == 0:
        return f(T)
    fT = []
    for i in range(0, sh[0]):
        fT += [applyElementwise(f, T[i])]
    return as_tensor(fT)


def split_plus_minus(T):
    x_plus = applyElementwise(lambda x: 0.5 * (abs(x) + x), T)
    x_minus = applyElementwise(lambda x: 0.5 * (abs(x) - x), T)
    return x_plus, x_minus


def get_eigenstate(t):
    eig1 = 0.5 * (tr(t) + safeSqrt(tr(t) * tr(t) - 4 * det(t)))
    eig2 = 0.5 * (tr(t) - safeSqrt(tr(t) * tr(t) - 4 * det(t)))
    return as_tensor([[eig1, 0], [0, eig2]])


def safePower(x, pw):
    # return pow(x + DOLFIN_EPS, pw)
    return pow(x, pw)


def safeSqrt(x):
    return sqrt(x + DOLFIN_EPS)


def degradation(p):
    return (1 - p) ** 2 + 1e-4
