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

|ID|Mesh File Name|Domain (m)|Description|Spacing (m)|Nodes|
|---|---|---|---|--:|--:|
|A1|`Lx500_1C_NA.msh`|500 × 750 × 125|Single crack, non-adaptive|—|—|
|A2|`Lx500_1C_AD.msh`|500 × 750 × 125|Single crack, adaptive|—|—|
|A3|`Lx500_2C_S15.msh`|500 × 750 × 125|2 cracks, non-adaptive|15|—|
|A4|`Lx500_2C_S25.msh`|500 × 750 × 125|2 cracks, non-adaptive|25|—|
|A5|`Lx500_2C_S50.msh`|500 × 750 × 125|2 cracks, non-adaptive|50|—|
|A6|`Lx500_2C_S100.msh`|500 × 750 × 125|2 cracks, non-adaptive|100|—|
|A7|`Lx500_5C_S50.msh`|500 × 750 × 125|5 cracks, non-adaptive|50|—|
|A8|`Lx500_5C_S70.msh`|500 × 750 × 125|5 cracks, non-adaptive|70|—|
|A9|`Lx500_10C_S70.msh`|500 × 750 × 125|10 cracks, non-adaptive|70|—|
|A10|`Lx500_1C_NA_4M.msh`|500 × 750 × 125|Single crack, non-adaptive|—|4,473,396|
|B1|`Lx1500_30C.msh`|1500 × 750 × 125|30 cracks|—|—|