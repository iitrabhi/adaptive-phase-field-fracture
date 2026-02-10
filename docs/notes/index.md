# Foundations of Phase-Field Fracture

## Notes Overview

Phase-field fracture provides a variational and computationally robust framework for modeling crack initiation, propagation, branching, and interaction without explicit crack tracking. These notes develop a rigorous yet practical foundation for building, analyzing, and scaling phase-field fracture simulations.

Rather than starting with a large codebase or a single application, the material builds the essential tools needed to understand the formulation, implement reliable solvers, and make informed modeling and numerical choices in research settings.

## Who is the intended audience?

My goal is to document what I learn and develop as I go, breaking down the formulation into intuitive steps and connecting it to my background in computational mechanics, finite elements, adaptivity, and high-performance computing.

These notes are ideal for:

- Researchers and PhD students in solid mechanics, computational mechanics, and applied mathematics  
- Developers and engineers implementing fracture models in FEM codes  
- Readers who understand PDEs and FEM and want a deep, implementation-aware view of phase-field fracture  

## Notes Structure

The notes are divided into core modules that build logically from theory to implementation and large-scale practice.

### Module 1: Variational fracture mechanics foundations
Griffith energy, regularized crack surfaces, energetic consistency, and the logic behind phase-field fracture as a variational approximation of brittle fracture.

### Module 2: Phase-field fracture models and constitutive choices
AT1 and AT2 formulations, degradation functions, tension-compression splits, irreversibility enforcement, and how modeling choices influence physical realism.

### Module 3: Weak forms and finite element discretization
Derivation of weak forms, function spaces, boundary conditions, stabilization considerations, and the mechanics of translating the formulation to FEM.

### Module 4: Solution strategies and numerical robustness
Staggered versus monolithic schemes, nonlinear solvers, convergence behavior, time stepping, and failure modes in practical simulations.

### Module 5: Adaptive mesh refinement for fracture
Error indicators, refinement strategies near evolving cracks, field transfer between meshes, and how to resolve fracture zones efficiently without brute-force meshes.

### Module 6: High-performance and parallel fracture simulation
Parallel assembly and solvers, memory bottlenecks, profiling, scalability, and practical strategies for running large-scale phase-field fracture simulations.

## What You'll Gain

- A clear understanding of the variational structure behind phase-field fracture  
- The ability to implement and debug phase-field fracture solvers in FEM frameworks such as FEniCS  
- Practical insight into numerical stability, parameter sensitivity, and solver design  
- A roadmap for adaptivity and HPC workflows suitable for research-grade problems  

## Requirements

- Strong Python proficiency and comfort with scientific computing  
- Basic continuum mechanics and variational methods  
- Familiarity with finite element discretization (weak forms, function spaces)  
- No prior fracture mechanics specialization required, but it helps  
