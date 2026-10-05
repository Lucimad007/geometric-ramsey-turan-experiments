# Methodology

## What a run is

An experiment supplies an explicit finite pair of point sets and the parameters `(p, ℓ, μ, K)`, applies the edge rules B1 and B2 from Section 3.1 of the paper, and writes the resulting graph. The file is a record of that graph. The field `guarantees` is always the string `none; finite sample`.

Edge density, cross density, and degree statistics are counts on that graph. They are not estimates of `ϱ_p(q)`, and they are not the cross density `ℓ/p` from Theorem 1.1.

## Point sets

Two sources are used.

1. **Hand points.** Coordinates are written in the experiment file. They exist so that a person can check one edge and one non-edge by hand.
2. **Seeded Gaussian sample.** For dimension `k` and seed `s`, a NumPy Generator draws `2k` independent standard normal reals for each point, reshapes them into `k` complex coordinates, and divides by the Euclidean norm. The same seed and the same `numpy` Generator algorithm reproduce the same points. This distribution is uniform on the sphere. It is not the equal-measure small-diameter partition of Lemma 2.4.

## What the dimension sweep measures

`data/density-sweep.json` records, for each dimension, three fractions of the cross pairs:

- **arc rate**, the share whose Hermitian argument lies in `[0, 2πℓ/p]`;
- **stripe rate**, the share that stays at least `Kμ` away from every rotated real axis;
- **both rate**, the share that is a B2 edge. On a balanced bipartition this is the cross density.

The arc rate on uniform points sits near `ℓ/p` already at modest dimension, because the argument of a nonzero inner product is roughly uniform. The stripe rate does not. Theorem 1.1 needs both, and it needs the bad set for the stripe condition to have small measure, which the paper obtains from a cap estimate when `εK` is small. The sweep includes a series with `ε = 0.2`, `K = 5` (so that estimate is vacuous) and a series with `ε = 0.05`, `K = 2`. Neither series is a fine partition of the sphere, so neither is a numerical proof of the theorem. The gap between the both-rate and `ℓ/p` is the quantity a reader of Section 3 can watch.

## Parameters in the shipped experiments

The paper sends `k → ∞` first and only then lets `μ = ε / √(2k)` and `K` tend to infinity inside a hierarchy `1/k ≪ ε ≪ 1/K ≪ 1/p`. On a laptop-sized sample that hierarchy makes `√μ` so small that internal edges disappear and the imaginary-part threshold `Kμ` becomes a statement about noise.

The random experiments therefore use fixed, moderate thresholds `μ = 0.05` and `K = 2`, with `p = 3` and `ℓ ∈ {1, 2}`, on `k ∈ {2, 3}` and `n ∈ {12, 24}` points in each part. These values make both rules visible. They do not satisfy the paper’s asymptotic hierarchy, and the README says so.

## Tolerances

- A vector is rejected unless `abs(\|z\| − 1) ≤ 1e-9`.
- An internal comparison `\|w − ρ^h w'\| ≤ √μ` is accepted when the distance is at most `√μ * (1 + 1e-9) + 1e-12`.
- An imaginary-part comparison `\|Im(·)\| ≥ Kμ` is accepted when the absolute value is at least `Kμ * (1 − 1e-9) − 1e-15`.
- Arguments use `cmath.phase`, range `(-π, π]`. Membership in `[0, 2πℓ/p]` is evaluated after mapping a negative phase into `[0, 2π)` when the arc extends past `π`. The right endpoint is closed.

## Clique and independence caps

Triangles are counted for graphs with at most 80 vertices. Cliques of size at most `p + 2` are sought by enumerating combinations when the graph has at most 40 vertices. The ordinary independence number is computed by scanning subsets when the graph has at most 20 vertices. The `p`-independence number, which rejects every set containing a clique of order `p`, is computed only up to 12 vertices. Larger graphs leave those keys out and record the reason.

## Output layout

Each experiment writes:

- `data/<name>.json` — full record (points, edges, witnesses, statistics).
- `data/summary.csv` — one row per experiment.
- `apps/web/public/data/<name>.json` — the same JSON the site loads.
- `apps/web/public/data/index.json` — the list of dataset ids.

Re-running `python -m grt.experiments.run` from `python/` overwrites these files. Seeds are constants in `python/src/grt/experiments/run.py`.
