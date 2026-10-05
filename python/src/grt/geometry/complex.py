"""Numerically stable operations on vectors in C^k.

The inner product follows the paper's convention ⟨w, z⟩ = Σ w_i conj(z_i).
Arguments lie in (-π, π]. A vector is treated as a unit vector when its
Euclidean norm is within ABS_TOL of 1.
"""

from __future__ import annotations

import cmath
import math

import numpy as np

ABS_TOL = 1e-9
REL_TOL = 1e-9

Vector = np.ndarray


def as_vector(coords: np.ndarray) -> Vector:
    """Return a one-dimensional complex array."""
    vector = np.asarray(coords, dtype=np.complex128).reshape(-1)
    if vector.size == 0:
        raise ValueError("a point needs at least one coordinate")
    return vector


def norm(vector: Vector) -> float:
    """Euclidean norm √⟨z, z⟩."""
    vector = as_vector(vector)
    return float(np.linalg.norm(vector))


def require_unit(vector: Vector, tol: float = ABS_TOL) -> Vector:
    """Return the vector, or raise if it is not a unit vector."""
    vector = as_vector(vector)
    if abs(norm(vector) - 1.0) > tol:
        raise ValueError(f"expected a unit vector, got norm {norm(vector)}")
    return vector


def hermitian_inner(left: Vector, right: Vector) -> complex:
    """⟨left, right⟩ = Σ left_i conj(right_i)."""
    left = as_vector(left)
    right = as_vector(right)
    if left.shape != right.shape:
        raise ValueError("inner product requires equal dimensions")
    return complex(np.vdot(right, left))


def argument(value: complex) -> float:
    """Argument in (-π, π]. Zero has undefined argument; this raises."""
    if value == 0:
        raise ValueError("argument of zero is undefined")
    return float(cmath.phase(value))


def root_of_unity(p: int, h: int = 1) -> complex:
    """ρ^h for ρ = exp(2πi/p)."""
    if p < 1:
        raise ValueError("p must be a positive integer")
    return cmath.exp(2j * math.pi * (h % p) / p)


def rotation_distance(left: Vector, right: Vector, p: int, h: int) -> float:
    """‖left − ρ^h right‖."""
    left = as_vector(left)
    right = as_vector(right)
    rotated = root_of_unity(p, h) * right
    return float(np.linalg.norm(left - rotated))


def within_upper(value: float, threshold: float, rel: float = REL_TOL, abs_tol: float = 1e-12) -> bool:
    """True when value is at most threshold, up to a small slack."""
    return value <= threshold * (1.0 + rel) + abs_tol


def at_least(value: float, threshold: float, rel: float = REL_TOL, abs_tol: float = 1e-15) -> bool:
    """True when value is at least threshold, up to a small slack."""
    return value >= threshold * (1.0 - rel) - abs_tol


def argument_in_arc(value: complex, p: int, ell: int) -> bool:
    """True when arg(value) lies in [0, 2πℓ/p], endpoints included.

    The representative used for the comparison is the argument mapped into
    [0, 2π). This matches the paper's condition that some α in the interval
    sends e^{-iα} value onto the nonnegative real axis.
    """
    if p <= 0 or ell < 0:
        raise ValueError("p and ell must be nonnegative, with p positive")
    if value == 0:
        return False
    turn = argument(value) % (2.0 * math.pi)
    # cmath.phase returns (-π, π], so a negative phase modulo 2π lands in (π, 2π).
    upper = 2.0 * math.pi * ell / p
    return 0.0 <= turn <= upper * (1.0 + REL_TOL) + 1e-12


def imag_stripe_min(inner: complex, p: int) -> float:
    """min_{h=0}^{p-1} |Im(ρ^h inner)|."""
    if p < 1:
        raise ValueError("p must be a positive integer")
    smallest = math.inf
    for h in range(p):
        rotated = root_of_unity(p, h) * inner
        smallest = min(smallest, abs(rotated.imag))
    return float(smallest)


def one_minus_root_modulus(p: int, m: int) -> float:
    """|1 − ρ^m|."""
    return abs(1 - root_of_unity(p, m))


def passes_elementary_gap(p: int, m: int) -> bool:
    """Return whether |1 − ρ^m| ≥ 4/p for m not divisible by p.

    This is the elementary bound in the proof of Lemma 3.1. It is an
    arithmetic check, not a freeness proof.
    """
    if m % p == 0:
        return False
    return one_minus_root_modulus(p, m) + 1e-12 >= 4.0 / p
