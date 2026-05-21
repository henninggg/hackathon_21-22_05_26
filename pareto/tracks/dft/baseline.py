# Copyright (c) 2026 ORIQX AG. MIT licensed.
"""PySCF reference for DFT track accuracy comparison.

Install: `pip install -e ".[dft]"` from the repo root.
"""

from __future__ import annotations


def rhf_reference(geometry: list[tuple[str, list[float]]], basis: str = "sto-3g") -> float:
    """Run a PySCF RHF calculation and return the total energy in Hartree."""
    from pyscf import gto, scf

    atom_str = "\n".join(f"{sym} {x} {y} {z}" for sym, (x, y, z) in geometry)
    mol = gto.M(atom=atom_str, basis=basis, unit="Angstrom", verbose=0)
    mf = scf.RHF(mol)
    return float(mf.kernel())


def nmr_shieldings_reference(
    geometry: list[tuple[str, list[float]]], basis: str = "sto-3g"
) -> list[float]:
    """PySCF NMR isotropic shielding tensors (ppm) for each atom."""
    from pyscf import gto, scf
    from pyscf.prop import nmr

    atom_str = "\n".join(f"{sym} {x} {y} {z}" for sym, (x, y, z) in geometry)
    mol = gto.M(atom=atom_str, basis=basis, unit="Angstrom", verbose=0)
    mf = scf.RHF(mol).run()
    sigma = nmr.RHF(mf).kernel()
    return [float(s.trace() / 3.0) for s in sigma]


if __name__ == "__main__":
    H2O = [
        ("O", [0.0, 0.0, 0.1173]),
        ("H", [0.0, 0.7572, -0.4692]),
        ("H", [0.0, -0.7572, -0.4692]),
    ]
    energy = rhf_reference(H2O, "sto-3g")
    print(f"H2O RHF/STO-3G energy: {energy:.6f} Ha")
