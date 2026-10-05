"""Finite search related to the Bollobás–Erdős rhombus lemma.

Theorem 2.5 says that for 0 < μ < 1/4 no four points on a real unit sphere
realise two long pairs and four short cross pairs. Searching a finite set
can find a violator or report that this particular set has none. It does
not prove the lemma.
"""

from __future__ import annotations

from itertools import combinations

import numpy as np

from grt.geometry.complex import as_vector, within_upper


def _distance(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.linalg.norm(left - right))


def find_rhombus(points: list[np.ndarray], mu: float) -> dict | None:
    """Return the first 4-tuple violating the rhombus inequalities, or None.

    A hit is four indices (p1, p2, q1, q2) with
    d(p1, p2) ≥ 2 − μ, d(q1, q2) ≥ 2 − μ, and d(pi, qj) ≤ √2 − μ.
    Points are compared as real vectors. Callers that start from complex
    samples should pass the image under φ.
    """
    if not 0 < mu < 0.25:
        raise ValueError("mu must lie in (0, 1/4) for the rhombus search")
    real = []
    for point in points:
        vector = np.asarray(as_vector(point))
        if np.max(np.abs(np.imag(vector))) > 1e-8:
            raise ValueError("rhombus search expects real vectors")
        real.append(np.real(vector).astype(np.float64))
    long_at_least = 2.0 - mu
    short_at_most = math_sqrt2() - mu
    for combo in combinations(range(len(real)), 4):
        for pairing in _pairings(combo):
            (a, b), (c, d) = pairing
            if _distance(real[a], real[b]) + 1e-12 < long_at_least:
                continue
            if _distance(real[c], real[d]) + 1e-12 < long_at_least:
                continue
            crosses = (
                _distance(real[a], real[c]),
                _distance(real[a], real[d]),
                _distance(real[b], real[c]),
                _distance(real[b], real[d]),
            )
            if all(within_upper(value, short_at_most) for value in crosses):
                return {
                    "indices": [a, b, c, d],
                    "long_distances": [
                        _distance(real[a], real[b]),
                        _distance(real[c], real[d]),
                    ],
                    "cross_distances": list(crosses),
                    "note": "4-tuple in this finite set; not a counterexample to Theorem 2.5 unless the points lie on a sphere and the inequalities are strict",
                }
    return None


def math_sqrt2() -> float:
    return float(np.sqrt(2.0))


def _pairings(indices: tuple[int, int, int, int]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    a, b, c, d = indices
    return [((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c))]
