# Project Context — ORIQX Hackathon (Idearum, Zurich, 21–22 May 2026)

## Our goal

We compete in the **ORIQX track**, custom use-case: **Quantum Cryptography**.

The deliverable is a hardware-agnostic implementation using the `uniqx` SDK that:
1. Starts from the baseline notebook (`pareto/examples/notebooks/quantum_cryptography.ipynb`)
2. Extends it with state-of-the-art research algorithms
3. Runs `preflight()` to get the Pareto frontier (runtime / cost / accuracy / carbon across CPU, GPU, QPU)
4. Picks and justifies the optimal hardware point

**Winning criterion:** strongest end-to-end performance through smart algorithm × hardware co-design, with clear Pareto reasoning.

---

## Baseline: what the starter notebook does

File: `pareto/examples/notebooks/quantum_cryptography.ipynb`

Three workloads, all via `uniqx.domains.optimization.crypto`:

| Workload | SDK module builder | Key ops | Hardware routing |
|---|---|---|---|
| Period finding (Shor-like) | `build_period_finding_module(N, a)` | `expv` + `matmul` (QFT) | CPU small N, GPU/QPU large N |
| Lattice analysis (SVP) | `build_lattice_module(dim, q)` | `eigs` on Gram matrix | CPU dim≤8, GPU dim≥12 |
| Discrete logarithm | `build_discrete_log_module(g, p)` | `expv` + `matmul` | GPU/QPU (same structure as Shor) |

Problem sizes tested: N ∈ {15, 21, 35, 55}, lattice dim ∈ {4, 8, 12, 16}, primes p ∈ {13, 17, 23}.

SDK imports used in baseline:
```python
from uniqx.domains.optimization.crypto import (
    build_period_finding_module,
    build_lattice_module,
    build_discrete_log_module,
    FACTORING_EXAMPLES,
)
from uniqx import parse_result
from uniqx.core.execution import connect, preflight, submit, get
```

---

## Our extension: research directions to implement

The goal is to go beyond the baseline by incorporating state-of-the-art algorithms. Candidates (pick/combine at hackathon):

### 1. Improved Shor / period finding
- **Windowed QFT** (Gidney & Ekerå 2021): reduces qubit count for large N via a windowed arithmetic approach — relevant when targeting N > 35 where QPU advantage appears
- **Approximate QFT**: trade small accuracy loss for fewer gates/lower error rate — visible in `preflight()` as lower cost with nonzero `max_error_rate`
- Vary `a` (co-prime base) and order `r` to explore the probability landscape

### 2. Lattice: beyond Gram matrix eigendecomposition
- **LLL reduction** (Lenstra-Lenstra-Lovász): classical preprocessing that shortens basis vectors before any quantum step — reduces effective problem dimension
- **BKZ-β algorithm**: block-Korkine-Zolotarev, the state-of-the-art classical SVP solver; express inner β-block eigs with `ux.eigs` for hardware dispatch
- **Quantum speedup for SVP**: Laarhoven's quantum walk speedup — O(2^{0.2653n}) vs classical O(2^{0.2972n}); implement the inner sieve step using `ux.expv`
- Scale to higher dimensions (dim = 32, 64) to show the GPU crossover moving

### 3. Elliptic Curve Discrete Log (ECDLP)
- Extend discrete log from ℤ_p to elliptic curve groups — cryptographically relevant (breaks ECDSA)
- Shor's algorithm on EC groups requires quantum point addition; express as `expv` + `matmul` in group algebra

### 4. Post-quantum baseline comparison (classical)
- Add a **CRYSTALS-Kyber / LWE** classical baseline to show what quantum algorithms are attacking
- Use `ux.linear_solve` for LWE decoding as a hardware-agnostic reference

---

## Hardware-agnostic SDK pattern

```python
import os, uniqx

uniqx.login(os.environ["UNIQX_API_KEY"],
            gateway=os.environ.get("UNIQX_GATEWAY", "api.oriqx.com:443"))
client = uniqx.connect(os.environ.get("UNIQX_GATEWAY", "api.oriqx.com:443"))

module = my_workload(params)          # @ux.trace — builds IR, does NOT run locally
options = uniqx.preflight(module, client=client)
print(options.summary())              # Pareto table: time / cost / error / carbon / hw split
choice = options.recommended          # or override
job_id = uniqx.submit(module, client=client, backend=choice["label"])
result = uniqx.get(job_id, client=client)
```

**Critical rule:** never use Python `for` loops inside `@ux.trace` for >~5 iterations — they unroll into huge IR. Use `ux.fori_loop` or `ux.scan_loop`.

---

## Key primitives (`import uniqx as ux`)

- `ux.expv(A, v, t, *, hermitian)` — matrix exponential action (core of QFT/period finding)
- `ux.matmul`, `ux.einsum`, `ux.eigs` — dense linear algebra
- `ux.linear_solve(A, b, *, hermitian, positive_definite)` — lattice/LWE solves
- `ux.fori_loop(lower, upper, body_fn, init_val)` — compiled loops (SCF, BKZ blocks)
- `ux.scan_loop` — loops that collect outputs per step
- `ux.reduce_sum/mean`, `ux.add/sub/mul/div`, `ux.sqrt/pow/abs`

Full reference: `pareto/docs/ORIQX_PRIMITIVES.md`

---

## Install

```bash
export UNIQX_API_KEY="uxk_b854f1fa05d878f6ec0d0a7d6c1f3873"
export UNIQX_GATEWAY="<host:port from organiser on the day>"

python3.11 -m venv venv && source venv/bin/activate
# use --index-url (not --extra-index-url) so pip finds the wheel
pip install --index-url "https://uniqx:${UNIQX_API_KEY}@wheels.oriqx.com/simple/" uniqx
pip install -e "pareto/[all]"
```

Credentials persist to `~/.config/uniqx/credentials.json` after first `uniqx.login()`.

**Python version:** use 3.11 — llvmlite/numba fail on 3.12.

---

## Judging (4 criteria, equal weight)

1. **Performance** — wall-clock runtime, accuracy vs baseline, scalability with problem size
2. **Tradeoff reasoning** — defend Pareto point with numbers from `preflight().summary()`
3. **Creativity** — originality of algorithm extensions (research integration)
4. **Robustness** — code quality, reproducibility

---

## Submission

Copy `pareto/templates/submission/` → `submissions/<team-handle>/`, fill:
- `results.json` — members, metrics, track = "custom" (quantum cryptography)
- `submission.ipynb` — runnable notebook extending the baseline
- `preflight_log.txt` — paste of `preflight().summary()` output

PR against the `pareto` repo before deadline.

---

## Repo layout

```
hackathon_21-22_05_26/
├── CLAUDE.md                          ← you are here
├── pareto/                            ← starter repo (plain files, no submodule)
│   ├── examples/notebooks/
│   │   └── quantum_cryptography.ipynb ← OUR BASELINE
│   ├── tracks/md|cfd|dft/             ← other tracks (not ours)
│   ├── docs/ORIQX_PRIMITIVES.md       ← full SDK primitive reference
│   └── templates/submission/
├── venv/                              ← Python 3.11 venv
└── scrape_docs.py                     ← Playwright scraper for app.oriqx.com/docs
```
