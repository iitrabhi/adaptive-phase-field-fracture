---
layout: home

hero:
  name: Phase-field fracture notes and research
  text:
  tagline: These notes document my understanding and ongoing work on phase-field fracture methods, with emphasis on large-scale simulations, adaptive mesh refinement, and high-performance computing. The content blends theory, numerical formulation, implementation details, and lessons learned from real research problems such as glacier crevasse growth and multi-physics fracture.
  actions:
    - theme: brand
      text: Start reading
      link: /notes/
    - theme: alt
      text: GitHub
      link: https://github.com/iitrabhi

features:
  - title: Variational fracture mechanics
    icon: ⊙
    details: Learn the energetic foundations of phase-field fracture. We derive the governing equations from variational principles, interpret the length-scale parameter, and connect the formulation to Griffith fracture and regularized crack representations.
    link: /notes/01_variational_fracture/01_energy_formulation

  - title: Phase-field formulation and models
    icon: ◈
    details: Explore common phase-field fracture models, including AT1 and AT2 formulations. Understand crack irreversibility, history variables, degradation functions, and how modeling choices influence physical realism and numerical robustness.
    link: /notes/02_phase_field_models/01_at_models

  - title: Numerical implementation in FEniCS
    icon: ▲
    details: Step-by-step construction of a working phase-field fracture solver in FEniCS. Topics include weak forms, staggered versus monolithic schemes, function spaces, constraint handling, and convergence behavior.
    link: /notes/03_implementation/01_weak_form

  - title: Adaptive mesh refinement for fracture
    icon: ⌂
    details: Adaptive refinement is essential for resolving narrow fracture zones efficiently. Learn refinement indicators, mesh transfer strategies, and how to evolve fracture paths without mesh coarsening, as used in the SPICE framework.
    link: /notes/04_adaptivity/01_why_amr

  - title: High-performance and parallel computing
    icon: ⎈
    details: Scale phase-field fracture simulations to large problem sizes. Topics include parallel assembly, solver choices, memory bottlenecks, profiling, and practical strategies for running simulations with tens to hundreds of millions of degrees of freedom.
    link: /notes/05_hpc/01_parallel_scaling

  - title: Applications and reproducibility
    icon: ❖
    details: Case studies from glacier surface crevasse growth, structural fracture, and multi-physics problems. Emphasis on reproducibility, mesh and data management, and how numerical choices affect scientific conclusions.
    link: /notes/06_applications/01_glaciers

---
