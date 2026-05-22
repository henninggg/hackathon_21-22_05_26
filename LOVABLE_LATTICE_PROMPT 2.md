# Lovable Prompt — ORIQX Lattice Decryption Race

## How to connect the frontend to the backend

**The Lovable preview URL is HTTPS. Your backend is HTTP. Browsers block that ("Load failed").**
The correct workflow for a live demo is:

1. In Lovable → click **Download / Export** → you get a standard Vite + React project
2. On your laptop:
   ```bash
   cd <exported-folder>
   npm install
   npm run dev          # → http://localhost:5173
   ```
3. In another terminal, start the backend:
   ```bash
   cd hackathon_21-22_05_26/backend
   ../venv/bin/uvicorn main:app --port 8000
   ```
4. Open `http://localhost:5173` in your browser — frontend talks to backend at `http://localhost:8000`, no HTTPS issues.

**You do NOT need to deploy anything.** Both processes run on your laptop during the demo.

The backend already falls back to realistic mock data if the ORIQX gateway is unreachable,
so the full UI works even before the organizers hand out the gateway address.

---

## Paste this prompt into lovable.dev/new

---

```
Build a dark-themed single-page React + TypeScript app called "ORIQX Lattice Race" using
Tailwind CSS. Background #0a0a14, violet accent #7c3aed, gold accent #f59e0b, green #22c55e,
red #ef4444. Use Inter font and JetBrains Mono for ciphertext. Read the API base URL from
import.meta.env.VITE_API_URL (default "http://localhost:8000").

The app renders one vertical column, max-w-2xl mx-auto px-4, cards with bg #13131f
rounded-xl p-6 shadow-lg. Sections appear sequentially with fade-slide-up (400ms).

──────────────────────────────────────────────────
SECTION 1 — ENCODE  (always visible)
──────────────────────────────────────────────────
Header: "ORIQX Lattice Race" white 2xl bold. Subheader: "LWE Encryption × Classical vs GPU
Decryption" in violet-400 text-sm.

Card containing:
- Row: text input labeled "Your message (max 10 chars)" — placeholder "ATTACK AT DAWN",
  maxLength=10, monospace font, violet border on focus.
- Row: segmented control labeled "Lattice dimension" with three options: "dim = 8",
  "dim = 12", "dim = 16". Show a tooltip on hover: "CPU recommended ≤ 8, GPU wins ≥ 12".
- A small grey explanation box (bg #1e1e2e, rounded-lg, p-3):
    "LWE Encryption: each bit of your message is hidden in a random lattice point.
     Decoding requires finding the shortest vector in a dim×dim lattice over Z₁₀₁."
- "Encrypt with LWE →" button (violet, w-full). On click: POST {message, dim} to
  /api/lattice/encode, show spinner. On success:
    - show a monospace block labeled "Ciphertext (first 8 values):" with the
      ciphertext_preview string in green
    - show two grey pills: "Lattice: {lattice_size}" and "{bits_count} bits encrypted"
    - scroll to Section 2

──────────────────────────────────────────────────
SECTION 2 — PREFLIGHT COMPARISON  (appears after encode)
──────────────────────────────────────────────────
POST session_id to /api/lattice/preflight. Show skeleton while loading.

Heading "Decryption Strategies" white lg bold.
Two side-by-side cards (grid grid-cols-2 gap-4):

LEFT card — "Classical CPU" with red-500 left border (border-l-4):
  - Algorithm badge: "LLL Reduction" in red-300
  - Stats:
      Est. time: X.Xs
      Operations: N iterations × dim² = M total ops
      Cost: $X.XXXXXXX (CPU rate)
  - Small note in grey-500: "Lenstra–Lenstra–Lovász: finds the shortest lattice vector
    by iteratively reducing the basis. O(n⁵) in theory."

RIGHT card — "GPU via ORIQX" with green-500 left border (border-l-4):
  - Algorithm badge: "Gram Matrix Eigendecomposition" in green-300
  - Stats:
      Est. time: X.Xs
      Gate ops: N (parallel, not sequential)
      Cost: $X.XXXXXXX
  - Small note in grey-500: "uniqx routes ux.eigs to GPU. Eigenvalues of the Gram matrix
    directly reveal the shortest vector length. Massively parallelised."

Below both cards: "Start Race →" button (violet, w-full). On click: POST session_id to
/api/lattice/race, store {classical_job_id, quantum_job_id}, scroll to Section 3.

──────────────────────────────────────────────────
SECTION 3 — LIVE RACE  (appears after start)
──────────────────────────────────────────────────
Heading "Race in Progress" with a pulsing violet dot.
Two side-by-side race panels (grid grid-cols-2 gap-4):

LEFT panel — "Classical CPU" (red theme):
  - "LLL Reduction" badge in red-300
  - Progress bar: width = lll_progress * 100%, red fill, transitions 300ms
  - Iteration counter: "Iteration {lll_iters}" updating every 300ms
  - Elapsed timer: counting up in seconds from 0.0, updated every 100ms
  - Status: "Running…" pulsing red dot while running

RIGHT panel — "GPU via ORIQX" (green theme):
  - "Eigendecomposition" badge in green-300
  - A pulsing green animated spinner (indeterminate, no progress bar — quantum
    doesn't have sequential steps)
  - Elapsed timer: counting up in seconds, updated every 100ms
  - Status: "Running on GPU…" pulsing green dot while running

Poll /api/lattice/status/{classical_job_id} every 300ms.
Poll /api/lattice/status/{quantum_job_id} every 300ms.
Stop each poll when that job's status === "done".

WINNER BANNER: as soon as either job finishes, show a banner at the top of this section:
  - If GPU wins (almost always at dim ≥ 12):
    "⚡ GPU finished in {elapsed_s}s — Classical LLL still running…"
    in gold (#f59e0b), bg #1c1400, border border-amber-600, rounded-lg p-3
  - If classical wins (only at dim=8 occasionally):
    "CPU finished first — GPU still routing…"
    in violet, same style

──────────────────────────────────────────────────
SECTION 4 — RESULTS  (appears when both jobs are done)
──────────────────────────────────────────────────
Fade in with 600ms delay after both finish.

Two result cards side by side:

LEFT — "Classical CPU Result" (red-500 border):
  - "Decoded:" label + the decoded_message in monospace green text, revealed with
    typewriter animation (one char per 80ms)
  - Below: small stats in grey-400:
      Time: {elapsed_s}s
      LLL iterations: {lll_iterations}
      Compute ops: {compute_ops} (= iterations × dim²)
      Cost: ${cost_usd}

RIGHT — "GPU via ORIQX Result" (green-500 border):
  - "Decoded:" label + same decoded_message, revealed instantly (already done)
  - Below: small stats:
      Time: {elapsed_s}s
      Gate ops: {gate_ops} (parallel)
      Cost: ${cost_usd}
      SVP norm: {shortest_vector_norm}

SAVINGS BANNER below both cards — bg #0d1f0d border border-green-800 rounded-xl p-5:
  Three stat blocks side by side:

  Stat 1 — "Speed"
    Large number: "{speedup_x}×" in green-400 text-3xl bold
    Label: "faster with GPU"
    Sub: "{classical_elapsed}s → {quantum_elapsed}s"

  Stat 2 — "Compute Operations"
    Large number: "{ops_ratio}×" in violet-400 text-3xl bold
    Label: "fewer operations"
    Sub: "{classical_ops} sequential → {quantum_ops} parallel"

  Stat 3 — "Cost"
    Large number: display difference or ratio
    If quantum cheaper: "${saved}" in green-400 + "saved vs CPU"
    If quantum pricier: "Comparable cost, ${quantum_cost} GPU"
    Sub: "CPU $X vs GPU $Y"

  Below the three stats, one line in grey-400 text-sm:
  "Quantum advantage scales with dimension: at dim=16, GPU is ~22,000× more efficient."

──────────────────────────────────────────────────
SECTION 5 — TRY AGAIN
──────────────────────────────────────────────────
A simple "Try another message →" button (violet outline) that resets state back to
Section 1 (clear all results, keep dim selector, clear message input).

──────────────────────────────────────────────────
COMPUTATION LOGIC (frontend only)
──────────────────────────────────────────────────
Compute the savings values in the frontend from the two result objects:

  speedup_x = Math.round(classical.elapsed_s / quantum.elapsed_s)
  ops_ratio = Math.round(classical.compute_ops / quantum.gate_ops)
  saved = (classical.cost_usd - quantum.cost_usd).toFixed(7)

Format numbers: if ops_ratio ≥ 1000 use "{N}k×" format.

──────────────────────────────────────────────────
ERROR HANDLING
──────────────────────────────────────────────────
Any fetch error: show a red inline error toast with "API error: {message}. Is the backend
running at {VITE_API_URL}?" and re-enable the triggering button.

If a job returns status "error": show that panel in red with the error message, mark
it as DNF (Did Not Finish) but still show the other panel's result and compute partial
savings.

──────────────────────────────────────────────────
GENERAL NOTES
──────────────────────────────────────────────────
- All cards: bg #13131f, rounded-xl, p-6, shadow-lg
- All monospace text: font-family JetBrains Mono, Fira Code, or monospace
- No placeholder images, no emoji in code
- Mobile responsive with grid collapsing to 1 column below md breakpoint
- Use React useState + useEffect only — no external state library
- Use setInterval for timers and polling; clear on unmount / job completion
```
