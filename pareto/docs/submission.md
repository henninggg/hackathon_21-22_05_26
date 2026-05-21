# How to submit

Submissions are pull requests against [github.com/oriqx/pareto](https://github.com/oriqx/pareto). One PR per team.

## File layout

Copy [`templates/submission/`](../templates/submission/) into a new directory named `submissions/<team-handle>/`:

```
submissions/<team-handle>/
├── README.md              # Your team, your story (1 page max)
├── results.json           # Structured submission metadata — required, schema below
├── submission.ipynb       # Your traced workload + preflight + run + analysis
├── preflight_log.txt      # Pasted output of `options.summary()` — required
└── baseline.py            # Your reference implementation for accuracy comparison
```

## `results.json` schema

```json
{
  "team": "string — team name as it should appear on the leaderboard",
  "members": ["array of names"],
  "track": "dft | cfd | md | custom",
  "workload_description": "string — one paragraph; mandatory for track=custom",
  "preflight_choice": "string — the `label` of the option you submitted",
  "justification": "string — why this point on the Pareto frontier",
  "metrics": {
    "runtime_s":           "number — wall-clock seconds end-to-job",
    "accuracy_rel_error":  "number — your |result - baseline| / |baseline|, or 0 if exact",
    "cost_usd":            "number — from preflight, for the option you ran",
    "carbon_g":            "number — from preflight, for the option you ran",
    "problem_size":        "number — atoms / grid nodes / basis functions"
  },
  "baseline_comparison": "string — describe what your baseline computes and how you compared",
  "stretch": "string (optional) — anything beyond the starter you tried"
}
```

The schema is enforced by CI lint. A PR with malformed JSON will not be reviewed until it parses.

## `preflight_log.txt`

Paste the output of `options.summary()` for the run you submitted. If you ran multiple configurations to show how the frontier moves (a strong move for Tradeoff Reasoning), include all of them, each prefixed with a one-line description:

```
=== Baseline algorithm, 64-atom box ===
+----------------+---------+------------+--------+-------------+
...

=== Improved algorithm, 64-atom box ===
+----------------+---------+------------+--------+-------------+
...

=== Improved algorithm, 256-atom box ===
+----------------+---------+------------+--------+-------------+
...
```

## `submission.ipynb` requirements

The notebook must execute top-to-bottom against the platform gateway. Required cells (use the cell headers from the template):

1. **Setup** — imports, gateway connect, hyperparameters
2. **Workload** — the traced module with `@uniqx.to_module`
3. **Preflight** — call `uniqx.preflight()` and display `options.summary()` and `options.plot()`
4. **Submit** — pick an option, call `uniqx.submit()` + `uniqx.get()`
5. **Baseline comparison** — run the reference, compute relative error
6. **Discussion** — short prose explaining your tradeoff choice

Judges run your notebook end-to-job. If it does not execute, you score zero on Robustness.

## Deadline & PR target

Your PR must be open against `main` before the deadline announced in the hackathon Slack workspace. Late PRs are accepted only if they were *opened* before the deadline — pushes after the deadline are fine.

## Multiple submissions per team

A team may open one PR. If you want to submit multiple variants, put each variant under `submissions/<team-handle>/<variant-name>/`. Judges will score the variant you nominate in the PR description; others are bonus material.
