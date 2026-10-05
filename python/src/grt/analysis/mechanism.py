"""Finite readings of the Section 3 mechanism.

Nothing here estimates ϱ_p(q). The targets ℓ/p and ℓ/(2p) are the
quantities Theorem 1.1 would produce for a balanced two-part graph coming
from a fine partition of a high-dimensional sphere. A uniform sample is a
different point set, and the comparison is only a comparison.
"""

from __future__ import annotations

import math

import numpy as np

from grt.graphs.complex_be import rotation_index_matches
from grt.graphs.vectorized import hermitian_matrix, internal_mask, stack_points, stripe_and_arc


def mechanism_report(
    part_w: list[np.ndarray],
    part_z: list[np.ndarray],
    edges: list[dict],
    p: int,
    ell: int,
    mu: float,
    k_stripe: float,
) -> dict:
    w_matrix = stack_points(part_w)
    z_matrix = stack_points(part_z)
    inners = hermitian_matrix(w_matrix, z_matrix) if len(part_w) and len(part_z) else np.zeros((0, 0))
    stripe, arc, _minimum = stripe_and_arc(inners, p, ell, mu, k_stripe) if inners.size else (
        np.zeros((0, 0), dtype=bool),
        np.zeros((0, 0), dtype=bool),
        np.zeros((0, 0)),
    )
    pair_count = int(inners.size)
    both = stripe & arc
    internal_w = _internal_density(w_matrix, p, mu)
    internal_z = _internal_density(z_matrix, p, mu)
    audit = _rotation_audit(edges, p)
    return {
        "cross_pair_count": pair_count,
        "stripe_rate": _rate(stripe, pair_count),
        "arc_rate": _rate(arc, pair_count),
        "both_rate": _rate(both, pair_count),
        "target_cross_density": ell / p,
        "cross_gap": (float(both.mean()) - ell / p) if pair_count else None,
        "target_balanced_density": ell / (2 * p),
        "internal_edge_rate_W": internal_w,
        "internal_edge_rate_Z": internal_z,
        "rotation_triangles": audit["triangles"],
        "rotation_triangles_matching_lemma": audit["matching"],
        "reading": (
            "both_rate is the fraction of cross pairs that satisfy B2. "
            "target_cross_density is ℓ/p from Theorem 1.1. "
            "target_balanced_density is ℓ/(2p), the graph density that theorem "
            "would give on two equal parts with negligible internal edges. "
            "A gap is a fact about this sample."
        ),
    }


def cross_cloud(
    part_w: list[np.ndarray],
    part_z: list[np.ndarray],
    p: int,
    ell: int,
    mu: float,
    k_stripe: float,
) -> list[dict]:
    """Every cross pair, with the two B2 conditions scored separately."""
    if not part_w or not part_z:
        return []
    inners = hermitian_matrix(stack_points(part_w), stack_points(part_z))
    stripe, arc, minimum = stripe_and_arc(inners, p, ell, mu, k_stripe)
    rows = []
    for i in range(inners.shape[0]):
        for j in range(inners.shape[1]):
            value = inners[i, j]
            rows.append(
                {
                    "w": f"w{i}",
                    "z": f"z{j}",
                    "re": float(value.real),
                    "im": float(value.imag),
                    "min_abs_im": float(minimum[i, j]),
                    "stripe": bool(stripe[i, j]),
                    "arc": bool(arc[i, j]),
                    "edge": bool(stripe[i, j] and arc[i, j]),
                }
            )
    return rows


def paper_thresholds(k: int, epsilon: float, k_stripe: float) -> float:
    """μ = ε / √(2k), the scale written in Section 3.1.

    The paper also requires 1/k ≪ ε ≪ 1/K ≪ 1/p and an enormous partition.
    Returning μ does not put a sample into that regime.
    """
    if k < 1 or epsilon <= 0:
        raise ValueError("k and epsilon must be positive")
    return epsilon / math.sqrt(2 * k)


def _internal_density(points: np.ndarray, p: int, mu: float) -> float | None:
    n = points.shape[0]
    if n < 2:
        return None
    adjacent, _witness = internal_mask(points, p, mu)
    edges = int(np.triu(adjacent, k=1).sum())
    return 2.0 * edges / (n * (n - 1))


def _rotation_audit(edges: list[dict], p: int) -> dict:
    """Count internal triangles whose recorded indices obey Lemma 3.1's relation."""
    oriented: dict[tuple[str, str], int] = {}
    neighbours: dict[str, set[str]] = {}
    for edge in edges:
        if edge["kind"] != "internal":
            continue
        source, target = edge["source"], edge["target"]
        h = int(edge["witness"]["h"])
        oriented[(source, target)] = h
        oriented[(target, source)] = (p - h) % p
        neighbours.setdefault(source, set()).add(target)
        neighbours.setdefault(target, set()).add(source)
    triangles = 0
    matching = 0
    seen: set[frozenset[str]] = set()
    for origin, nbs in neighbours.items():
        for left, right in _pairs(nbs):
            if right not in neighbours.get(left, ()):
                continue
            key = frozenset((origin, left, right))
            if key in seen:
                continue
            seen.add(key)
            triangles += 1
            if _triple_matches(origin, left, right, oriented, p):
                matching += 1
    return {"triangles": triangles, "matching": matching}


def _triple_matches(
    origin: str,
    left: str,
    right: str,
    oriented: dict[tuple[str, str], int],
    p: int,
) -> bool:
    # left and right as rotations of origin, then the edge between them.
    return rotation_index_matches(
        oriented[(left, origin)],
        oriented[(right, origin)],
        oriented[(left, right)],
        p,
    )


def _pairs(items: set[str]) -> list[tuple[str, str]]:
    ordered = sorted(items)
    return [(ordered[i], ordered[j]) for i in range(len(ordered)) for j in range(i + 1, len(ordered))]


def _rate(mask: np.ndarray, count: int) -> float | None:
    if count == 0:
        return None
    return float(mask.sum()) / count
