# Judging rubric

Four criteria, weighted equally. Each scored 0–25. Maximum 100.

## Performance (25 pts)

| Score | Bar |
|---|---|
| 25 | Beats the baseline on both runtime and accuracy. Demonstrates scaling — at least two problem sizes. |
| 18 | Beats the baseline on runtime with comparable accuracy. One problem size. |
| 12 | Matches the baseline. Workload runs end-to-job without errors. |
| 6  | Workload runs but is slower or less accurate than the baseline. |
| 0  | Workload does not run, or no baseline provided. |

What counts as "the baseline": for DFT, PySCF on the same molecule and basis. For CFD, the NumPy LBM step. For MD, the NumPy velocity-Verlet integrator. For custom workloads, whatever reference you specify in `results.json.baseline_comparison`.

## Tradeoff reasoning (25 pts)

| Score | Bar |
|---|---|
| 25 | Picks a non-recommended option and defends the choice with measurable evidence (e.g., "I picked the GPU option because the carbon column dropped 40% with only 0.1% accuracy loss"). Shows how the frontier moves as the algorithm or problem size changes. |
| 18 | Picks the recommended option and explains why each of the four metrics matters for this workload. |
| 12 | Picks the recommended option without engaging the table. |
| 6  | Pasted the summary but did not interpret it. |
| 0  | No `preflight_log.txt` provided. |

The strongest justifications are 3–6 sentences referencing the specific numbers in the table. Hand-wavy language ("the GPU was faster") scores low.

## Creativity (25 pts)

| Score | Bar |
|---|---|
| 25 | Custom workload that is well-motivated and well-executed. Or: pre-defined track with a non-obvious algorithmic twist — preconditioning, multigrid, learned force field, basis-set extrapolation, etc. |
| 18 | Pre-defined track with a meaningful algorithmic variation beyond the starter. |
| 12 | Pre-defined track at a larger problem size than the starter. |
| 6  | Starter notebook with cosmetic changes. |
| 0  | Starter notebook unchanged. |

Originality is evaluated against the starter, not against the hackathon population. If two teams independently arrive at the same idea, both are scored on the merit of the execution.

## Robustness (25 pts)

| Score | Bar |
|---|---|
| 25 | Notebook runs top-to-bottom on a clean machine. `results.json` is valid. Code is readable. Submission template is complete. |
| 18 | Notebook runs with one minor fix (e.g., adjust a path or env var). Everything else clean. |
| 12 | Notebook runs but requires manual intervention. Some template fields missing. |
| 6  | Notebook errors mid-run. |
| 0  | Submission cannot be reproduced. |

Reproducibility is a hard floor. The judges will execute your notebook on a fresh machine with the documented env vars set. If it doesn't run, no other score matters.

## Tie-breaker

If two submissions tie within 2 points, the carbon column wins. The team whose submitted option has the lower `total_carbon_g` takes the higher rank.
