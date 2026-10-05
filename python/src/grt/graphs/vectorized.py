"""Vectorised B1/B2 checks.

These match the scalar predicates in `complex_be`, including the same
slack on the thresholds. They exist so a dimension sweep stays exact
rather than switching to a looser approximation.
"""

from __future__ import annotations

import math

import numpy as np

from grt.geometry.complex import REL_TOL, root_of_unity


def stack_points(points: list[np.ndarray]) -> np.ndarray:
    if not points:
        return np.zeros((0, 1), dtype=np.complex128)
    return np.vstack([np.asarray(point, dtype=np.complex128) for point in points])


def hermitian_matrix(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """⟨left_i, right_j⟩ for every pair, with ⟨w, z⟩ = Σ w_t conj(z_t)."""
    return left @ right.conj().T


def stripe_and_arc(
    inners: np.ndarray,
    p: int,
    ell: int,
    mu: float,
    k_stripe: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Boolean masks: stripe condition, arc condition, and the pointwise min |Im|."""
    minimum = np.full(inners.shape, np.inf)
    for h in range(p):
        rotated = root_of_unity(p, h) * inners
        minimum = np.minimum(minimum, np.abs(rotated.imag))
    threshold = k_stripe * mu
    stripe = minimum >= threshold * (1.0 - REL_TOL) - 1e-15
    upper = 2.0 * math.pi * ell / p
    turn = np.mod(np.angle(inners), 2.0 * math.pi)
    nonzero = inners != 0
    arc = nonzero & (turn <= upper * (1.0 + REL_TOL) + 1e-12)
    return stripe, arc, minimum


def internal_mask(points: np.ndarray, p: int, mu: float) -> tuple[np.ndarray, np.ndarray]:
    """Upper-triangular adjacency and the smallest witnessing h (0 if none)."""
    n = points.shape[0]
    adjacent = np.zeros((n, n), dtype=bool)
    witness_h = np.zeros((n, n), dtype=np.int32)
    threshold = math.sqrt(mu)
    limit = threshold * (1.0 + REL_TOL) + 1e-12
    for h in range(1, p):
        rotated = root_of_unity(p, h) * points
        # ‖points[i] − ρ^h points[j]‖
        diff = points[:, None, :] - rotated[None, :, :]
        distance = np.linalg.norm(diff, axis=2)
        hit = distance <= limit
        np.fill_diagonal(hit, False)
        newly = hit & ~adjacent
        witness_h[newly] = h
        adjacent |= hit
    return adjacent, witness_h
