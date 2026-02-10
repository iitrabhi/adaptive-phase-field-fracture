export const sidebar_content = {
  "/notes/": [
    {
      text: "Introduction",
      collapsed: false,
      items: [
        {
          text: "What is Phase-Field Fracture?",
          link: "/notes/00_introduction/01_what_is_phase_field_fracture",
        },
        {
          text: "Why Phase-Field Methods for Fracture?",
          link: "/notes/00_introduction/02_why_phase_field",
        },
        {
          text: "Relation to Classical Fracture Mechanics",
          link: "/notes/00_introduction/03_classical_vs_phase_field",
        },
        {
          text: "Applications in Engineering and Geophysics",
          link: "/notes/00_introduction/04_applications",
        },
        {
          text: "Software, Data, and Reproducibility",
          link: "/notes/00_introduction/05_tools_and_reproducibility",
        },
      ],
    },
  ],

  "/examples/": [
    {
      text: "Phase-Field Fracture Examples",
      collapsed: false,
      items: [
        {
          text: "1D Brittle Fracture: A Minimal Example",
          link: "/examples/01_basics/01_1d_brittle_fracture",
        },
        {
          text: "2D Tension Test with Phase-Field Fracture",
          link: "/examples/01_basics/02_2d_tension_test",
        },
        {
          text: "Single-Edge Notched Specimen (SEN)",
          link: "/examples/02_benchmarks/01_sen_specimen",
        },
        {
          text: "Adaptive Mesh Refinement near Cracks",
          link: "/examples/03_adaptivity/01_amr_near_crack",
        },
        {
          text: "Large-Scale Fracture Simulation and Scaling",
          link: "/examples/04_hpc/01_parallel_scaling",
        },
      ],
    },
  ],
};
