"""Finite graph defined by the Section 3.1 rules B1 and B2."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from grt.geometry.complex import (
    argument,
    argument_in_arc,
    at_least,
    hermitian_inner,
    imag_stripe_min,
    require_unit,
    rotation_distance,
    within_upper,
)


@dataclass(frozen=True)
class Parameters:
    p: int
    ell: int
    mu: float
    k_stripe: float

    def validate(self) -> None:
        if self.p < 2:
            raise ValueError("p must be an integer ≥ 2")
        if not (1 <= self.ell < self.p):
            raise ValueError("ell must satisfy 1 ≤ ell < p")
        if self.mu <= 0 or self.k_stripe <= 0:
            raise ValueError("mu and K must be positive")


def build_graph(
    part_w: list[np.ndarray],
    part_z: list[np.ndarray],
    p: int,
    ell: int,
    mu: float,
    k_stripe: float,
) -> dict:
    """Apply B1 inside each part and B2 across the cut.

    The result is a plain dictionary so experiments can write it as JSON.
    No density or freeness claim is attached.
    """
    params = Parameters(p=p, ell=ell, mu=mu, k_stripe=k_stripe)
    params.validate()
    w_points = [require_unit(point) for point in part_w]
    z_points = [require_unit(point) for point in part_z]
    if w_points and z_points and w_points[0].shape != z_points[0].shape:
        raise ValueError("W and Z must lie in the same C^k")
    dimension = int(w_points[0].size if w_points else z_points[0].size)

    points = []
    for index, vector in enumerate(w_points):
        points.append(_point_record(f"w{index}", "W", vector))
    for index, vector in enumerate(z_points):
        points.append(_point_record(f"z{index}", "Z", vector))

    edges: list[dict] = []
    edges.extend(_internal_edges(w_points, "w", params))
    edges.extend(_internal_edges(z_points, "z", params))
    edges.extend(_cross_edges(w_points, z_points, params))
    return {
        "parameters": {
            "p": p,
            "ell": ell,
            "mu": mu,
            "K": k_stripe,
            "k": dimension,
        },
        "points": points,
        "edges": edges,
        "guarantees": "none; finite sample",
    }


def internal_witness(left: np.ndarray, right: np.ndarray, p: int, mu: float) -> dict | None:
    """Smallest h ∈ {1, …, p−1} with ‖left − ρ^h right‖ ≤ √μ, if any."""
    threshold = math.sqrt(mu)
    best: dict | None = None
    for h in range(1, p):
        distance = rotation_distance(left, right, p, h)
        if within_upper(distance, threshold):
            record = {"h": h, "distance": distance, "threshold": threshold}
            if best is None or h < best["h"]:
                best = record
    return best


def cross_witness(left: np.ndarray, right: np.ndarray, p: int, ell: int, mu: float, k_stripe: float) -> dict | None:
    """Witness for B2, or None when the pair is a non-edge."""
    inner = hermitian_inner(left, right)
    minimum = imag_stripe_min(inner, p)
    threshold = k_stripe * mu
    if not at_least(minimum, threshold):
        return None
    if not argument_in_arc(inner, p, ell):
        return None
    return {
        "argument": argument(inner),
        "argument_upper": 2.0 * math.pi * ell / p,
        "min_abs_im": minimum,
        "im_threshold": threshold,
        "inner_re": inner.real,
        "inner_im": inner.imag,
    }


def rotation_index_matches(h_i: int, h_j: int, h_ij: int, p: int) -> bool:
    """Check the rotation-difference relation from the first sentence of Lemma 3.1.

    If w_i is an h_i-rotation of w_t and w_j is an h_j-rotation of w_t, the
    paper concludes that w_i is an (h_i − h_j)-rotation of w_j and h_i ≠ h_j.
    This function only checks the index arithmetic on recorded witnesses.
    """
    if h_i % p == h_j % p:
        return False
    return h_ij % p == (h_i - h_j) % p


def _internal_edges(points: list[np.ndarray], prefix: str, params: Parameters) -> list[dict]:
    edges = []
    for i, left in enumerate(points):
        for j in range(i + 1, len(points)):
            witness = internal_witness(left, points[j], params.p, params.mu)
            if witness is None:
                continue
            edges.append(
                {
                    "source": f"{prefix}{i}",
                    "target": f"{prefix}{j}",
                    "kind": "internal",
                    "witness": witness,
                }
            )
    return edges


def _cross_edges(part_w: list[np.ndarray], part_z: list[np.ndarray], params: Parameters) -> list[dict]:
    edges = []
    for i, left in enumerate(part_w):
        for j, right in enumerate(part_z):
            witness = cross_witness(left, right, params.p, params.ell, params.mu, params.k_stripe)
            if witness is None:
                continue
            edges.append(
                {
                    "source": f"w{i}",
                    "target": f"z{j}",
                    "kind": "cross",
                    "witness": witness,
                }
            )
    return edges


def _point_record(point_id: str, part: str, vector: np.ndarray) -> dict:
    return {
        "id": point_id,
        "part": part,
        "coords": [{"re": float(value.real), "im": float(value.imag)} for value in vector],
    }
