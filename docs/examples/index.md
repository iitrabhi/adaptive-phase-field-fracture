# Introduction to the Phase-Field Fracture Example Book

This book is a practical companion to the phase-field fracture notes and research presented on this site. While the main notes develop the theoretical, variational, and numerical foundations of phase-field fracture, this book focuses entirely on **worked examples** — executable, research-grade simulations that expose how the theory behaves in practice.

Each chapter walks through **progressively richer fracture problems**, starting from minimal phase-field setups and moving toward adaptive, large-scale, and application-driven simulations. The emphasis is on understanding modeling choices, numerical behavior, and implementation details rather than presenting polished end results.

## What You Will Learn

This book is designed to help you:

- Translate phase-field fracture theory into working numerical models  
- Develop intuition for length scales, crack regularization, and irreversibility  
- Understand solver behavior, convergence issues, and numerical stability  
- Implement phase-field fracture solvers in FEniCS and related frameworks  
- Analyze the impact of mesh resolution, adaptivity, and model parameters  
- Reproduce and extend research-level fracture simulations  

## Structure of the Book

The book is organized around increasing complexity:

1. **Minimal Phase-Field Fracture Examples**  
   One-dimensional and simple two-dimensional problems to build intuition

2. **Standard Benchmark Problems**  
   Single-edge notched specimens, tension and shear tests, validation cases

3. **Numerical Schemes and Solver Behavior**  
   Staggered vs monolithic schemes, convergence, and failure modes

4. **Adaptive and Large-Scale Examples**  
   Mesh refinement strategies, field transfer, and performance considerations

5. **Application-Driven Case Studies**  
   Glacier crevasses, structural fracture, and multi-physics extensions

Each example is **self-contained and executable**, with meshes, parameters, and scripts provided to enable direct reproduction.

## How to Use This Book

These examples are meant to be explored actively.

- Run the simulations  
- Change parameters and observe failure modes  
- Refine meshes and study crack evolution  

