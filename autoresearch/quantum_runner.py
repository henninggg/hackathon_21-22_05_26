"""
quantum_runner.py — tunable quantum cryptography experiment for uniqx.

This is the ONLY file the agent edits (the TUNABLE CONFIGURATION section).
Run it as:   python autoresearch/quantum_runner.py > run.log 2>&1

Before modifying this file, always validate API calls against:
  - oriqx_docs.md           (full SDK reference — correct call signatures)
  - pareto/docs/preflight.md (preflight / submission flow)
  - pareto/docs/ORIQX_PRIMITIVES.md (available primitives: expv, eigs, matmul, expect)

Metric: pareto_score (lower is better)
  pareto_score = mean over workloads of (cost_usd * time_s * (1 + 10 * error_rate))
"""

import os
import time

from uniqx import login
from uniqx.core.execution import connect, preflight, submit, get
from uniqx.domains.optimization.crypto import (
    build_period_finding_module,
    build_lattice_module,
    build_discrete_log_module,
    FACTORING_EXAMPLES,
)

# ============================================================
# TUNABLE CONFIGURATION — agent modifies this section only
# ============================================================

# Factoring: which N values to factor (must exist in FACTORING_EXAMPLES)
PERIOD_FINDING_Ns = [15, 21, 35]

# Lattice: dimensions to analyse (Gram matrix is dim × dim)
LATTICE_DIMS = [4, 8, 12, 16]

# Lattice modulus (prime; higher = denser integer lattice)
LATTICE_Q = 101

# Discrete log: (g, p) pairs — p must be prime
DLOG_PARAMS = [(2, 13), (3, 17), (2, 23)]

# Hardware selection strategy for each workload:
#   "recommended" — use the platform's recommended option
#   "cheapest"    — minimise cost_usd
#   "fastest"     — minimise total_time
#   "lowest_err"  — minimise max_error_rate
HARDWARE_STRATEGY = "recommended"

# Maximum acceptable error rate (options above this are skipped when picking)
MAX_ERROR_RATE = 0.05

# Enable / disable workload categories
RUN_PERIOD_FINDING = True
RUN_LATTICE = True
RUN_DLOG = True

# ============================================================
# FIXED EXECUTION — do not modify below this line
# ============================================================

GATEWAY = os.environ.get("UNIQX_GATEWAY", "api.oriqx.com:443")
login(os.environ.get("UNIQX_API_KEY", ""), gateway=GATEWAY)
client = connect(GATEWAY)


def pick_option(options, strategy, max_err):
    candidates = [o for o in options if o.get("max_error_rate", 1.0) <= max_err]
    if not candidates:
        candidates = options
    if strategy == "recommended":
        rec = [o for o in candidates if o.get("recommended")]
        return rec[0] if rec else candidates[0]
    if strategy == "cheapest":
        return min(candidates, key=lambda o: o["total_cost_usd"])
    if strategy == "fastest":
        return min(candidates, key=lambda o: o["total_time"])
    if strategy == "lowest_err":
        return min(candidates, key=lambda o: o.get("max_error_rate", 1.0))
    return candidates[0]


def run_workload(mod, inputs):
    opts = preflight(mod, client=client)
    all_opts = list(opts)
    opt = pick_option(all_opts, HARDWARE_STRATEGY, MAX_ERROR_RATE)
    t0 = time.monotonic()
    jid = submit(
        mod,
        client=client,
        runtime_inputs=inputs,
        preflight_job_id=opts.job_id,
        option_idx=opt["_idx"],
    )
    try:
        get(jid, client=client)
    except Exception as e:
        print(f"  WARNING: job {jid} failed: {e} — using preflight estimates only")
    wall = time.monotonic() - t0
    return opt, wall, all_opts


scores = []
rows = []
total_cost = 0.0
total_time_sum = 0.0
total_err = 0.0

if RUN_PERIOD_FINDING:
    for N in PERIOD_FINDING_Ns:
        if N not in FACTORING_EXAMPLES:
            print(f"WARNING: N={N} not in FACTORING_EXAMPLES, skipping")
            continue
        info = FACTORING_EXAMPLES[N]
        mod, inputs, meta = build_period_finding_module(N=N, a=info["a"])
        opt, wall, _ = run_workload(mod, inputs)
        s = opt["total_cost_usd"] * opt["total_time"] * (1 + 10 * opt["max_error_rate"])
        scores.append(s)
        total_cost += opt["total_cost_usd"]
        total_time_sum += opt["total_time"]
        total_err += opt["max_error_rate"]
        rows.append(
            f"period_finding N={N:>2} dim={meta['dim']:>4}  hw={opt['label']:<16}"
            f"time={opt['total_time']:>8.1f}  cost=${opt['total_cost_usd']:.4f}"
            f"  err={opt['max_error_rate']:.4f}  score={s:.6f}"
        )

if RUN_LATTICE:
    for dim in LATTICE_DIMS:
        mod, inputs, meta = build_lattice_module(dim=dim, q=LATTICE_Q)
        opt, wall, _ = run_workload(mod, inputs)
        s = opt["total_cost_usd"] * opt["total_time"] * (1 + 10 * opt["max_error_rate"])
        scores.append(s)
        total_cost += opt["total_cost_usd"]
        total_time_sum += opt["total_time"]
        total_err += opt["max_error_rate"]
        rows.append(
            f"lattice       dim={dim:>4}        hw={opt['label']:<16}"
            f"time={opt['total_time']:>8.1f}  cost=${opt['total_cost_usd']:.4f}"
            f"  err={opt['max_error_rate']:.4f}  score={s:.6f}"
        )

if RUN_DLOG:
    for g, p in DLOG_PARAMS:
        mod, inputs, meta = build_discrete_log_module(g=g, p=p)
        opt, wall, _ = run_workload(mod, inputs)
        s = opt["total_cost_usd"] * opt["total_time"] * (1 + 10 * opt["max_error_rate"])
        scores.append(s)
        total_cost += opt["total_cost_usd"]
        total_time_sum += opt["total_time"]
        total_err += opt["max_error_rate"]
        rows.append(
            f"discrete_log  g={g} p={p:>2}        hw={opt['label']:<16}"
            f"time={opt['total_time']:>8.1f}  cost=${opt['total_cost_usd']:.4f}"
            f"  err={opt['max_error_rate']:.4f}  score={s:.6f}"
        )

n = len(scores)
pareto_score = sum(scores) / n if n else float("inf")

print("---")
print(f"pareto_score:     {pareto_score:.6f}")
print(f"num_workloads:    {n}")
print(f"mean_cost_usd:    {total_cost / n:.6f}")
print(f"mean_time_s:      {total_time_sum / n:.2f}")
print(f"mean_error_rate:  {total_err / n:.6f}")
for row in rows:
    print(f"  {row}")
