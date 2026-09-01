These are the mesh files that are required with crack width 5 and depth in both direction 10m
a. $500\times750\times125$ m
	1. Single crack on one face - non-adaptive
	2. Single crack on one face - adaptive
	3. Two cracks on opposite face - non-adpative - 15 spacing
	4. Two cracks on opposite face - non-adpative - 25 spacing
	5. Two cracks on opposite face - non-adpative - 50 spacing
	6. Two cracks on opposite face - non-adpative - 100 spacing
	7. Five cracks on one face - non-adaptive - 50m
	8. Five cracks on one face - non-adaptive - 70m
	9. Ten cracks on two face - non-adaptive - 70m
	10. Single crack on one face - non-adaptive- 4473396 nodes
	 
b. $1500\times750\times125$ m 
	1. 30 cracks on two faces.

So, we need 11 meshes to run all the studies.

| ID  | Mesh File Name           | Domain (m)       | Description                                              | Spacing (m) |     Nodes |
| --- | ------------------------ | ---------------- | -------------------------------------------------------- | ----------: | --------: |
| A1  | `01/Lx500_1C_NA.xdmf`    | 500 × 750 × 125  | Single crack, non-adaptive                               |           — |         — |
| A2  | `02/Lx500_1C_AD.xdmf`    | 500 × 750 × 125  | Single crack, adaptive                                   |           — |         — |
| A3  | `03/Lx500_2C_S15.xdmf`   | 500 × 750 × 125  | 2 cracks                                                 |          15 |         — |
| A4  | `04/Lx500_2C_S25.xdmf`   | 500 × 750 × 125  | 2 cracks                                                 |          25 |         — |
| A5  | `05/Lx500_2C_S50.xdmf`   | 500 × 750 × 125  | 2 cracks                                                 |          50 |         — |
| A6  | `06/Lx500_2C_S100.xdmf`  | 500 × 750 × 125  | 2 cracks                                                 |         100 |         — |
| A7  | `07/Lx500_5C_S50.xdmf`   | 500 × 750 × 125  | 5 cracks                                                 |          50 |         — |
| A8  | `08/Lx500_5C_S70.xdmf`   | 500 × 750 × 125  | 5 cracks                                                 |          70 |         — |
| A9  | `09/Lx500_10C_S70.xdmf`  | 500 × 750 × 125  | 10 cracks, opposing crevasse fields                      |          70 |         — |
| A10 | `10/Lx500_1C_NA_4M.xdmf` | 500 × 750 × 125  | Single crack, large non-adaptive mesh for parallel study |           — | 4,473,396 |
| B1  | `11/Lx1500_30C.xdmf`     | 1500 × 750 × 125 | Kilometer-scale, 30 cracks                               |           — |         — |

---

| Run No. | Section | Mesh ID | Mesh File                | Simulation Description                                                                                                                                                                                           |
| ------: | :-----: | :-----: | ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|      01 |   4.1   |   01    | `01/Lx500_1C_NA.xdmf`    | Single-crevasse non-adaptive reference simulation with hw=0h_w=0. Used to establish the dry reference crack depth and computational response.                                                                    |
|      02 |   4.1   |   01    | `01/Lx500_1C_NA.xdmf`    | Single-crevasse non-adaptive reference simulation with hw=0.25Hh_w=0.25H. Used to quantify the effect of partial ocean pressure on crevasse depth.                                                               |
|      03 |   4.1   |   01    | `01/Lx500_1C_NA.xdmf`    | Single-crevasse non-adaptive reference simulation with hw=0.5Hh_w=0.5H. Used as the high-water reference case.                                                                                                   |
|      04 |   4.1   |   02    | `02/Lx500_1C_AD.xdmf`    | Single-crevasse adaptive simulation with hw=0h_w=0. Used to compare adaptive accuracy and computational cost against Run 01.                                                                                     |
|      05 |   4.1   |   02    | `02/Lx500_1C_AD.xdmf`    | Single-crevasse adaptive simulation with hw=0.25Hh_w=0.25H. Used to compare adaptive accuracy and efficiency against Run 02.                                                                                     |
|      06 |   4.1   |   02    | `02/Lx500_1C_AD.xdmf`    | Single-crevasse adaptive simulation with hw=0.5Hh_w=0.5H. Used to compare adaptive accuracy and efficiency against Run 03.                                                                                       |
|      07 |   4.2   |   02    | `02/Lx500_1C_AD.xdmf`    | Single-crevasse adaptive length-scale study with ℓ=5\ell=5 m. Used to examine the effect of finer fracture regularization on crack depth and computational cost.                                                 |
|      08 |   4.2   |   02    | `02/Lx500_1C_AD.xdmf`    | Single-crevasse adaptive length-scale study with ℓ=10\ell=10 m. Baseline case for the length-scale sensitivity comparison.                                                                                       |
|      09 |   4.2   |   02    | `02/Lx500_1C_AD.xdmf`    | Single-crevasse adaptive length-scale study with ℓ=20\ell=20 m. Used to examine the effect of a larger regularization length scale on crack depth and computational cost.                                        |
|      10 |   4.3   |   03    | `03/Lx500_2C_S15.xdmf`   | Two-crevasse interaction simulation with S=15S=15 m. Used to study strong crack interaction and coalescence.                                                                                                     |
|      11 |   4.3   |   04    | `04/Lx500_2C_S25.xdmf`   | Two-crevasse interaction simulation with S=25S=25 m. Used to study crack curving and interaction without coalescence.                                                                                            |
|      12 |   4.3   |   05    | `05/Lx500_2C_S50.xdmf`   | Two-crevasse interaction simulation with S=50S=50 m. Used to study crack-tip interaction and shielding.                                                                                                          |
|      13 |   4.3   |   06    | `06/Lx500_2C_S100.xdmf`  | Two-crevasse interaction simulation with S=100S=100 m. Used to examine approximately independent propagation at large spacing.                                                                                   |
|      14 |   4.4   |   07    | `07/Lx500_5C_S50.xdmf`   | Five-crevasse competitive-growth simulation with S=50S=50 m. Used to identify dominant cracks and cracks arrested by stress shielding.                                                                           |
|      15 |   4.4   |   08    | `08/Lx500_5C_S70.xdmf`   | Five-crevasse competitive-growth simulation with S=70S=70 m. Used to examine how increased spacing changes which crevasses propagate.                                                                            |
|      16 |   4.4   |   09    | `09/Lx500_10C_S70.xdmf`  | Ten-crevasse simulation with opposing crevasse fields and S=70S=70 m. Used to study competitive growth and coalescence between cracks from opposite sides.                                                       |
|      17 |   4.5   |   10    | `10/Lx500_1C_NA_4M.xdmf` | Strong-scaling run using 1 MPI process. One RAMR cycle is used as the serial timing reference.                                                                                                                   |
|      18 |   4.5   |   10    | `10/Lx500_1C_NA_4M.xdmf` | Strong-scaling run using 2 MPI processes. Used to measure parallel speedup relative to Run 17.                                                                                                                   |
|      19 |   4.5   |   10    | `10/Lx500_1C_NA_4M.xdmf` | Strong-scaling run using 4 MPI processes. Used to evaluate scaling of the solver and RAMR operations.                                                                                                            |
|      20 |   4.5   |   10    | `10/Lx500_1C_NA_4M.xdmf` | Strong-scaling run using 8 MPI processes. Used to quantify continued reduction in total runtime.                                                                                                                 |
|      21 |   4.5   |   10    | `10/Lx500_1C_NA_4M.xdmf` | Strong-scaling run using 16 MPI processes. Used to identify the process count near minimum total runtime.                                                                                                        |
|      22 |   4.5   |   10    | `10/Lx500_1C_NA_4M.xdmf` | Strong-scaling run using 32 MPI processes. Used to quantify the increasing cost of parallel mesh refinement.                                                                                                     |
|      23 |   4.5   |   11    | `11/Lx1500_30C.xdmf`     | Kilometer-scale 30-crevasse simulation with the standard slip-boundary configuration. Used to demonstrate large-scale adaptive simulation of an interacting crevasse field.                                      |
|      24 |   4.6   |   11    | `11/Lx1500_30C.xdmf`     | Kilometer-scale 30-crevasse simulation with one lateral boundary fixed. Run until a converged fracture configuration is obtained under the fixed-boundary state.                                                 |
|      25 |   4.6   |   11    | `11/Lx1500_30C.xdmf`     | Restart of Run 24 from its final converged state. The previously fixed lateral boundary is released and the simulation is continued to study the resulting stress redistribution and additional crevasse growth. |
