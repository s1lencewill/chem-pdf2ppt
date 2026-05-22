# Chemistry Paper PPT Template Library

This document provides specific slide templates and content generation guidelines for three chemistry paper types.

## Template A: Experimental Chemistry Papers

### A1. Title Slide
- Paper title (large bold)
- English title (small muted)
- Authors & journal information
- Optional: TOC graphic as faded background

### A2. Background & Chemical Problem
- 1–2 slides
- Importance of the chemistry domain
- Challenges in the chemical transformation (selectivity / activity / stability)
- Use specific numbers (industry scale, energy consumption share, etc.)

### A3. Prior Work & Bottlenecks
- 1 slide
- Prior strategies categorized: Strategy A (pros), Strategy B (cons)
- Core bottleneck: state in one sentence
- Lead into how this work is different

### A4. Design Strategy
- 1 slide
- Strategy schematic (extracted from paper or described in text)
- 3 design points: why this system / method / condition
- One-sentence hypothesis

### A5. Synthesis / Preparation Route
- 1 slide
- Preparation flow chart (text-based or extracted figure)
- Key conditions annotated (temperature, time, precursor ratios)
- If method is simple, merge into next slide

### A6. Structure & Composition Characterization
- 1–2 slides
- XRD: phase confirmation + crystallite size
- TEM/SEM: morphology + particle size distribution
- XPS: element valence states + surface composition
- Others: BET, EPR, Raman, EXAFS (select most critical)

### A7. Morphology & Microstructure
- 1 slide (may merge with A6)
- HRTEM: lattice fringes + FFT
- HAADF-STEM + EDS mapping (if single-atom/alloy)
- AC-HAADF-STEM (if applicable)

### A8. Performance Evaluation
- 1–2 slides
- Core data: conversion, selectivity, FE, yield, TOF, stability
- Performance comparison table (vs. literature benchmarks)
- Condition optimization (temperature/pH/potential/time dependence)

### A9. Key Control Experiments
- 1 slide
- Control catalyst/condition results
- Evidence proving active site or reaction pathway
- Ruling out alternatives

### A10. Mechanistic Investigation
- 1–2 slides
- In-situ characterization (in-situ FTIR/Raman/XAS/EPR)
- Kinetic experiments (reaction order, apparent activation energy)
- Poisoning experiments or radical trapping
- Isotope labeling

### A11. Structure-Activity / Active Site Discussion
- 1 slide
- Correlation of active site structure with performance
- Theoretical support (if DFT available)
- Why this structure/composition is better

### A12. Summary & Outlook
- 1 slide
- 3–4 core innovations
- 1–2 future directions
- Synthesize "what was learned" rather than repeating results

---

## Template B: Theoretical/Computational Chemistry Papers

### B1. Title Slide
- Same as Template A

### B2. Background & Need for Computation
- 1 slide
- Why computation is needed for this chemistry problem
- Limitations of experimental approaches (cannot observe intermediates/TS in situ, etc.)

### B3. Prior Computational Studies
- 1 slide
- What methods/models were used, what conclusions were drawn
- Problems with prior calculations: oversimplified model, insufficient method accuracy, neglected XX effects

### B4. Computational Methods & Models
- 1–2 slides (this is the core of a computational paper)
- Software package and version (VASP 6.x / Gaussian 16 / CP2K, etc.)
- Functional and basis set (or pseudopotential, cutoff energy)
- Model system: slab size, k-point sampling, vacuum thickness
- Key settings: van der Waals correction (DFT-D3), solvation model (VASPsol/implicit), Hubbard U
- Free energy methods: harmonic TS, NEB, CI-NEB, dimer method
- AIMD parameters (if applicable)

### B5. Method Validation / Benchmarking
- 1 slide
- Comparison with experimental values or high-level calculations (CCSD(T), etc.)
- Functional/basis set comparison
- Convergence tests (k-point, cutoff energy)

### B6. Key Intermediate / Transition State Structures
- 1–2 slides
- Optimized adsorption structures (from paper)
- Key bond lengths, adsorption energies
- Bader charge / charge density difference

### B7. Energy Profiles / Free Energy Diagrams
- 1 slide (core evidence)
- Full reaction pathway free energy diagram
- Label RDS and barrier values
- Energy comparison of competing pathways

### B8. Electronic Structure Analysis
- 1 slide
- PDOS / d-band center analysis
- Charge density difference
- COHP/COOP bonding analysis
- ELF or differential charge

### B9. Selectivity Analysis
- 1 slide
- Energy differences between competing pathways
- Selectivity-determining step analysis
- Descriptor analysis (ΔG*O − ΔG*OH, etc.)

### B10. Microkinetics / Volcano Plot (if applicable)
- 1 slide
- Microkinetic model results (comparison with experimental rates)
- Volcano activity trends
- Screening / predicting new catalysts

### B11. Comparison with Experiment (if applicable)
- 1 slide
- Table comparing computed vs. experimental values
- Explaining agreement or discrepancies

### B12. Summary & Outlook
- 1 slide
- New theoretical understanding gained
- Design principles for experiment
- Computational method limitations

---

## Template C: Experimental + Theoretical Hybrid Papers

### C1. Title Slide
- Same as Template A

### C2. Background
- 1 slide

### C3. Research Strategy (Experimental + Computational Joint)
- 1 slide
- Flow chart: what experiment does → what computation does → how they cross-validate
- Core logic of the joint strategy

### C4–C6. Experimental Section
- 3 slides
- Synthesis + characterization + performance (reference Template A, condensed to essentials)

### C7–C9. Computational Section
- 3 slides
- Methods + models + key results (reference Template B, condensed to essentials)

### C10. Experiment-Theory Cross-Validation
- 1–2 slides (core value slide of hybrid papers)
- Comparison table: experimental vs. computed values
- How computation explains experimental observations
- How experiment validates computational predictions

### C11. Unified Mechanism Model
- 1 slide
- Complete reaction mechanism synthesized from experimental + computational evidence
- Use original figure or text-based mechanism schematic

### C12. Summary & Outlook
- 1 slide

---

## General Content Writing Guidelines

### Bullet Point Writing

**Poor** (vague, no information):
- The catalyst shows good activity

**Good** (has data, comparison, explanation):
- Ru₁/Cu achieves FE(C₂₊) of 82%, 1.8× that of pure Cu NPs (45%)

### Conclusion-Style Title Writing

**Poor** (label-style):
- XRD Characterization
- Catalytic Performance
- Reaction Mechanism

**Good** (conclusion-style):
- XRD Confirms Ru Doped as Single Atoms into CuO Lattice
- Ru₁/CuO Achieves 82% C₂₊ Faradaic Efficiency at −0.9 V vs RHE
- Operando XAS + DFT Reveal Ru Sites Promote *CO Enrichment and C-C Coupling

### Chemical Naming Conventions

- Full compound name at first occurrence, abbreviation thereafter (e.g., "metal-organic framework (MOF)")
- Catalyst naming: active component / support (e.g., "Ru₁/CuO", "Pt/N-C")
- Catalytic conditions fully specified: temperature, pressure, space velocity, electrolyte concentration
- Energy data with reference points: eV vs SHE, kcal/mol, kJ/mol

### Data Presentation

- Catalytic performance must include at minimum: conversion + selectivity + stability
- Comparison data must note whether test conditions are consistent
- Computational data must note functional / basis set level
- Use tables rather than text walls for multi-group comparison data
