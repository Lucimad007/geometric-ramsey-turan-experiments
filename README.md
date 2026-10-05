# Geometric Ramsey–Turán experiments

This repository provides a computational exploration of geometric constructions in Ramsey–Turán theory. It does not implement the full theoretical paper or reproduce its non-constructive existence proofs.

The code evaluates two finite edge rules on explicit point sets and displays the resulting graph. A run on a sample is not a proof of a Ramsey–Turán density.

## Paper

H. Liu, C. Reiher, M. Sharifzadeh, K. Staden, Geometric constructions for Ramsey–Turán theory, *Journal of the European Mathematical Society* **28** (2026), 79–112.

- arXiv: [2103.10423](https://arxiv.org/abs/2103.10423)
- DOI: [10.4171/JEMS/1712](https://doi.org/10.4171/JEMS/1712)
- Local copy: [`papers/liu-reiher-sharifzadeh-staden-geometric-constructions-ramsey-turan.pdf`](papers/liu-reiher-sharifzadeh-staden-geometric-constructions-ramsey-turan.pdf)
- Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

## Mathematical background

The paper studies the Ramsey–Turán density `ϱ_p(q)`, the asymptotic maximum edge density of a `K_q`-free graph on `n` vertices whose `p`-independence number is `o(n)`. One construction, in Section 3, places two finite sets `W` and `Z` on the complex unit sphere and joins pairs by rotation distance (rule B1) and by the argument of a Hermitian inner product (rule B2). In high dimension, with points taken from a fine equal-measure partition, the cross density approaches `ℓ/p` and, for `ℓ ≤ p/2`, the graph is `K_{p+ℓ+1}`-free.

A second construction, in Section 4, produces denser almost multipartite graphs from a high-dimensional Borsuk hypergraph. The upper bounds in Section 5 are weighted extremal arguments.

A short account in our own words is in [`docs/mathematics.md`](docs/mathematics.md). The decision of what is computed is in [`docs/IMPLEMENTATION_SCOPE.md`](docs/IMPLEMENTATION_SCOPE.md).

## Implemented

- Hermitian inner products, norms, arguments, and roots of unity on `C^k`.
- Rule B1: an internal edge when some `h ∈ {1,…,p−1}` satisfies `‖w − ρ^h w′‖ ≤ √μ`.
- Rule B2: a cross edge when `|Im(ρ^h ⟨w, z⟩)| ≥ Kμ` for every `h`, and `arg⟨w, z⟩ ∈ [0, 2πℓ/p]`.
- Seeded uniform samples on the complex sphere (normalised Gaussians).
- Counts on the concrete graph: densities, degrees, components, and, under explicit size caps, triangles, small cliques, and independence numbers.
- A bounded search for rhombus configurations on a supplied real point set. Absence in a sample is not Theorem 2.5.
- A viewer that loads the precomputed JSON. It does not reimplement the edge rules.

## Not implemented

- The equal-measure partition of the sphere (Lemma 2.4) and the cap-measure lemmas.
- Sublinear `p`-independence, `o(1)` internal density, and `K_{p+ℓ+1}`-freeness.
- The Section 4 Borsuk hypergraph, its blow-up, and Theorem 1.3.
- The weighted-graph upper bounds (Theorems 1.4 and 1.5).
- Any numerical value of `ϱ_p(q)`.

The shipped random experiments use `μ = 0.05` and `K = 2` so that both rules are visible on a few dozen points. Those constants do not follow the paper’s asymptotic hierarchy `1/k ≪ ε ≪ 1/K ≪ 1/p`.

## Architecture

```text
python/src/grt     edge rules, sampling, counts
experiments/       how to regenerate the JSON
data/              full experiment records and summary.csv
apps/web           Next.js viewer of public/data
docs/              scope, mathematics, methodology
```

Python is the source of the mathematics. The site only reads JSON written by `python -m grt.experiments.run`. Vercel should use root directory `apps/web`. The Python package is not deployed.

## Installation

Python 3.11 or newer, and Node 20 or newer.

```bash
pip install -e "python[dev]"
npm install --prefix apps/web
```

## Python usage

From `python/`, with the package installed:

```bash
python -c "from grt.graphs.complex_be import build_graph; from grt.graphs.samples import sample_complex_sphere; print(len(build_graph(sample_complex_sphere(8, 2, 0), sample_complex_sphere(8, 2, 1), p=3, ell=1, mu=0.05, k_stripe=2)['edges']))"
```

`build_graph` returns points, edges, and a witness on every edge. See [`docs/methodology.md`](docs/methodology.md) for tolerances.

## Tests

```bash
cd python
python -m pytest
```

From `apps/web`:

```bash
npm test
```

The web test checks the coordinate projection `φ`. It does not re-check the edge rules.

## Reproduce the experiments

```bash
cd python
python -m grt.experiments.run
```

This overwrites `data/*.json`, `data/summary.csv`, and `apps/web/public/data/`. Seeds are constants in `python/src/grt/experiments/run.py`. Each record has `"guarantees": "none; finite sample"`.

## Web application

```bash
npm run dev --prefix apps/web
```

Open the local URL Next prints. Choose a dataset in the side panel. “Points” shows the sample; “Graph” draws the stored edges. Selecting a vertex lists the witnesses that Python recorded (rotation index and distance, or argument and imaginary-part minimum). Changing `p`, `ℓ`, `μ`, `K`, or the sample switches to another precomputed file. It does not build a new graph in the browser.

## Deployment

In the Vercel project settings set **Root Directory** to `apps/web`. The framework preset is Next.js. The build command is `npm run build`. No Python runtime is required on Vercel, because the viewer ships the JSON under `apps/web/public/data/`.

Confirm the build locally:

```bash
npm run build --prefix apps/web
```

## Limitations

Floating-point comparisons use a documented slack around the thresholds `√μ` and `Kμ`. Uniform samples are not the partition used in the proof of Theorem 1.1. Clique and independence searches stop at the vertex caps in `docs/methodology.md`. The three-dimensional view keeps only the first three real coordinates of `φ`.

## Reproducibility

- Edge rules: `python/src/grt/graphs/complex_be.py`
- Sampler: NumPy `Generator(PCG64(seed))`, independent standard normals, then normalise
- Experiment list and seeds: `python/src/grt/experiments/run.py`
- Snapshot test of one 8-vertex edge set: `python/tests/test_rules.py`
