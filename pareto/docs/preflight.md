# `preflight()` — reading the Pareto table

`uniqx.preflight(module, client=client)` is the heart of this hackathon. It returns a `PreflightResult` — a list of Pareto-ranked execution options, one row per (algorithm, hardware-assignment) plan the engine considered.

## Signature

```python
options = uniqx.preflight(module, client=client)
```

Each option is a dict with the following keys:

| Key | Meaning |
|---|---|
| `label` | Strategy name, e.g. `"cpu-only"`, `"cpu+gpu"`, `"cpu+qpu"` |
| `recommended` | `True` for the engine's suggested option |
| `total_time` | Relative compute time (lower = faster) |
| `total_cost_usd` | Estimated USD cost (lower = cheaper) |
| `max_error_rate` | Worst-case error/infidelity in `[0, 1]` |
| `total_carbon_g` | CO₂-equivalent grams |
| `node_assignments` | Dict mapping IR node ID → `"cpu"` \| `"gpu"` \| `"qpu"` |
| `_idx` | Integer index for `submit(option_idx=...)` |

The result also carries:

- `options.recommended` — the option marked `recommended=True`, or the first if none
- `options.needs_gpu` / `options.needs_qpu` — whether the recommended plan assigns any node to GPU/QPU
- `options.summary()` — print a comparison table (the artifact judges read)
- `options.plot()` — grouped bar chart of the four metrics with `matplotlib`

## Reading the table

`options.summary()` returns text like:

```
+----------------+---------+------------+--------+-------------+
| Option         | Time    | Cost (USD) | Error  | Carbon (g)  |
+----------------+---------+------------+--------+-------------+
| cpu-only *     | 1240 tu | $0.0042    | 0.00%  | 3.210       |
| cpu+gpu        |  430 tu | $0.0118    | 0.00%  | 4.870       |
| cpu+gpu+qpu    |  210 tu | $0.0890    | 0.32%  | 2.140       |
+----------------+---------+------------+--------+-------------+
```

`*` marks the engine's recommendation. The four metrics map directly to two of the judging criteria:

| Metric | Maps to |
|---|---|
| `total_time` | **Performance** — wall-clock |
| `max_error_rate` | **Performance** — accuracy vs. baseline |
| `total_cost_usd` + `total_carbon_g` | **Tradeoff reasoning** — what you traded to get the speed-up |
| `node_assignments` distribution | **Tradeoff reasoning** — *why* you trusted the recommendation, or *why* you overrode it |

## Submitting a specific option

To override the recommendation:

```python
options = uniqx.preflight(module, client=client)
choice = options.by_label("cpu+gpu")          # or pick any row
job_id = uniqx.submit(
    module,
    client=client,
    preflight_job_id=options.job_id,           # reuse the analysis
    option_idx=choice["_idx"],
    runtime_inputs=inputs,
)
```

`preflight_job_id` + `option_idx` lets the gateway skip re-scoring the graph.

## What the judges read

Judges will look at three things from your `preflight()` output:

1. **The summary table itself** — pasted into `preflight_log.txt` in your submission.
2. **Which option you picked and why** — explained in the `justification` field of `results.json`.
3. **How the table moved when you changed the algorithm** — captured as multiple summaries if you want bonus points on tradeoff reasoning.

A strong submission shows two or three `summary()` outputs side by side: baseline algorithm, your algorithm, your algorithm at a larger problem size. The shape of the Pareto frontier tells the judges more than any prose.

## Caveats

- Times are reported in `tu` (time units) for the lightweight scorer and `~Ns` (seconds) for the GNN scorer. Don't mix the two when reasoning about speedups — pin to one scorer per comparison.
- The `qpu` row only appears when the engine sees a measurable advantage from quantum execution. A purely classical winning submission is fine; the hackathon does not require quantum.
