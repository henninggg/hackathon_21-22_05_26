# Lovable Prompt — ORIQX Quantum Cracker UI

Paste the block below verbatim at **lovable.dev/new** to generate the React frontend.
Set the env var `VITE_API_URL=http://localhost:8000` in Lovable's project settings
(or your deployed backend URL).

---

```
Build a dark-themed single-page React + TypeScript app called "ORIQX Quantum Cracker"
using Tailwind CSS and Recharts. The background is #0a0a14. Primary accent is #7c3aed (violet).
Gold accent #f59e0b for the recommended row. Use Inter font.

Read all API responses from the base URL stored in import.meta.env.VITE_API_URL
(default "http://localhost:8000").

The page has one column of four sections that appear sequentially:

──────────────────────────────────────────────────
SECTION 1 — SETUP  (always visible)
──────────────────────────────────────────────────
- Title row: "ORIQX Quantum Cracker" in white 2xl bold, subtitle "Shor's Algorithm × Hardware Co-design" in violet-400 text-sm
- A card (bg #13131f, rounded-xl, p-6) containing:
  - Label: "RSA Modulus N" with a <select> showing options 15, 21, 35, 55
  - Below the select, a monospace box labelled "Intercepted ciphertext" showing the ciphertext
    string returned by POST /api/preflight (fetch it whenever N changes; show a skeleton loader while fetching)
  - Small grey note: "Encrypted with an unknown factor of N using Caesar cipher"
  - A violet "Run Preflight →" button (w-full, disabled while loading)

──────────────────────────────────────────────────
SECTION 2 — HARDWARE PARETO TABLE  (appears after preflight)
──────────────────────────────────────────────────
Animate in with a fade-slide-up (duration 400ms).
- Section heading "Pareto Frontier" in white lg font
- A table with columns: Hardware | Est. Time | Cost (USD) | Error Rate | Carbon (gCO₂)
  - Data comes from the `options` array in the preflight response
  - The row where `recommended === true` gets a gold left border (border-l-4 border-amber-400)
    and a gold "★ Recommended" badge
  - All other rows have a violet left border
  - Format est_time_s as "X.Xs", cost_usd as "$0.00000", carbon_g as "X.Xg" (show "—" if null)
- Below the table: a "Launch Quantum Attack →" button (bg violet, w-full)
  Clicking it POSTs to /api/submit with { N, backend_label } where backend_label is the
  recommended option's label. Store the returned job_id and started_at.

──────────────────────────────────────────────────
SECTION 3 — LIVE COMPUTATION  (appears after submit)
──────────────────────────────────────────────────
Animate in with fade-slide-up.
- A hardware badge pill at top right: "Running on: CPU" / "CPU + GPU" / "CPU + GPU + QPU"
  in violet-200 text with a pulsing violet dot

- Progress bar: label "Elapsed / Estimated"
  - Show elapsed seconds counted up from started_at (update every 100ms)
  - Bar width = min(elapsed / est_time_s, 1) * 100%
  - Violet fill, transitions smoothly
  - Below bar: "X.Xs / Y.Ys"

- Cost ticker: "Running cost: $0.000000"
  - Increment linearly from 0 toward est cost_usd over est_time_s seconds, update every 100ms

- QFT Probability Distribution chart:
  - Use Recharts BarChart, dark background, violet bars, no x-axis labels
  - On mount, animate the bars building up over 2.5 seconds:
    - Compute the theoretical QFT distribution for the selected N using this formula:
      bins = 64 values from 0 to 63
      For period r (use KNOWN_PERIODS: {15:4, 21:6, 35:12, 55:20}):
        probability[k] = sum_{j=0}^{r-1} cos(2π * j * k / 64)² / r²  (simplified QFT peaks)
      Normalize so max = 1.
    - Animate: each 50ms frame, reveal bars up to the current time fraction * 64
    - After job completes, tint the peak bars gold and add label "Confirmed by QPU"
  - X-axis label: "QFT Output Register (64 bins)"  Y-axis: "Probability"

──────────────────────────────────────────────────
SECTION 4 — RESULT  (appears when job status === "done")
──────────────────────────────────────────────────
Animate in with fade-slide-up.
- A green-bordered card (border border-green-500) with:
  - "✓ Encryption Cracked" heading in green-400 text-2xl
  - "Period found: r = X" in white
  - "Factors: N = p × q" in violet-300 (e.g. "35 = 5 × 7")
  - A divider, then two monospace rows:
      Ciphertext:  [ciphertext string]
      Plaintext:   [plaintext string revealed via typewriter animation, one char per 120ms]
  - The cipher key shown as: "Caesar key = p (one factor of N)"
- A summary card below with three stats in a 3-col grid:
    Actual time | Cost | Hardware
  Values in violet-200, labels in grey-400

──────────────────────────────────────────────────
POLLING
──────────────────────────────────────────────────
While status !== "done", poll GET /api/status/{job_id} every 500ms.
Stop polling when status === "done", then trigger Section 4 to appear.

──────────────────────────────────────────────────
GENERAL NOTES
──────────────────────────────────────────────────
- All cards use bg #13131f, rounded-xl, p-6, shadow-lg
- Use React useState + useEffect (no external state library needed)
- Handle fetch errors gracefully: show a red inline error message, re-enable the button
- Mobile-responsive: max-w-2xl mx-auto px-4
- No placeholder images. No emoji in code. Clean monospace font (JetBrains Mono or Fira Code)
  for ciphertext/plaintext display.
```
