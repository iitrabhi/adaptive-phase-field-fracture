import ufl
import matplotlib.pyplot as plt
import time
import numpy as np
from dolfin import *
import csv
#Notchx multiple cracks:
# Mesh_new_nont /solution_hw05-incom-no-49-60
# 0.5 -3 th
# 0.3/0.2 -3 th
comm = MPI.comm_world  # MPI communicator
#Mesh_new_nont
mesh = Mesh()
with XDMFFile(comm, "mesh/ice.xdmf") as infile:
    infile.read(mesh)


xdmf = XDMFFile(comm, "output/solution_hw05_test_no_de.xdmf")
xdmf.parameters["functions_share_mesh"] = True
xdmf.parameters["rewrite_function_mesh"] = False
xdmf.parameters["flush_output"] = True

# Specify the CSV file path
csv_file_path = "output/crevasse_depth"+".csv"
file = open(csv_file_path, mode='w', newline='')
writer = csv.writer(file)

hs_ratio = 0.0  # water level in crevasse (normalized with crevasse height)
hw_ratio = 0.5  # water level at right terminus (normalized with glacier thickness)
prec_ratio = 0.08  # depth of pre-crack (normalized with glacier thickness)
# energy_thsd = 0.6348 #62.94  # 
# energy_thsd = 4 #62.94  # 

energy_thsd = 10  # incompresible thres = 40
# energy_thsd = 30


L, H = 500, 125

# ---------------------------------------------------------------------------------
# MATERIAL PARAMETERS     ------------------------------------------------
# ---------------------------------------------------------------------------------

rho_ice = 917  # density of ice (kg/m^3)
rho_H2O = 1000  # density of freshwater (kg/m^3)
rho_sea = 1020  # density of seawater (kg/m^3)
grav = 9.81  # gravity acceleration (m/s**2)
E = 9.5e9  # Young's modulus (Pa)
nu = 0.35  # Poisson's ratio
mu = E / 2 / (1 + nu)  # shear modulus
K = E / 3 / (1 - 2 * nu)  # bulk modulus
lmbda = K - 2 / 3 * mu  # Lame's first parameter
KIc = 0.1e6  # critical stress intensity factor (Pa*m^0.5)
lc = 0.625  # nonlocal length scale (m)
# lc = 0.1  # nonlocal length scale (m)
eta = 5e1  # viscous regularization parameter (N*s/m)
# eta = Constant(0.0)
# eta = 0.0
g1c = (KIc**2) * (1 - nu**2) / E  # critical strain energy release rate (Pa*m)
g2c = (
    10 * g1c
)  # assumed critical strain energy release rate for mode II fracture (Pa*m)
hw = hw_ratio * H  # water level at terminus (absolute height)
ci = 1
# sigmac = 0.1185e6  # critical stress only for stress based method

sigmac = np.sqrt((1-nu**2)*KIc**2/lc)
print(sigmac)

# ---------------------------------------------------------------------------------
# SIMULATION PARAMETERS        ------------------------------------------------
# ---------------------------------------------------------------------------------
time_elapsed = 0
time_total = 1000  # arbitrary
delta_t = 1.0  # time increment
time_counter = 0
output_increment = 5

Dcr = 0.6
air, water, ice = 0, 1, 2
water_left, water_right = 3, 4
right = 2

# ---------------------------------------------------------------------------------
# PARAMETERS FOR PARALLEL COMPUTATIONS   -----------------------------
# ---------------------------------------------------------------------------------


rank = comm.Get_rank()  # number of current process
size = comm.Get_size()  # total number of processes


def mwrite(filename, my_list):
    MPI.barrier(comm)
    if rank == 0:
        with open(filename, "w") as f:
            for item in my_list:
                f.write("%s" % item)


def mprint(*argv):
    if rank == 0:
        out = ""
        for arg in argv:
            out = out + str(arg)
        # this forces program to output when run in parallel
        print(out, flush=True)


# ---------------------------------------------------------------------------------
# SET SOME COMMON FENICS FLAGS     ---------------------------------------
# ---------------------------------------------------------------------------------
set_log_level(50)
parameters["form_compiler"]["optimize"] = True
parameters["form_compiler"]["cpp_optimize"] = True


# ---------------------------------------------------------------------------------
# MATERIAL MODEL  --------------------------------------------------------
# ---------------------------------------------------------------------------------
def epsilon(u):
    return 0.5 * (grad(u) + grad(u).T)


def sigma(u):
    return 2.0 * mu * epsilon(u) + lmbda * tr(epsilon(u)) * Identity(len(u))


# ---------------------------------------------------------------------------------
# ICE FRACTURE     --------------------------------------------------------
# ---------------------------------------------------------------------------------
def get_crack_tip_coord(dmg, damage_threshold=0.99):
    dmg_dg_1 = project(dmg, D1)
    coord_vec = y_co_ord.vector()[dmg_dg_1.vector()[:] >= damage_threshold]
    coord = 115  # ToDo: Change this
    if coord_vec.size > 0:
        coord = coord_vec.min()
    return MPI.min(comm, coord)


# As the crack will propogate it will change the crevasse depth
# Thus, I have to make a mesh function that will update the zones
# of air, water and ice

# Start with complete ice.
# Mark the zone where damage is > Dcr as air
# Mark the water zone


def get_density_mf(dmg, Dcr=0.99):
    density_mf = MeshFunction("size_t", mesh, 2)
    density_mf.set_all(ice)
    density_mf.array()[dmg.vector()[:] > Dcr] = air
    crevasse_depth, water_surface_from_bottom = surface_crevasse_level(dmg)
    water_zone = Function(D)
    water_zone.interpolate(
        Expression(
            "x[1]>zs && x[1]<wl?1:0",
            zs=H - crevasse_depth,
            wl=water_surface_from_bottom,
            degree=1,
        )
    )

    # water_zone_left = Function(D)
    # water_zone_left.interpolate(
    #     Expression(
    #         "x[1]>zs && x[1]<wl?1:0 && x[0]<250",
    #         zs=H - crevasse_depth,
    #         wl=water_surface_from_bottom,
    #         degree=1,
    #     )
    # )

    # water_zone_right = Function(D)
    # water_zone_right.interpolate(
    #     Expression(
    #         "x[1]>zs && x[1]<wl?1:0 && x[0]>250",
    #         zs=H - crevasse_depth,
    #         wl=water_surface_from_bottom,
    #         degree=1,
    #     )
    # )

    density_mf.array()[
        np.multiply(dmg.vector()[:] > Dcr, water_zone.vector()[:] > 0)
    ] = water
    density_mf.array()
    return density_mf


def surface_crevasse_level(dmg):
    # We have to figure out the crevasse_depth from top and the
    # crevasse_surface from bottom. We have the damage function
    x2_dmg_min = get_crack_tip_coord(dmg, damage_threshold=0.6)
    crevasse_depth = H - x2_dmg_min
    water_surface_from_bottom = crevasse_depth * hs_ratio + x2_dmg_min
    return crevasse_depth, water_surface_from_bottom


# ---------------------------------------------------------------------------------
# ENERGY CALCULATIONS        ------------------------------------------------
# ---------------------------------------------------------------------------------
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


def safeSqrt(x):
    return sqrt(x + DOLFIN_EPS)


def principal_tensor(t):
    eig1 = 0.5 * (tr(t) + safeSqrt(tr(t) * tr(t) - 4 * det(t)))
    eig2 = 0.5 * (tr(t) - safeSqrt(tr(t) * tr(t) - 4 * det(t)))
    return as_tensor([[eig1, 0], [0, eig2]])



def get_energy(disp, type="stress"):
    if type == "stress":
        principal_stress = principal_tensor(sigma(unew))
        stress_plus, stress_minus = split_plus_minus(principal_stress)
        # for sum
        energy_expr = ci * (((stress_plus[0, 0])**2 + (stress_plus[1, 1])**2)/sigmac ** 2  - 1)
        # for maximum principal stresses
        # s1 = ufl.Max(stress_plus[0, 0],0)**2
        # s2 = ufl.Max(stress_plus[1, 1],0)**2    
        # stressx = ufl.conditional(ufl.le(s1,s2), s2, s1) 
        # energy_expr = ci * (stressx/sigmac ** 2  - 1)

        energy_expr = ufl.Max(energy_expr, 0)
        # Apply the threshold condition
        energy_expr = ufl.conditional(ufl.le(energy_expr, energy_thsd), 0, energy_expr)

        energy = project(energy_expr, D).vector()[:]
        # energy = assemble(energy_expr*TestFunction(D)*dx())
    else:
        eig = principal_tensor(epsilon(disp))
        eig_1, eig_2 = eig[0, 0], eig[1, 1]

        # Define the energy function
        energy_expr = ufl.conditional(
            ufl.ge(eig_2, 0),
            (0.5 * lmbda * (eig_1 + eig_2) ** 2 + mu * (eig_1**2 + eig_2**2)) / g1c,
            ufl.conditional(
                ufl.And(ufl.ge(eig_1, 0), ufl.le(eig_2, 0)),
                conditional(
                    ufl.gt((1 - nu) * eig_1 + nu * eig_2, 0),
                    (0.5 * lmbda / nu / (1 - nu) * ((1 - nu) * eig_1 + nu * eig_2) ** 2)
                    / g1c,
                    0,
                ),
                0,
            ),
        )

        # Apply the threshold condition
        energy_expr = ufl.conditional(ufl.le(energy_expr, energy_thsd), 0, energy_expr)
        # https://fenicsproject.discourse.group/t/unable-to-use-conditional-module/6502
        energy = assemble(energy_expr * TestFunction(D) * dx())

    return energy


#  ▄▄       ▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄        ▄
# ▐░░▌     ▐░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░▌      ▐░▌
# ▐░▌░▌   ▐░▐░▌▐░█▀▀▀▀▀▀▀█░▌ ▀▀▀▀█░█▀▀▀▀ ▐░▌░▌     ▐░▌
# ▐░▌▐░▌ ▐░▌▐░▌▐░▌       ▐░▌     ▐░▌     ▐░▌▐░▌    ▐░▌
# ▐░▌ ▐░▐░▌ ▐░▌▐░█▄▄▄▄▄▄▄█░▌     ▐░▌     ▐░▌ ▐░▌   ▐░▌
# ▐░▌  ▐░▌  ▐░▌▐░░░░░░░░░░░▌     ▐░▌     ▐░▌  ▐░▌  ▐░▌
# ▐░▌   ▀   ▐░▌▐░█▀▀▀▀▀▀▀█░▌     ▐░▌     ▐░▌   ▐░▌ ▐░▌
# ▐░▌       ▐░▌▐░▌       ▐░▌     ▐░▌     ▐░▌    ▐░▌▐░▌
# ▐░▌       ▐░▌▐░▌       ▐░▌ ▄▄▄▄█░█▄▄▄▄ ▐░▌     ▐░▐░▌
# ▐░▌       ▐░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░▌      ▐░░▌
#  ▀         ▀  ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀        ▀▀


# ---------------------------------------------------------------------------------
# FUNCTION SPACES  ---------------------------------------------------------
# ---------------------------------------------------------------------------------
V = VectorFunctionSpace(mesh, "CG", 1)  # displacement shape function
S = FunctionSpace(mesh, "CG", 1)
D = FunctionSpace(mesh, "DG", 0)  # phase-field shape function
D1 = FunctionSpace(mesh, "DG", 1)

mprint("Number of vertices      : {}".format(S.dim()))
mprint("Number of cells         : {}".format(D.dim()))
mprint("Number of DoF           : {}".format(V.dim()))
mprint("Number of processes     : {}".format(size))
mprint("Number of DoF/process   : {}".format(int(V.dim() / size)))
mprint("-----------------------------------------------------")

# ---------------------------------------------------------------------------------
# BOUNDARIES AND MEASURES    ------------------------------------------------
# ---------------------------------------------------------------------------------
# notch_hight = 10 
left = CompiledSubDomain("near(x[0], 0)")
right_csd = CompiledSubDomain("near(x[0], L)", L=L)
bottom = CompiledSubDomain("near(x[1], 0)")
top = CompiledSubDomain("near(x[1], H)", H=H)

Xt = 250
Xn = 1.25
cracktip_coor = 115

left_wall = CompiledSubDomain("near(x[0], Xg) && x[1] >= Xf", Xg=Xt-Xn, Xf=cracktip_coor)
right_wall = CompiledSubDomain("near(x[0], Xr) && x[1] >= Xf", Xr=Xt+Xn, Xf=cracktip_coor)
bottom_wall = CompiledSubDomain("near(x[1], Yb) && x[0] >= Xg && x[0] <= Xr", Xg=Xt-Xn, Xr=Xt+Xn, Yb=cracktip_coor)

# bottom = CompiledSubDomain("near(x[1], nt)", nt = notch_hight = 10 
# )


bottom_roller = DirichletBC(V.sub(1), Constant(0), bottom)
left_roller = DirichletBC(V.sub(0), Constant(0), left)

disp_bc = [bottom_roller, left_roller]

y_co_ord = Function(D1)
y_co_ord.interpolate(Expression("x[1]", degree=1))

boundaries = MeshFunction("size_t", mesh, mesh.topology().dim() - 1)
left.mark(boundaries, 1)
right_csd.mark(boundaries, right)
bottom.mark(boundaries, 3)
top.mark(boundaries, 4)
ds = Measure("ds", subdomain_data=boundaries)


# ---------------------------------------------------------------------------------
# FUNCTIONS    --------------------------------------------------------------
# ---------------------------------------------------------------------------------

u, v = TrialFunction(V), TestFunction(V)
p, q = TrialFunction(D), TestFunction(D)

unew, uold = Function(V, name="displacement"), Function(V)
pnew, pold = Function(D, name="damage"), Function(D)
Hold = Function(D)
energy = Function(D, name="energy")
cdf = Function(D)
# ---------------------------------------------------------------------------------
# PRE-CRACK ZONES -----------------------------------------------------------
# ---------------------------------------------------------------------------------
cracktip_coor = H * (1 - prec_ratio)
# pre_crack_zone = Expression(
#     "x[1]>=H*(1 - prec_ratio) && (L - 4*lc)/2 < x[0] && x[0] < (L + 4*lc)/2?0.99:0",
#     L=L,
#     H=H,
#     lc=lc,
#     prec_ratio=prec_ratio,
#     degree=1,
# )
# pold.interpolate(pre_crack_zone)
# ---------------------------------------------------------------------------------
# PHASE FIELD PROBLEM      -----------------------------------------------
# ---------------------------------------------------------------------------------
# phase_a = (eta / delta_t + 1 / lc + 2 * cdf) * inner(p, q) * dx + lc * inner(
#     grad(p), grad(q)
# ) * dx
# phase_L = inner(q, 2 * cdf) * dx + eta / delta_t * inner(q, pold) * dx

# phase_a = (eta / delta_t + 1 + cdf) * inner(p, q) * dx + lc*lc * inner(
#     grad(p), grad(q)
# ) * dx
# phase_L = inner(q, cdf) * dx + eta / delta_t * inner(q, pold) * dx

phase_a = (lc**2 * inner(grad(p), grad(q)) + (1) * inner(p, q)+ cdf * inner(p, q))*dx
phase_L = inner(cdf, q) * dx 

phase_problem = LinearVariationalProblem(phase_a, phase_L, pnew)
phase_solver = LinearVariationalSolver(phase_problem)

prm_phase = phase_solver.parameters
prm_phase["linear_solver"] = "cg"
prm_phase["preconditioner"] = "hypre_euclid"
# ---------------------------------------------------------------------------------
# START ITERATIONS    -----------------------------------------------------
# ---------------------------------------------------------------------------------

start = time.time()

def Psi(p):
    pis = ufl.conditional(ufl.le(p, 0.6), 1, 0)
    return pis

def Psi_inverse(p):
    Inv = ufl.conditional(ufl.le(p, 0.6), 0, 1)
    return Inv


while time_elapsed <= time_total:
    # while time_counter <= 300:
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    crevasse_depth, water_surface_from_bottom = surface_crevasse_level(pold)
    dx = Measure("dx", subdomain_data=get_density_mf(pold))

    disp_a = inner(((1 - pold) ** 2 + 1e-4) * sigma(u), epsilon(v)) * dx
    # disp_L = inner(v, Constant((0, -rho_ice * grav))) * dx(ice)
    # disp_L = Psi(pold)*inner(v, Constant((0, -rho_ice * grav))) * dx
    # disp_L = (1-pold)*inner(v, Constant((0, -rho_ice * grav))) * dx
    disp_L = ((1 - pold) ** 2 + 1e-4)*inner(v, Constant((0, -rho_ice * grav))) * dx



    # disp_L += inner(v, Constant((0, -rho_H2O * grav))) * dx(water)  # check carefully?

    b_hw = Expression(
        ("(h - x[1] > 0 ?-rho_H2O * grav*(h - x[1]) : 0)", 0),
        h=hw,
        rho_H2O=rho_H2O,
        grav=grav,
        degree=1,
    )

    b_poro = Expression(
        "(wl - x[1] > 0 ? rho_H2O * grav*(wl - x[1]) : 0)",
        rho_H2O=rho_H2O,
        grav=grav,
        wl=water_surface_from_bottom,
        degree=1,
    )

    # b_poro = Expression(
    #     "rho_H2O*grav*(x[1]-wl)",
    #     rho_H2O=rho_H2O,
    #     grav=grav,
    #     wl=water_surface_from_bottom,
    #     degree=1,
    # )

    if hs_ratio > 0:
        # disp_L += inner(div(v), (1 - (1-pold) ** 2 ) * b_poro) * dx
        disp_L += inner(div(v),  Psi_inverse(pold)* b_poro) * dx

        # disp_L += Psi(pold)*inner(div(v), (pold) * b_poro) * dx

        # disp_L += Psi(pold)*inner(div(v), (1 - (1-pold) ** 2) * b_poro) * dx(water)


    if hw_ratio > 0:
        disp_L += inner(v, b_hw) * ds(right)  # terminus pressure

    unew = Function(V, name="displacement")
    disp_problem = LinearVariationalProblem(disp_a, disp_L, unew, disp_bc)
    disp_solver = LinearVariationalSolver(disp_problem)

    prm_disp = disp_solver.parameters
    prm_disp["linear_solver"] = "cg"
    prm_disp["preconditioner"] = "hypre_euclid"
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    disp_solver.solve()

    # update history variable --------------------------------------------------
    energy.vector().vec().array[:] = get_energy(unew)[:]
    energy.vector().vec().array[:] = np.maximum(energy.vector()[:], cdf.vector()[:])
    cdf.assign(energy)

    
    # kappa = np.fmax(energy, kappa)
    phase_solver.solve()

    # Clip the damage solution to 0-1 ------------------------------------------
    # pnew.vector().vec().array[:] = np.clip(pnew.vector()[:], 0, 1)

    # pnew will be max(pold,pnew)-----------------------------------------------


    # Update the measurse based on current damage ------------------------------
    pold.assign(pnew)

    # update counter -----------------------------------------------------------

    cracktip_coor = get_crack_tip_coord(pnew)
    depth = 1 - cracktip_coor / H
    xdmf.write(unew, time_counter)
    xdmf.write(pnew, time_counter)
    xdmf.write(energy, time_counter)
    mprint(
        "step: {0:3}, cracktip_ratio: {1:6.3f}, time: {2:6.0f}, CDF_max: {3:6.0f} ".format(
            time_counter,
            depth,
            time.time() - start,
            energy.vector().max(),
        )
    )

    writer.writerow([time_counter,depth,cracktip_coor])
    file.flush()

    time_elapsed += delta_t
    time_counter += 1


