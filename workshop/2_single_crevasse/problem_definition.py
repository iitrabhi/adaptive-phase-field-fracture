from dolfin import *
import ufl as ufl
import numpy as np
import time


class FractureProblem:
    def __init__(self, disp_problem, phase_problem, material, cdf,cdf_adaptive = None):
        self.disp_problem = disp_problem
        self.phase_problem = phase_problem
        self.cdf = cdf
        self.mat = material
        self.cdf_adaptive = cdf_adaptive


def fracture_parameters():
    prm = Parameters("problem_parameters")
    prm.add("time_start", 0.0)
    prm.add("time_total", 350.0)
    prm.add("delta_t", 1.0)
    return prm


def staggered_parameters():
    "Return default solver parameters."
    prm = Parameters("multi_staggered")
    prm.add("tolerance", 1e-5)
    prm.add("maximum_iterations", 1000)
    return prm


class FractureSolver:
    def __init__(self, problem):
        self.parameters = fracture_parameters()
        self.parameters.add(staggered_parameters())
        self.problem = problem
        self.mat = problem.mat
        self.disp_solver = LinearVariationalSolver(self.problem.disp_problem)
        self.phase_solver = LinearVariationalSolver(self.problem.phase_problem)

    def solve(self, xdmf_file=None):
        mesh = self.problem.disp_problem.u_ufl.function_space().mesh()
        FDG0 = FunctionSpace(mesh, "DG", 0)
        # TDG0 = TensorFunctionSpace(mesh, "DG", 0)
        # stress = Function(TDG0, name="stress")

        unew, pnew = self.problem.disp_problem.u_ufl, self.problem.phase_problem.u_ufl
        uold, pold = Function(unew.function_space()
                              ), Function(pnew.function_space())
        cnew, cold = self.problem.cdf, Function(self.problem.cdf.function_space())
        if self.problem.cdf_adaptive is not None:
            cold.assign(self.problem.cdf_adaptive)
        time_elapsed = self.parameters["time_start"]
        start = time.time()
        while time_elapsed <= self.parameters["time_total"]:
            min_ms_achieved = False
            ms_step = 0
            # print("-----------------Time Step----------------------")
            # START MULTI-STAGGERED ITERATIONS ---------------------------------
            while not min_ms_achieved:
                ms_step += 1
                self.disp_solver.solve()
                cnew.assign(
                    project(
                        ufl.Max(self.mat.get_crack_driving_force(unew), cold), FDG0)
                )
                self.phase_solver.solve()
                # Clip the damage solution to 0-1 ------------------------------------------
                pnew.vector().vec().array[:] = np.clip(pnew.vector()[:], 0, 1)

                err_u = sqrt(assemble((unew - uold) ** 2 * dx))
                err_phi = sqrt(assemble((pnew - pold) ** 2 * dx))
                ms_err = max(err_u, err_phi)
                # print(
                #     "err - u - {0:5.3e} -- err - phi - {1:5.3e}".format(
                #         err_u, err_phi)
                # )
                uold.assign(unew)
                pold.assign(pnew)
                cold.assign(cnew)
                # stress.assign(project(self.mat.stress(unew)))
                # ---------------------------------------------------------------------------
                if (
                    ms_err < self.parameters["multi_staggered"]["tolerance"]
                    or ms_step
                    >= self.parameters["multi_staggered"]["maximum_iterations"]
                ):
                    min_ms_achieved = True
            if xdmf_file is not None:
                xdmf_file.write(pnew, time_elapsed)
                xdmf_file.write(unew, time_elapsed)
                # xdmf_file.write(stress, time_elapsed)

            print(
                "step: {0:5}, dof: {1:9.0f}, hmin: {2:5.2f} time: {3:6.0f}".format(
                    time_elapsed,
                    mesh.num_vertices()*3,
                    mesh.hmin(),
                    time.time() - start,
                )
            )

            time_elapsed += self.parameters["delta_t"]
