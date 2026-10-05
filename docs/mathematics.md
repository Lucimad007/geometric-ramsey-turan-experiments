# Mathematical background

This page is a short guide to the objects the code evaluates. Proofs and asymptotic statements stay in the paper.

H. Liu, C. Reiher, M. Sharifzadeh, K. Staden, Geometric constructions for Ramsey–Turán theory, *Journal of the European Mathematical Society* **28** (2026), 79–112. arXiv:2103.10423. DOI: 10.4171/JEMS/1712.

## Ramsey–Turán density

For integers `p ≤ q`, the Ramsey–Turán number `RT_p(n, K_q, m)` is the maximum number of edges in an `n`-vertex `K_q`-free graph whose `p`-independence number is at most `m`. The `p`-independence number `α_p(G)` is the size of a largest vertex set that contains no clique of order `p`. The density studied in the paper is the iterated limit

`ϱ_p(q) = lim_{ε→0} lim_{n→∞} RT_p(n, K_q, εn) / binom(n, 2)`.

When `p = 2`, this density is known and the extremal graphs are described by a periodic block structure. For `p > 2` the same periodic picture was conjectured. The paper gives a geometric construction that meets the conjectured density for a range of parameters, and a second construction that exceeds it in other ranges. This repository does not decide either statement.

## The complex Bollobás–Erdős graph, as a finite rule

Fix integers `1 ≤ ℓ < p`. Let `ρ = exp(2πi / p)`. Let `W` and `Z` be finite sets of unit vectors in `C^k`, of equal cardinality in the paper’s construction. The Hermitian product is

`⟨w, z⟩ = Σ_{j=1}^k w_j conj(z_j)`.

Two internal rules and one cross rule define the edges. They are stated in Section 3.1 of the paper and implemented in `python/src/grt/graphs/complex_be.py`.

**Internal.** Distinct points `w, w'` in the same part are adjacent when some rotation index `h ∈ {1, …, p−1}` brings them within distance `√μ`:

`\|w − ρ^h w'\| ≤ √μ`.

**Cross.** A pair `(w, z)` with `w ∈ W` and `z ∈ Z` is adjacent when the inner product stays away from `p` equally spaced real rays, and its argument falls in an arc of length `2πℓ/p`:

1. `\|Im(ρ^h ⟨w, z⟩)\| ≥ K μ` for every `h ∈ {0, …, p−1}`.
2. `arg⟨w, z⟩ ∈ [0, 2πℓ/p]`.

Condition 2 is the paper’s requirement that some angle `α` in that interval makes `e^{-iα} ⟨w, z⟩` real and nonnegative. The length of the arc is the source of the factor `ℓ/p` in the paper’s cross density. On a finite set that factor is a target of the continuous construction, not a count the code enforces.

## What the geometry is for

The paper places one point in each cell of a fine equal-measure partition of the complex sphere. In high dimension, most pairs are far from every nontrivial rotate `ρ^h w'`, so internal edges are rare, while a positive fraction of cross pairs have argument in the arc and avoid the forbidden stripes. Clique-freeness, when `ℓ ≤ p/2`, uses a separate geometric obstruction (a complex form of the Bollobás–Erdős rhombus configuration) that is proved, not enumerated.

Those measure and freeness arguments need the partition and the dimension to grow in a linked way. The code keeps the edge rules and drops the measure argument. A random cloud of unit vectors is a legitimate input to the rules and an illegitimate substitute for the theorem.

## Real picture of a complex point

The map `(x_j + i y_j)_j ↦ (x_1, y_1, …, x_k, y_k)` identifies `S^{k-1}(C)` with the real sphere `S^{2k-1}(R)`. The viewer draws the first three coordinates of that real vector. For `k = 1` the picture is planar (the third coordinate is zero). For `k ≥ 2` it is a shadow of a higher-dimensional sphere.
