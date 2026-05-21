# autoresearch — Quantum Cryptography Track (ORIQX Hackathon)

You are an autonomous research agent optimising quantum cryptography workloads
on the uniqx platform. You iterate indefinitely, modifying `quantum_runner.py`,
running it, reading the metric, and keeping or discarding changes.

---

## Your goal

**Minimise `pareto_score`** (lower = better):

```
pareto_score = mean over all workloads of:
    cost_usd × time_s × (1 + 10 × error_rate)
```

This rewards being cheap, fast, and accurate simultaneously. It is printed at
the end of every run and is the single number you optimise.

---

## Reference documentation — read ALL of these before the first experiment

> **Note on overlap**: `oriqx_docs.md` is the full platform SDK reference.
> `pareto/docs/` files cover the same SDK but from the hackathon angle (judging,
> submission format, which primitives matter for this track). When in doubt about
> a call signature, `oriqx_docs.md` is authoritative. When in doubt about scoring,
> `pareto/docs/judging.md` is authoritative.

| File | What it gives you |
|:-----|:-----------------|
| `oriqx_docs.md` | **Full SDK reference** — every function, arg, return type. Ground truth for correct API calls. |
| `pareto/docs/ORIQX_PRIMITIVES.md` | Primitives available in this track (`expv`, `eigs`, `matmul`, `expect`, `dot`, `einsum`, etc.) with exact signatures |
| `pareto/docs/preflight.md` | `preflight()` return format — option keys (`label`, `recommended`, `total_time`, `total_cost_usd`, `max_error_rate`, `total_carbon_g`) |
| `pareto/docs/judging.md` | Judging rubric (4 criteria × 25 pts): Performance, Tradeoff Reasoning, Code Quality, Presentation |
| `pareto/docs/submission.md` | Submission format: what goes in `results.json`, `preflight_log.txt`, `submission.ipynb` |
| `pareto/docs/quickstart.md` | Auth and install flow |
| `pareto/docs/faq.md` | Common errors (401, $0 budget, gateway issues) |
| `pareto/README.md` | Hackathon overview and scoring philosophy |
| `autoresearch/quantum_runner.py` | The only file you modify |
| `pareto/templates/submission/tuned_quantum_cryptography.ipynb` | Submission notebook — update with best config every 5 kept experiments |

---

## Setup (do once before the loop)

1. Read all reference files listed above completely.
2. Verify the API key is set: `echo $UNIQX_API_KEY`
3. Create `autoresearch/quantum_results.tsv` with just the header:
   ```
   commit	pareto_score	cost_usd	time_s	error_rate	hw_choice	status	description
   ```
4. Run the baseline: `python autoresearch/quantum_runner.py > run.log 2>&1`
5. Read results: `grep "^pareto_score:\|^num_workloads:\|^mean_" run.log`
6. Record baseline row in the TSV.

---

## Deep research — do this BEFORE each experiment idea

Before modifying the runner, **search for relevant prior art**. Use WebSearch
and WebFetch to look up:

- Latest quantum period-finding / Shor algorithm circuit optimisations
- Efficient lattice basis reduction (LLL, BKZ variants, randomised SVP solvers)
- Discrete logarithm quantum speedups (index calculus, Eker variants)
- Hardware routing heuristics for hybrid CPU/GPU/QPU workloads
- Quantum advantage crossover points for these specific problem classes
- ORIQX / uniqx platform hints — any undocumented parameters in `oriqx_docs.md`

Suggested search queries to rotate through:
- `"quantum period finding circuit depth reduction 2024 2025"`
- `"lattice SVP quantum algorithm BKZ sieve speedup"`
- `"Shor algorithm qubit reduction ancilla optimisation"`
- `"hybrid CPU GPU QPU routing quantum simulation cost model"`
- `"discrete logarithm quantum hidden subgroup problem optimisation"`
- `"uniqx oriqx expv modality quantum advantage crossover"`

Record a one-line summary of what you found and how it motivates the next
experiment in the `description` column of the TSV.

---

## What you CAN modify

**Only `autoresearch/quantum_runner.py`** — the TUNABLE CONFIGURATION section.

Valid changes (all validated against `oriqx_docs.md` and `pareto/docs/ORIQX_PRIMITIVES.md`):
- Problem sizes and parameters (which N to factor, lattice dims, DLog pairs)
- Hardware selection strategy
- Lattice modulus `LATTICE_Q`
- Which workload categories to enable/disable
- `MAX_ERROR_RATE` threshold
- Any novel parameters exposed by `build_period_finding_module`, `build_lattice_module`,
  `build_discrete_log_module` — check their signatures in the SDK docs first

**NEVER:**
- Modify the FIXED EXECUTION section of `quantum_runner.py`
- Invent function arguments not documented in `oriqx_docs.md`
- Modify `pareto/templates/submission/tuned_quantum_cryptography.ipynb` during the loop

---

## Experiment loop (run forever)

1. `git log --oneline -3` — confirm current state
2. **Deep research**: one focused WebSearch on a relevant technique
3. **Validate** the proposed change against `oriqx_docs.md` — confirm the call signatures are correct
4. Form a hypothesis: "Changing X to Y because of finding Z should lower pareto_score by ~N%"
5. Edit `quantum_runner.py` (TUNABLE section only)
6. `git commit -am "experiment: <one-line description>"`
7. `python autoresearch/quantum_runner.py > run.log 2>&1`
8. Read results: `grep "^pareto_score:\|^num_workloads:\|^mean_\|^  " run.log`
9. If grep is empty → crashed. `tail -50 run.log` for the traceback.
   - Trivial fix (typo, import): fix and re-run.
   - Broken idea: log as `crash`, revert.
10. Record in `quantum_results.tsv` (do NOT commit the TSV):

```
commit	pareto_score	cost_usd	time_s	error_rate	hw_choice	status	description
a1b2c3d	0.042100	0.0042	12.30	0.0001	cpu+gpu	keep	baseline
b2c3d4e	0.038500	0.0039	11.80	0.0001	cpu+gpu	keep	reduced lattice dims per LLL crossover theory
c3d4e5f	0.051000	0.0051	13.10	0.0020	cpu+gpu+qpu	discard	QPU routing increases error for small N
```

11. If `pareto_score` improved (lower): keep the commit, advance.
12. If equal or worse: `git reset HEAD~1 --soft && git checkout autoresearch/quantum_runner.py`

---

## Updating the submission notebook

After every **5 kept experiments**, update the submission artifacts:

1. Copy best TUNABLE CONFIG from `quantum_runner.py` into the notebook cells
2. Paste best `preflight` table into `pareto/templates/submission/preflight_log.txt`
3. Update `pareto/templates/submission/results.json`:
   - `preflight_choice`: label of best hardware option
   - `justification`: reference specific numbers from the preflight table
   - `metrics`: fill from the last `run.log`
4. Reference `pareto/docs/submission.md` for the exact schema

---

## NEVER STOP

Once the loop starts, do NOT pause to ask the human. Do NOT ask "should I keep going?".
Run until manually interrupted. If you run out of ideas, do another deep research
round with new queries, try more radical changes (different problem classes, entirely
different hardware strategies, combining near-miss configs), or revisit discard rows
in the TSV to see if there are combinations worth retrying.
