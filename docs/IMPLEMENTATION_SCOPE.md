# Implementation scope

This note records what this repository computes, what it only samples experimentally, and what it leaves to the paper. It is a scope decision, not a proof.

Citation: H. Liu, C. Reiher, M. Sharifzadeh, K. Staden, Geometric constructions for Ramsey–Turán theory, *Journal of the European Mathematical Society* **28** (2026), 79–112. arXiv:2103.10423. DOI: 10.4171/JEMS/1712.

## Conventions used below

- **IMPLEMENTABLE.** A finite predicate or arithmetic check that, given explicit points and parameters, returns a definite answer.
- **EXPERIMENTAL / APPROXIMATE.** A finite sample or a bounded search. The output describes that sample. It does not establish an asymptotic theorem.
- **THEORETICAL / NOT IMPLEMENTABLE.** An existence argument, a measure-theoretic limit, or an extremal proof for which the paper does not supply an algorithm.

Numerical work uses IEEE complex arithmetic. A vector is accepted as a unit vector when its Euclidean norm differs from 1 by at most `1e-9`, unless a test sets a different tolerance. Arguments are returned in `(-π, π]`.

## Definitions

### Ramsey–Turán density

| | |
|---|---|
| Paper | Section 1.1, definition of `ϱ_p(q)` |
| Object | `lim_{ε→0} lim_{n→∞} RT_p(n, K_q, εn) / binom(n,2)` |
| Rule | Double limit of a maximum edge count |
| Computational reading | None. The quantity is an asymptotic density. |
| Status | **THEORETICAL** |

The repository never reports a value of `ϱ_p(q)`.

### p-independence number

| | |
|---|---|
| Paper | Section 1, definition of `α_p(G)` |
| Object | Largest vertex set that spans no copy of `K_p` |
| Rule | Exact maximum over subsets |
| Computational reading | On a concrete graph with at most 20 vertices, an exhaustive search can return the ordinary independence number. The `p`-independence number is computed only up to 12 vertices. Above those caps the field is omitted. |
| Status | **EXPERIMENTAL** on small graphs; **THEORETICAL** as the `o(n)` claim in Theorem 1.1 |

### Complex unit sphere and inner product

| | |
|---|---|
| Paper | Notation paragraph and display (3) in Section 2 |
| Object | `S^{k-1}(C) = {z ∈ C^k : Σ \|z_i\|^2 = 1}` |
| Rule | `⟨w, z⟩ = Σ_i w_i conj(z_i)`, `\|z\| = sqrt(⟨z, z⟩)`. The real isometry `φ` sends `(x_j + i y_j)` to `(x_1, y_1, …, x_k, y_k)` in `S^{2k-1}(R)`. |
| Inputs | A length-`k` complex vector |
| Outputs | Norm, inner product, argument, real coordinates under `φ` |
| Limitations | Floating-point inner products. `φ` is used for display of the first three real coordinates, which is a projection when `2k > 3`. |
| Not reproduced | Lebesgue measure on the sphere, spherical caps, concentration |
| Status | **IMPLEMENTABLE** as linear algebra |

### Root of unity

| | |
|---|---|
| Paper | Section 3.1, `ρ := cos(2π/p) + i sin(2π/p)` |
| Rule | `ρ = exp(2πi/p)`, computed with `cmath.exp` |
| Status | **IMPLEMENTABLE** |

## Graph rules that are implemented

### B1, internal edges

| | |
|---|---|
| Paper | Section 3.1, rule B1 |
| Object | Graph on a finite set `W` (and, separately, on `Z`) of points in `C^k` |
| Exact rule | Distinct `w, w'` are adjacent if and only if some integer `h ∈ {1, …, p−1}` satisfies `\|w − ρ^h w'\| ≤ √μ` |
| Inputs | Unit vectors, integers `p ≥ 2`, real `μ > 0` |
| Outputs | Each edge, the witnessing `h`, and the distance `\|w − ρ^h w'\|`. If several `h` work, the smallest `h` is stored. |
| Limitations | Comparison uses a relative slack of `1e-9` on the threshold so that a distance that lands on `√μ` in exact arithmetic is not dropped by rounding. |
| Not reproduced | The claim that these edges have density `o(1)` (Lemma 3.4), or that the graph is `K_{p+1}`-free for every point set (Lemma 3.1 is a structural lemma under B1, proved by a pigeonhole argument that is not re-proved here). |
| Status | **IMPLEMENTABLE** as a predicate on supplied points |

### B2, cross edges

| | |
|---|---|
| Paper | Section 3.1, rule B2; Figure 2 illustrates the two conditions for `p = 3` |
| Object | Bipartite pairs between finite sets `W` and `Z` |
| Exact rule | `(w, z)` is an edge if and only if both of the following hold. (i) For every `h ∈ {0, …, p−1}`, `\|Im(ρ^h ⟨w, z⟩)\| ≥ Kμ`. (ii) There exists `α ∈ [0, 2πℓ/p]` such that `e^{-iα} ⟨w, z⟩` is real and nonnegative. Condition (ii) is the same as `arg⟨w, z⟩ ∈ [0, 2πℓ/p]`, with arguments taken in `(-π, π]`. |
| Inputs | Unit vectors, integers `1 ≤ ℓ < p`, reals `μ > 0`, `K > 0` |
| Outputs | The edge, `arg⟨w, z⟩`, and `min_h \|Im(ρ^h ⟨w, z⟩)\|` |
| Limitations | A negative argument is outside `[0, 2πℓ/p]`. The endpoint `2πℓ/p` is included. If `ℓ/p > 1/2`, the interval may pass `π`; arguments are compared after wrapping into `[0, 2π)`. |
| Not reproduced | Lemma 3.5, which says each vertex has about `(ℓ/p)n` cross-neighbours when the points come from a fine equal-measure partition. A finite sample can have any cross density. |
| Status | **IMPLEMENTABLE** as a predicate on supplied points |

### Rotation arithmetic on a concrete triangle

| | |
|---|---|
| Paper | Lemma 3.1, first sentence, and the bound `\|1 − ρ^m\| ≥ 4/p` in display (5) |
| Object | Three vertices already joined by B1, together with recorded rotation indices |
| Exact rule | If `w_i` is an `h_i`-rotation of `w_t` and `w_j` is an `h_j`-rotation of `w_t`, the code checks whether `w_i` is an `(h_i − h_j) mod p` rotation of `w_j` in the sense of the stored witnesses, and evaluates `\|1 − ρ^m\|` against `4/p`. |
| Not reproduced | The deduction that every point set yields a `K_{p+1}`-free graph. That deduction uses the diameter of the domains and the smallness of `μ` relative to `1/p`. |
| Status | **IMPLEMENTABLE** as a check on recorded witnesses; **THEORETICAL** as a freeness theorem |

## Experimental searches

### Uniform points on the sphere

| | |
|---|---|
| Paper | The construction begins with Lemma 2.4, an equal-measure partition into `n` domains of diameter at most `μ/4`, then one point from each domain |
| What we do instead | Draw i.i.d. standard normal coordinates in `R^{2k}`, normalise, and read them as `C^k` via `φ^{-1}`. The generator is seeded. |
| Why this is not the construction | Lemma 2.4 asserts a partition with a diameter bound. The paper cites it as folklore and does not give a partition algorithm. Random points do not have disjoint domains of controlled diameter. |
| Status | **EXPERIMENTAL** |

### Rhombus search

| | |
|---|---|
| Paper | Theorem 2.5 (Bollobás–Erdős rhombus lemma): for `0 < μ < 1/4` there are no four points on a real sphere with two pairs at distance at least `2−μ` and all four cross pairs at distance at most `√2 − μ` |
| Computational reading | On a supplied finite subset of a real sphere, test all 4-tuples against those inequalities. |
| Output | “No such 4-tuple in this set” or an explicit 4-tuple. |
| Not reproduced | The lemma itself. Absence in a sample is not a proof. |
| Status | **EXPERIMENTAL** |

### Graph statistics

Measured on the concrete graph from B1 and B2: vertex and edge counts, edge density `2\|E\|/(\|V\|(\|V\|−1))`, internal densities inside `W` and inside `Z`, cross density `e(W,Z)/(\|W\|\|Z\|)`, degree minimum, mean, and maximum, and the number of connected components.

Triangle counts are computed when `\|V\| ≤ 80`. A search for a clique on at most `p+2` vertices, and an exact `α_r` for `r ≤ p`, run only when `\|V\| ≤ 40`. Larger instances omit those fields and record the reason. None of these numbers is a Ramsey–Turán density.

## Explicit non-goals

The following are not implemented. Each one is an existence or extremal argument rather than a finite rule.

- Lemma 2.1, Lemma 2.2, Lemma 2.3: measure of spherical caps and the two-set distance bound.
- Lemma 2.4: equal-measure small-diameter partition of the sphere.
- Lemma 3.2 and Lemma 3.3: sublinear `p`-independence via concentration.
- Lemma 3.4: maximum degree `≤ e^{-k/2} n`.
- Lemma 3.5 and Claim 3.6: cross degree `(ℓ/p ± K^{-1/2}) n`.
- Section 3.4: `K_{p+ℓ+1}`-freeness when `ℓ ≤ p/2` (Lemma 3.7 and the counting argument that follows).
- Corollary 1.2: complete joins of several copies, used to lift the two-part graph to more parts. The paper invokes graphs that already have sublinear `p`-independence number; those graphs are not constructed here.
- All of Section 4: the auxiliary graphs `Q_h`, the hypergraph `B`, the blow-up `B'`, the Borsuk graph `B(ℓ)`, the edge-colouring rule for cross edges, and Theorem 1.3. The cross rule in Section 4 refers to coordinates of vertices that are themselves points of `B'`, and `B'` is obtained by a blow-up and a deletion argument cited from earlier work. There is no finite input on which that object is defined explicitly.
- Section 5: weighted graphs `G̃_p(q)`, the embedding lemma, and Theorems 1.4 and 1.5.
- Theorem 1.1 as a theorem. Running B1 and B2 on a sample does not prove `ϱ_p(p+ℓ+1) ≥ ℓ/(2p)`.
