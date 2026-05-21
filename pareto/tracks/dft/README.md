# Track: DFT

Compute the SCF ground-state energy and NMR shieldings for a small molecule. The platform decides where each block of the graph runs; you decide the algorithm, the basis, and the molecule.

## What ships

- [`starter.ipynb`](starter.ipynb) — H₂O at STO-3G, full preflight → submit → compare-to-PySCF workflow.
- [`baseline.py`](baseline.py) — PySCF RHF reference for accuracy comparison.

## SDK surface

```python
from uniqx.domains.chemistry.basis import extract_basis
from uniqx.domains.chemistry.hartree_fock import rhf_module
from uniqx.domains.chemistry.nmr_full import nmr_full_module, scf_module
```

`scf_module(geometry, basis_info, max_iter=N)` returns a traced iterative SCF; `rhf_module` returns the closed-form analytic module. `nmr_full_module` returns SCF energy plus isotropic shieldings plus Fermi-contact J-couplings.

All four take the same six runtime inputs derived from `basis_info`:

```python
runtime_inputs = [
    list(info.exps_flat),
    list(info.coeffs_flat),
    list(info.centers_flat),
    list(info.ang_flat),
    list(info.atom_coords_flat),
    list(info.charges_flat),
]
```

## Where to push beyond the starter

| Direction | What changes |
|---|---|
| Bigger basis (6-31G, cc-pVDZ) | Cost column climbs; accuracy improves; graph fans out |
| Bigger molecule (methane → methanol → alanine) | Gateway splits the graph into more execution blocks |
| Geometry optimization | Wraps SCF in an outer minimization loop |
| Tighten `max_iter` / convergence | Trades accuracy for runtime — read the `max_error_rate` column |

## Reference behaviour

H₂O at STO-3G: RHF total energy ≈ −74.96 Ha (PySCF reference). The starter checks within 5 mHa.

H₂ at STO-3G: RHF total energy ≈ −1.117 Ha — used by the SDK's own validation script.
