"""Hand-checkable tests for the Section 3 predicates."""

from __future__ import annotations

import math

import numpy as np
import pytest

from grt.analysis.stats import analyse
from grt.geometry.complex import (
    argument_in_arc,
    hermitian_inner,
    one_minus_root_modulus,
    passes_elementary_gap,
    require_unit,
    root_of_unity,
    within_upper,
)
from grt.geometry.rhombus import find_rhombus
from grt.graphs.complex_be import (
    build_graph,
    cross_witness,
    internal_witness,
    rotation_index_matches,
)
from grt.graphs.samples import sample_complex_sphere
from grt.graphs.vectorized import hermitian_matrix, stack_points, stripe_and_arc


def _e1() -> np.ndarray:
    return np.array([1, 0], dtype=np.complex128)


def _rho(p: int = 3) -> complex:
    return root_of_unity(p, 1)


def test_inner_product_conjugates_the_right_vector():
    left = np.array([1, 1j], dtype=np.complex128)
    right = np.array([1j, 1], dtype=np.complex128)
    # ⟨left, right⟩ = 1*conj(1j) + 1j*conj(1) = -1j + 1j = 0
    assert hermitian_inner(left, right) == pytest.approx(0)


def test_non_unit_is_rejected():
    with pytest.raises(ValueError):
        require_unit(np.array([2, 0], dtype=np.complex128))


def test_internal_edge_when_one_point_is_a_root_rotate_of_the_other():
    rho = _rho()
    left = _e1()
    right = np.array([rho, 0], dtype=np.complex128)
    witness = internal_witness(left, right, p=3, mu=0.05)
    assert witness is not None
    assert witness["h"] == 2
    assert witness["distance"] == pytest.approx(0.0, abs=1e-12)


def test_internal_non_edge_for_orthogonal_basis_vectors():
    left = _e1()
    right = np.array([0, 1], dtype=np.complex128)
    assert internal_witness(left, right, p=3, mu=0.05) is None


def test_threshold_includes_the_endpoint_and_rejects_a_clear_overshoot():
    threshold = math.sqrt(0.05)
    assert within_upper(threshold, threshold)
    assert not within_upper(threshold * (1 + 1e-6), threshold)


def test_cross_edge_inside_the_arc_and_outside_the_stripes():
    # ⟨w, z⟩ = exp(i π/6), so the argument is π/6 ∈ [0, 2π/3].
    angle = math.pi / 6
    left = _e1()
    right = np.array([cmath_exp(-1j * angle), 0], dtype=np.complex128)
    witness = cross_witness(left, right, p=3, ell=1, mu=0.05, k_stripe=2)
    assert witness is not None
    assert witness["argument"] == pytest.approx(angle)
    assert witness["min_abs_im"] == pytest.approx(0.5, abs=1e-9)


def test_cross_non_edge_when_the_argument_is_past_the_arc():
    left = _e1()
    right = np.array([-1, 0], dtype=np.complex128)
    assert cross_witness(left, right, p=3, ell=1, mu=0.05, k_stripe=2) is None


def test_argument_arc_endpoints():
    upper = 2 * math.pi / 3
    assert argument_in_arc(1 + 0j, p=3, ell=1)
    assert argument_in_arc(cmath_exp(1j * upper), p=3, ell=1)
    assert not argument_in_arc(cmath_exp(1j * (upper + 1e-4)), p=3, ell=1)
    assert not argument_in_arc(cmath_exp(-1j * 0.01), p=3, ell=1)


def test_ell_at_least_p_is_rejected():
    with pytest.raises(ValueError):
        build_graph([_e1()], [_e1()], p=3, ell=3, mu=0.05, k_stripe=2)


def test_rotation_difference_on_three_explicit_points():
    rho = _rho()
    wt = _e1()
    wi = np.array([rho, 0], dtype=np.complex128)
    wj = np.array([rho**2, 0], dtype=np.complex128)
    witness_i = internal_witness(wi, wt, p=3, mu=0.05)
    witness_j = internal_witness(wj, wt, p=3, mu=0.05)
    witness_ij = internal_witness(wi, wj, p=3, mu=0.05)
    assert witness_i is not None and witness_j is not None and witness_ij is not None
    assert rotation_index_matches(witness_i["h"], witness_j["h"], witness_ij["h"], p=3)
    assert passes_elementary_gap(3, 1)
    assert one_minus_root_modulus(3, 1) >= 4 / 3


def test_seeded_sample_is_stable_and_has_a_fixed_edge_set():
    part_w = sample_complex_sphere(4, 2, seed=0)
    part_z = sample_complex_sphere(4, 2, seed=1)
    again = sample_complex_sphere(4, 2, seed=0)
    assert np.allclose(part_w[0], again[0])
    graph = build_graph(part_w, part_z, p=3, ell=1, mu=0.05, k_stripe=2)
    pairs = sorted((edge["source"], edge["target"], edge["kind"]) for edge in graph["edges"])
    assert pairs == GOLDEN_PAIRS
    stats = analyse(graph, p=3)
    assert stats["vertex_count"] == 8
    assert stats["edge_count"] == len(GOLDEN_PAIRS)


GOLDEN_PAIRS: list[tuple[str, str, str]] = [
    ("w0", "z0", "cross"),
    ("w1", "z0", "cross"),
    ("w2", "z3", "cross"),
    ("w3", "z3", "cross"),
]


def test_vectorized_b2_matches_the_scalar_witness():
    part_w = sample_complex_sphere(5, 3, seed=4)
    part_z = sample_complex_sphere(5, 3, seed=9)
    inners = hermitian_matrix(stack_points(part_w), stack_points(part_z))
    stripe, arc, _minimum = stripe_and_arc(inners, p=3, ell=1, mu=0.05, k_stripe=2)
    for i, left in enumerate(part_w):
        for j, right in enumerate(part_z):
            witness = cross_witness(left, right, p=3, ell=1, mu=0.05, k_stripe=2)
            assert bool(stripe[i, j] and arc[i, j]) is (witness is not None)


def test_rhombus_search_reports_absence_on_two_points():
    assert find_rhombus([np.array([1.0, 0.0]), np.array([-1.0, 0.0])], mu=0.1) is None


def cmath_exp(value: complex) -> complex:
    import cmath

    return cmath.exp(value)
